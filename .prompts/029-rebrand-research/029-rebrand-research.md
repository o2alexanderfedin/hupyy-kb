<objective>
Research and catalog all occurrences of "PipesHub" branding throughout the codebase to prepare for a comprehensive rebrand to "Hupyy KB".

This research will inform a systematic, history-preserving rebrand that updates the application name, tagline, colors, logos, and all brand elements while maintaining git commit history for traceability.
</objective>

<context>
The application is currently branded as "PipesHub" and needs to be rebranded to "Hupyy KB" with a complete brand identity update. This is a full-stack application with:
- Frontend (React/TypeScript)
- Backend (Node.js and Python)
- Docker deployment configurations
- Documentation and README files
- Database schemas and configurations
- Test files and CI/CD workflows

The rebrand must preserve git history with clear, traceable commits rather than a single mass find-replace operation.

Read the project structure to understand the codebase organization:
@CLAUDE.md
@package.json
@README.md
</context>

<research_objectives>
Thoroughly catalog all locations where "PipesHub" branding appears:

1. **Code References**:
   - Application names in package.json, setup.py, etc.
   - Import statements and module names
   - Class names, function names, variable names
   - Comments referencing the application
   - Configuration files

2. **User-Facing Text**:
   - UI component text and labels
   - Page titles and meta tags
   - Error messages and notifications
   - Documentation strings

3. **Documentation**:
   - README files
   - Documentation markdown files
   - API documentation
   - Code comments

4. **Assets and Resources**:
   - Image files (logos, icons, favicons)
   - CSS/styling references
   - Environment variable names
   - Docker container names

5. **Database and Configuration**:
   - Database names
   - Collection/table names
   - Environment variables
   - Docker compose service names
   - Volume names

6. **Build and Deployment**:
   - Docker image names
   - CI/CD workflow names
   - Artifact names
   - URLs and endpoints
</research_objectives>

<search_strategy>
Use systematic searches to find all occurrences:

1. Case-sensitive search for exact matches: "PipesHub", "pipeshub", "PIPESHUB"
2. Search for variations: "pipes-hub", "pipes_hub", "pipesHub"
3. Check file and directory names containing "pipes" or "hub"
4. Review package names, import paths, and namespaces
5. Examine asset files (SVG, PNG, ICO) that might contain embedded text or need replacement

For each occurrence found, document:
- File path and line number
- Context (what it's used for)
- Type (code, UI, docs, config, asset)
- Replacement strategy (simple find-replace, refactor, regenerate asset, etc.)
</search_strategy>

<deliverables>
Create a comprehensive research report saved to: `./.prompts/029-rebrand-research/REBRAND-CATALOG.md`

The report should include:

1. **Executive Summary**: Total occurrences by category
2. **Detailed Catalog**: Grouped by file type/location
3. **Asset Inventory**: List of logos, icons, and graphics needing replacement
4. **Risk Assessment**: Potential breaking changes or special considerations
5. **Recommended Approach**: Suggested order of operations for the rebrand

Format each entry as:
```
### [Category Name]

**File**: `path/to/file.ext:line_number`
**Current**: "PipesHub AI Platform"
**New**: "Hupyy KB"
**Type**: [code|ui|docs|config|asset]
**Strategy**: [simple-replace|refactor|regenerate|manual]
**Notes**: Any special considerations
```
</deliverables>

<verification>
Before completing, verify:
- All major file types searched (py, ts, tsx, js, jsx, json, yml, yaml, md, env, docker, css, svg)
- Both exact and case-insensitive searches performed
- File and directory names checked
- Asset files inventoried
- Edge cases identified (embedded in images, compiled assets, etc.)
- Total count of occurrences matches sum of categorized entries
</verification>

<success_criteria>
- Comprehensive catalog created with all PipesHub references
- Clear categorization by type and replacement strategy
- Specific recommendations for execution order
- Risk assessment completed
- Ready to proceed to planning phase with complete information
</success_criteria>
