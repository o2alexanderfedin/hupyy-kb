<objective>
Create a detailed, phase-based implementation plan for rebranding PipesHub to Hupyy KB with complete brand identity update.

This plan will define the exact sequence of changes, git commit strategy, and verification steps to ensure a smooth transition while preserving git history and maintaining application functionality throughout the process.
</objective>

<context>
Based on the research catalog from prompt 029, create a systematic plan that:
- Updates all code references, UI text, documentation, configs, database elements, and assets
- Preserves git history with meaningful commits grouped by functional area
- Minimizes risk by executing changes in dependency order
- Includes new brand identity elements (name, tagline, colors, logos)
- Ensures no breaking changes to functionality

Review the research findings:
@.prompts/029-rebrand-research/REBRAND-CATALOG.md
@CLAUDE.md
</context>

<planning_requirements>
Create a phased implementation plan with the following structure:

### Phase 1: Brand Identity Definition
Define the complete new brand identity:
- Official name: "Hupyy KB"
- Full name variations: "Hupyy Knowledge Base", "Hupyy KB Platform", etc.
- Tagline and description
- Color scheme (primary, secondary, accent colors with hex codes)
- Typography guidelines
- Logo specifications and requirements

### Phase 2: Asset Preparation
Before touching code, prepare all new assets:
- Logo files (SVG, PNG at various sizes)
- Favicon (ICO, PNG)
- Social media images (OpenGraph, Twitter cards)
- App icons if applicable
- Any custom graphics or illustrations

### Phase 3: Configuration & Environment
Update non-code configuration first (lowest risk):
- Environment variable names
- Docker compose service names (but NOT container image names yet to avoid breaking dependencies)
- Database names and connection strings
- API endpoint configurations
- .env.example files

### Phase 4: Documentation
Update all documentation (safe, non-breaking):
- README.md files at all levels
- Documentation markdown files
- API documentation
- Code comment blocks
- CLAUDE.md project guidelines

### Phase 5: Frontend UI Text
Update user-facing text in order of visibility:
- Page titles and meta tags
- Main navigation and headers
- Component labels and buttons
- Form labels and placeholders
- Error messages and notifications
- Loading states and feedback messages

### Phase 6: Backend Code References
Update backend code systematically:
- Module names and imports
- Class and function names (if they reference PipesHub)
- Variable names
- Configuration objects
- API route handlers
- Database query references

### Phase 7: Frontend Code References
Update frontend code systematically:
- Component names
- Module imports
- Type definitions
- State management references
- Utility functions
- Test files

### Phase 8: Build & Deployment
Update build and deployment configurations:
- Docker image names in compose files
- CI/CD workflow names and variables
- Build artifact names
- Deployment scripts
- GitHub Actions workflows

### Phase 9: Testing & Verification
Comprehensive testing after rebrand:
- Run all linters
- Run all test suites
- Build all Docker images
- Start all services
- Verify UI rendering
- Test critical user flows
- Check external integrations

### Phase 10: Final Cleanup
- Search for any remaining "PipesHub" references
- Update git remote URLs if applicable
- Create comprehensive release notes
- Tag the rebrand completion
</planning_requirements>

<git_commit_strategy>
For each phase, define clear commit messages following conventional commits:

**Example commits**:
```
docs(rebrand): update README and documentation for Hupyy KB

feat(rebrand): add new Hupyy KB brand assets and logos

refactor(rebrand): update frontend UI text to Hupyy KB

refactor(rebrand): rename backend modules and classes for Hupyy KB

chore(rebrand): update Docker and CI/CD configs for Hupyy KB
```

Each commit should:
- Be focused on a single phase or logical grouping
- Include clear description of what changed
- Pass linters and type checks before committing
- Not break application functionality
</git_commit_strategy>

<risk_mitigation>
Identify and document:

1. **Breaking Changes**: What might break and how to prevent it
2. **Database Migration**: Whether schema changes are needed
3. **API Compatibility**: If external systems depend on current naming
4. **Rollback Strategy**: How to revert if issues arise
5. **Testing Checkpoints**: When to verify functionality
</risk_mitigation>

<deliverables>
Create implementation plan saved to: `./.prompts/030-rebrand-plan/REBRAND-IMPLEMENTATION-PLAN.md`

Include:
1. **Phase-by-phase breakdown** with specific file lists
2. **Git commit strategy** with example messages
3. **Testing checklist** for each phase
4. **Risk assessment** and mitigation strategies
5. **Estimated effort** for each phase
6. **Dependencies** between phases
7. **Rollback procedures** if needed

Also create: `./.prompts/030-rebrand-plan/BRAND-IDENTITY.md`
Document the complete new brand identity specifications.
</deliverables>

<verification>
Before declaring plan complete:
- All phases address findings from research catalog
- Phases are in safe dependency order
- Each phase has clear success criteria
- Git commit strategy is well-defined
- Testing checkpoints are comprehensive
- Rollback strategy is documented
- No orphaned references will remain
</verification>

<success_criteria>
- Complete implementation plan created
- Brand identity fully specified
- Safe execution order defined
- Git history preservation strategy clear
- Risk mitigation documented
- Ready to proceed to implementation phase
</success_criteria>
