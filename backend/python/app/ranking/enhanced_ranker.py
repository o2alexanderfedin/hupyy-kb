"""
Enhanced ranker with verification scores.

Ranking formula (from architecture):
0.45 × semantic + 0.30 × pagerank + 0.15 × verification + 0.10 × historical

Features:
- Gradual weight transition (cold start)
- Failure mode multipliers
- Feature flag integration
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from app.config.feature_flags import FeatureFlagService


@dataclass
class SearchResult:
    """Search result with all ranking signals."""

    chunk_id: str
    semantic_similarity: float
    pagerank_score: float
    verification_confidence: float
    verification_verdict: Optional[str]
    failure_mode: Optional[str]
    historical_success: float
    final_score: float = 0.0


class FailureModeClassifier:
    """Maps failure modes to confidence multipliers."""

    MULTIPLIERS = {
        "verified_sat": 1.8,  # High confidence boost
        "invalid": 0.3,  # Strong penalty for contradictions
        "ambiguous": 0.7,  # Moderate penalty
        "incomplete": 0.8,  # Small penalty
        "timeout": 0.85,  # Very small penalty (not solver's fault)
        "theory_incomplete": 1.0,  # Neutral (undecidable)
        "never_verified": 1.0,  # Neutral
        "service_unavailable": 1.0,  # Neutral (external issue)
    }

    @classmethod
    def get_multiplier(
        cls, verdict: Optional[str], failure_mode: Optional[str]
    ) -> float:
        """
        Get score multiplier based on verdict and failure mode.

        Args:
            verdict: Verification verdict (SAT/UNSAT/UNKNOWN/ERROR)
            failure_mode: Specific failure mode

        Returns:
            Score multiplier (0.3 to 1.8)
        """
        # SAT verdict
        if verdict == "SAT":
            if failure_mode:
                return cls.MULTIPLIERS.get(failure_mode, 1.0)
            return cls.MULTIPLIERS["verified_sat"]

        # UNSAT verdict
        elif verdict == "UNSAT":
            return cls.MULTIPLIERS["invalid"]

        # UNKNOWN/ERROR verdict
        elif verdict in ["UNKNOWN", "ERROR"]:
            if failure_mode:
                return cls.MULTIPLIERS.get(failure_mode, 1.0)
            return cls.MULTIPLIERS["timeout"]

        # Never verified
        else:
            return cls.MULTIPLIERS["never_verified"]


class EnhancedRanker:
    """Enhanced ranker with verification scores."""

    def __init__(
        self,
        feature_flag_service: FeatureFlagService,
        cold_start_days: int = 7,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """
        Initialize enhanced ranker.

        Args:
            feature_flag_service: Feature flag service
            cold_start_days: Days for weight transition
            logger: Optional logger
        """
        self.feature_flag_service = feature_flag_service
        self.cold_start_days = cold_start_days
        self.logger = logger or logging.getLogger(__name__)

        # Store deployment timestamp for cold start
        self.deployment_time = datetime.utcnow()

    async def rank_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """
        Rank search results with verification scores.

        Args:
            results: List of search results

        Returns:
            Ranked list of results
        """
        # Get current verification weight
        verification_weight = await self._get_verification_weight()

        # Calculate final scores
        for result in results:
            # Base score (weighted sum)
            base_score = (
                0.45 * result.semantic_similarity
                + 0.30 * result.pagerank_score
                + verification_weight * result.verification_confidence
                + (0.25 - verification_weight)
                * result.historical_success  # Adjust historical weight
            )

            # Apply failure mode multiplier
            multiplier = FailureModeClassifier.get_multiplier(
                result.verification_verdict, result.failure_mode
            )

            result.final_score = base_score * multiplier

        # Sort by final score (descending)
        ranked_results = sorted(results, key=lambda r: r.final_score, reverse=True)

        self.logger.debug(
            f"📊 Ranked {len(results)} results (verification_weight: {verification_weight:.2f})"
        )

        return ranked_results

    async def _get_verification_weight(self) -> float:
        """
        Get current verification weight with cold start transition.

        Gradual transition:
        - Days 0-7: 0% → 15% (linear)
        - Days 7+: 15% (or feature flag override)

        Returns:
            Verification weight (0.0 to 0.15)
        """
        # Get feature flag weight
        flags = await self.feature_flag_service.get_verification_flags()
        target_weight = flags.verification_ranking_weight

        # Check if we're in cold start period
        days_since_deployment = (datetime.utcnow() - self.deployment_time).days

        if days_since_deployment < self.cold_start_days:
            # Linear transition
            progress = days_since_deployment / self.cold_start_days
            current_weight = progress * target_weight
            self.logger.debug(
                f"🥶 Cold start: Day {days_since_deployment}/{self.cold_start_days}, "
                f"weight: {current_weight:.3f} (target: {target_weight:.3f})"
            )
            return current_weight
        else:
            return target_weight

    def calculate_verification_score(
        self,
        verdict: str,
        confidence: float,
        formalization_similarity: float,
        failure_mode: Optional[str] = None,
    ) -> float:
        """
        Calculate verification score with failure mode handling.

        Formula (from architecture):
        - SAT: confidence × formalization_similarity × failure_mode_multiplier
        - UNSAT: 0.5 × confidence (penalty for contradiction)
        - UNKNOWN/ERROR: 0.0 (neutral, fallback to other signals)

        Args:
            verdict: Verification verdict
            confidence: Confidence score
            formalization_similarity: Formalization similarity
            failure_mode: Optional failure mode

        Returns:
            Verification score (0.0 to 1.0)
        """
        if verdict == "SAT":
            base_score = confidence * (formalization_similarity or 1.0)
            multiplier = FailureModeClassifier.get_multiplier(verdict, failure_mode)
            # Normalize to 0-1 range (multiplier can go up to 1.8)
            return min(base_score * (multiplier / 1.8), 1.0)

        elif verdict == "UNSAT":
            return 0.5 * confidence  # Penalty

        else:  # UNKNOWN/ERROR
            return 0.0  # Neutral
