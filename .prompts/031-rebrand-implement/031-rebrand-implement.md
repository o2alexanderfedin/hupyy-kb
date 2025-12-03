<objective>
Execute the comprehensive rebrand from PipesHub to Hupyy KB following the phased implementation plan, preserving git history with clear commits for each phase.

Transform the entire application brand identity while maintaining full functionality, passing all tests, and creating a traceable commit history for the rebrand process.
</objective>

<context>
Execute the rebrand based on the detailed plan created in prompt 030. This is the implementation phase where all changes are made systematically.

Review the implementation plan and brand identity:
@.prompts/030-rebrand-plan/REBRAND-IMPLEMENTATION-PLAN.md
@.prompts/030-rebrand-plan/BRAND-IDENTITY.md
@.prompts/029-rebrand-research/REBRAND-CATALOG.md
@CLAUDE.md

The rebrand must:
- Follow the phase-by-phase plan exactly
- Create git commits after each phase
- Run linters before each commit
- Verify functionality at testing checkpoints
- Preserve all existing functionality
</context>

<implementation_process>
Execute each phase from the plan in sequence:

### Phase Execution Protocol

For EACH phase:

1. **Pre-Phase Checklist**:
   - Review phase objectives from implementation plan
   - Identify all files to be modified in this phase
   - Understand dependencies and risks
   - Prepare rollback strategy

2. **Execute Changes**:
   - Make all changes specified for the phase
   - Follow replacement strategies from the catalog
   - Maintain code quality and style consistency
   - Update imports, references, and dependencies
   - Ensure type safety is preserved

3. **Verification**:
   - Run applicable linters: `npm run lint`, `pylint`, `mypy`, etc.
   - Run applicable type checkers: `tsc --noEmit`
   - Fix all linting and type errors
   - For critical phases, run relevant test suites
   - Verify no broken imports or references

4. **Git Commit**:
   - Stage only files modified in this phase: `git add [specific files]`
   - Create focused commit with conventional commit message
   - Format: `<type>(rebrand): <description>`
   - Include details of what changed in commit body
   - Example:
     ```
     feat(rebrand): add Hupyy KB brand assets and styling

     - Created new logo SVG with Hupyy KB branding
     - Added favicon with updated brand colors
     - Updated primary color scheme to new brand palette
     - Generated OpenGraph and social media images
     ```

5. **Post-Commit Verification**:
   - Verify commit was created successfully
   - Check git log to confirm clear history
   - Ensure working directory is clean for next phase

### Special Considerations

**For Asset Replacement**:
- Create new SVG logos with proper dimensions and styling
- Generate favicon in multiple sizes (16x16, 32x32, 192x192)
- Ensure all images have proper accessibility attributes
- Optimize file sizes for web delivery

**For Code Refactoring**:
- Use case-sensitive find/replace for exact matches
- Update all import statements that reference renamed modules
- Maintain TypeScript type safety throughout
- Fix any circular dependencies that arise

**For Configuration Updates**:
- Update environment variable references in code when .env changes
- Verify Docker services can still communicate after name changes
- Test database connections with new configuration
- Update API endpoint URLs if they contain brand name

**For Documentation**:
- Update all README badges and links
- Fix relative links that break due to renames
- Update screenshots if they show old branding
- Ensure code examples reflect new naming

</implementation_process>

<testing_checkpoints>
After specific phases, run comprehensive verification:

**After Phase 3 (Configuration)**:
```bash
docker compose -f deployment/docker-compose/docker-compose.dev.yml config
```
Verify configuration is valid.

**After Phase 5 (Frontend UI)**:
```bash
cd frontend && npm run lint && npm run type-check
```
Verify no TypeScript or linting errors.

**After Phase 6 (Backend Code)**:
```bash
cd backend/nodejs && npm run lint && npm run type-check
cd ../python && pylint app/ && mypy app/
```
Verify backend code quality.

**After Phase 8 (Build & Deployment)**:
```bash
docker compose -f deployment/docker-compose/docker-compose.dev.yml build
```
Verify all images build successfully.

**After Phase 9 (Testing)**:
```bash
# Run all test suites
npm test
pytest
npx playwright test
```
Verify all tests pass with new branding.

**Final Verification**:
```bash
# Start all services
docker compose -f deployment/docker-compose/docker-compose.dev.yml up -d

# Check service health
docker compose -f deployment/docker-compose/docker-compose.dev.yml ps

# Access application at http://localhost:3000
# Verify UI displays Hupyy KB branding correctly
```
</testing_checkpoints>

<rollback_strategy>
If any phase fails critically:

1. **Identify the issue**:
   - Check linter output
   - Review type checker errors
   - Examine test failures
   - Inspect service logs

2. **Attempt fix**:
   - Fix linting/type errors in current phase
   - Do NOT proceed to next phase until current phase is clean

3. **If fix is not immediately obvious**:
   - Revert current phase changes: `git reset --hard HEAD~1`
   - Review implementation plan for phase
   - Identify what went wrong
   - Adjust approach and retry phase

4. **Document issues**:
   - Create `.prompts/031-rebrand-implement/ISSUES.md` if problems arise
   - Document unexpected complications
   - Note solutions for future reference
</rollback_strategy>

<deliverables>
Upon completion, create:

1. **`.prompts/031-rebrand-implement/EXECUTION-SUMMARY.md`**:
   - List all commits created
   - Document any issues encountered and resolved
   - Confirm all phases completed successfully
   - List verification steps performed

2. **`.prompts/031-rebrand-implement/FINAL-VERIFICATION.md`**:
   - Screenshots of rebranded UI
   - Test results from all test suites
   - Linter output showing clean state
   - Service health checks showing all services running

3. **Git History**:
   - Clear, focused commits for each phase
   - Meaningful commit messages
   - Traceable rebrand process in git log

</deliverables>

<final_verification>
Before declaring the rebrand complete, verify:

1. **No remaining "PipesHub" references**:
   ```bash
   # Search for any missed occurrences
   grep -r "PipesHub" --exclude-dir=node_modules --exclude-dir=.git
   grep -r "pipeshub" --exclude-dir=node_modules --exclude-dir=.git
   grep -r "pipes-hub" --exclude-dir=node_modules --exclude-dir=.git
   ```
   Should return zero results.

2. **All linters pass**:
   - TypeScript: No type errors
   - ESLint: No linting errors
   - Pylint: No linting errors
   - Mypy: No type errors

3. **All tests pass**:
   - Unit tests: All passing
   - Integration tests: All passing
   - E2E tests: All passing

4. **Application runs successfully**:
   - All Docker services healthy
   - Frontend loads at http://localhost:3000
   - UI displays "Hupyy KB" branding
   - All features functional

5. **Git history is clean**:
   - Each phase has dedicated commit
   - Commit messages follow conventional commits
   - No merge conflicts or orphaned commits

</final_verification>

<success_criteria>
- All 10 phases from implementation plan executed successfully
- Git commits created for each phase with clear messages
- All linters pass with zero errors
- All tests pass
- Application runs with complete Hupyy KB branding
- No "PipesHub" references remain in codebase
- Documentation reflects new brand identity
- Docker services run with updated names and configuration
- Execution summary and verification reports created
- Ready for git release with rebrand completion
</success_criteria>

<meta_note>
This is a large-scale refactoring task. Use TodoWrite tool extensively to track progress through the 10 phases. Mark each phase as completed only after its git commit is successfully created and verified.

Expected execution time: 2-4 hours depending on codebase size.
Expected commits: 10-15 commits (one per phase, potentially split for large phases)
</meta_note>
