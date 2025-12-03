# PipesHub to Hupyy KB Rebrand - Comprehensive Catalog

## Executive Summary

This document catalogs all occurrences of "PipesHub" branding throughout the codebase to support a systematic, history-preserving rebrand to "Hupyy KB".

### Total Occurrences by Category

| Category | Count | Status |
|----------|-------|--------|
| **Documentation Files** | 5 files | High Priority |
| **Frontend HTML/UI** | 2 files | High Priority |
| **Docker & Deployment** | 2 files | High Priority |
| **Package Configuration** | 3 files | Medium Priority |
| **Logo & Brand Assets** | 7+ files | Requires Regeneration |
| **GitHub/External URLs** | Multiple | Reference Only |
| **Directory Names** | 1 | Rename Required |
| **Test Configuration** | 2 files | Medium Priority |

**Total Estimated References**: 150+ occurrences across documentation, code, config, and assets

---

## Detailed Catalog

### 1. Documentation Files

#### README.md
**File**: `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig/README.md`

**Occurrences**: 60+ references

**Context**: Main project README with comprehensive PipesHub branding
- Line 4: GitHub repo URL reference
- Line 5: Logo SVG reference
- Line 8: "Workplace AI Platform" tagline
- Line 13: Trendshift badge reference
- Line 24: docs.pipeshub.com URL
- Line 29-31: Discord link
- Line 36-75: Multiple GitHub stars/badges with pipeshub-ai organization
- Line 79: "[PipesHub](https://www.pipeshub.com/)" product description
- Line 80: "PipesHub AI helps you..." product description
- Line 88: Architecture diagram reference
- Line 98: YouTube video reference
- Line 104: "Unmatched Value of PipesHub" section header
- Line 118-145: Connector logo references
- Line 205: "git clone https://github.com/pipeshub-ai/pipeshub-ai.git"
- Line 208: "cd pipeshub-ai/deployment/docker-compose"
- Line 216: "docker compose -f docker-compose.prod.yml -p pipeshub-ai up -d"
- Line 219: "docker compose -f docker-compose.prod.yml -p pipeshub-ai down"
- Line 226: "git clone https://github.com/pipeshub-ai/pipeshub-ai.git"
- Line 237: "docker compose -f docker-compose.dev.yml -p pipeshub-ai up --build -d"
- Line 245: "Contributing Guide" URL with pipeshub-ai
- Line 252: GIF reference

**Type**: Documentation
**Strategy**: Manual replacement with careful preservation of structure
**Priority**: HIGH

---

#### CLAUDE.md
**File**: `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig/CLAUDE.md`

**Occurrences**: 3 references

**Context**: Claude Code project guidelines
- Line 1: "# Claude Code Guidelines for PipesHub AI Project"
- Line 103: "## PipesHub Configuration" section header
- Line 106: Docker volume mount path comment

**Type**: Documentation
**Strategy**: Simple replacement
**Priority**: HIGH
**Notes**: Update project name and configuration section header

---

#### CONTRIBUTING.md
**File**: `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig/CONTRIBUTING.md`

**Occurrences**: 1 reference

**Context**: Contributing guidelines
- Line 1: "# Contributing to PipesHub Workplace AI"

**Type**: Documentation
**Strategy**: Simple replacement
**Priority**: HIGH

---

#### CODE_OF_CONDUCT.md
**File**: `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig/CODE_OF_CONDUCT.md`

**Occurrences**: 1 reference

**Context**: Community code of conduct
- Line 63: "contact@pipeshub.com" email address

**Type**: Documentation
**Strategy**: Update contact email
**Priority**: MEDIUM
**Notes**: Will need new contact email for Hupyy KB

---

#### CONNECTOR_INTEGRATION_PLAYBOOK.md
**File**: `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig/CONNECTOR_INTEGRATION_PLAYBOOK.md`

**Occurrences**: 50+ references

**Context**: Technical documentation with GitHub URLs and code references
- Line 191, 283-288, 302-309, 315-316, 322, 332: Multiple GitHub URL references to pipeshub-ai organization
- Various code examples and file path references

**Type**: Documentation
**Strategy**: Update GitHub organization references (if repo moves) or mark as legacy references
**Priority**: MEDIUM
**Notes**: Consider if this is external documentation that references the old brand for historical accuracy

---

### 2. Frontend UI & HTML

#### index.html
**File**: `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig/frontend/index.html`

**Occurrences**: 1 reference

**Context**: Main HTML entry point for the application
- Line 8: `<title>PipesHub: The Open Source Alternative To Glean</title>`

**Type**: UI - Page Title
**Strategy**: Simple replacement
**Priority**: HIGH
**New Value**: "Hupyy KB: The Open Source Alternative To Glean" or "Hupyy KB - Your Workplace AI Platform"

---

#### frontend/package.json
**File**: `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig/frontend/package.json`

**Occurrences**: 1 reference

**Context**: Frontend package metadata
- Line 3: `"author": "PipesHub"`

**Type**: Configuration - Package Metadata
**Strategy**: Simple replacement
**Priority**: MEDIUM
**New Value**: "Hupyy" or "Hupyy Team"

---

### 3. Docker & Deployment Configuration

#### docker-compose.dev.yml
**File**: `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig/deployment/docker-compose/docker-compose.dev.yml`

**Occurrences**: 6 references

**Context**: Development Docker Compose configuration
- Line 2: Service name `pipeshub-ai:`
- Line 3: Image name `image: pipeshub-ai:latest`
- Line 101: Volume `pipeshub_data:/data/pipeshub`
- Line 102: Volume `pipeshub_root_local:/root/.local`
- Line 103: Host path `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig:/data/local-files:ro`
- Line 251: Volume definition `pipeshub_data:`
- Line 253: Volume definition `pipeshub_root_local:`

**Type**: Configuration - Docker
**Strategy**: Systematic replacement of service names, image names, and volume names
**Priority**: HIGH
**Notes**:
- Service name: pipeshub-ai → hupyy-kb
- Image name: pipeshub-ai → hupyy-kb
- Volumes: pipeshub_data → hupyy_data, pipeshub_root_local → hupyy_root_local
- Host path will change based on new directory name

---

#### docker-compose.prod.yml
**File**: `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig/deployment/docker-compose/docker-compose.prod.yml`

**Occurrences**: 6 references

**Context**: Production Docker Compose configuration
- Line 2: Service name `pipeshub-ai:`
- Line 3: Image name `image: pipeshubai/pipeshub-ai:${IMAGE_TAG:-latest}`
- Line 4: Container name `container_name: pipeshub-ai`
- Line 81: Volume `pipeshub_data:/data/pipeshub`
- Line 82: Volume `pipeshub_root_local:/root/.local`
- Line 85: Host path `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig:/data/local-files:ro`
- Line 257: Volume definition `pipeshub_data:`
- Line 259: Volume definition `pipeshub_root_local:`

**Type**: Configuration - Docker
**Strategy**: Systematic replacement including DockerHub organization
**Priority**: HIGH
**Notes**:
- DockerHub org: pipeshubai → hupyy (or hupyykb)
- Image: pipeshubai/pipeshub-ai → hupyy/hupyy-kb
- All other naming follows dev pattern

---

#### .env
**File**: `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig/deployment/docker-compose/.env`

**Occurrences**: 1 reference

**Context**: Environment configuration file
- Line 2: `# PipesHub Local Deployment Configuration`

**Type**: Configuration - Environment
**Strategy**: Simple comment replacement
**Priority**: LOW

---

### 4. Package Configuration

#### Root package.json
**File**: `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig/package.json`

**Occurrences**: 1 reference

**Context**: Root package configuration
- Line 1: `"name":"pipeshub-config"`

**Type**: Configuration - Package
**Strategy**: Simple replacement
**Priority**: MEDIUM
**New Value**: "hupyy-config"

---

#### Root package-lock.json
**File**: `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig/package-lock.json`

**Occurrences**: 2 references

**Context**: NPM lock file (auto-generated)
- Line 2: `"name": "pipeshub-config"`
- Line 8: Package name in packages section

**Type**: Configuration - Auto-generated
**Strategy**: Regenerate after package.json update
**Priority**: LOW
**Notes**: Will be automatically updated when package.json changes and npm install runs

---

### 5. Test Configuration

#### playwright.config.ts
**File**: `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig/playwright.config.ts`

**Occurrences**: 0 direct references (filename only: pipeshub-ai-orig in path)

**Type**: Configuration - Testing
**Strategy**: Update if project name is referenced in test configuration
**Priority**: LOW

---

#### test-results/e2e-results.json
**File**: `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig/test-results/e2e-results.json`

**Occurrences**: 10+ references

**Context**: Generated test results file
- Line 3-4: Config file paths with pipeshub-ai-orig
- Line 14: `"project": "PipesHub AI"`
- Line 15: `"description": "End-to-end tests for PipesHub AI verification feature"`
- Line 52-82: Multiple test result entries with paths

**Type**: Test Results - Auto-generated
**Strategy**: Regenerate after rebrand by running tests
**Priority**: LOW
**Notes**: This file is auto-generated and will update automatically

---

### 6. Logo & Brand Assets

#### Primary Logos

**File**: `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig/frontend/public/logo/logo-blue.svg`
**Type**: Logo Asset - SVG
**Strategy**: Regenerate with new Hupyy KB branding
**Priority**: CRITICAL
**Size**: 38,527 bytes
**Notes**: Primary brand logo, likely contains "PipesHub" text

---

**File**: `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig/frontend/public/logo/logo-full.svg`
**Type**: Logo Asset - SVG
**Strategy**: Regenerate with new Hupyy KB branding
**Priority**: CRITICAL
**Size**: 38,527 bytes
**Notes**: Full brand logo with text

---

**File**: `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig/frontend/public/logo/logo-single.jpg`
**Type**: Logo Asset - JPEG
**Strategy**: Regenerate with new Hupyy KB branding
**Priority**: CRITICAL
**Size**: 31,881 bytes
**Notes**: Logo icon/mark only

---

#### Marketing Assets

**File**: `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig/frontend/public/logo/signinpage.png`
**Type**: Marketing Asset - Sign-in Page Background
**Strategy**: Review and potentially regenerate
**Priority**: HIGH
**Size**: 997,988 bytes
**Notes**: Large sign-in page asset, may contain branding

---

**File**: `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig/frontend/public/logo/welcomegif.gif`
**Type**: Marketing Asset - Welcome Animation
**Strategy**: Review and potentially regenerate
**Priority**: HIGH
**Size**: 262,359 bytes
**Notes**: Animated welcome graphic, may contain branding

---

#### Favicon

**File**: `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig/frontend/public/favicon.ico`
**Type**: Browser Icon
**Strategy**: Regenerate with new Hupyy KB icon
**Priority**: HIGH
**Size**: 15,406 bytes

---

**File**: `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig/frontend/dist/favicon.ico`
**Type**: Browser Icon - Distribution Build
**Strategy**: Regenerate with new Hupyy KB icon
**Priority**: HIGH
**Notes**: Build artifact, will be regenerated from source

---

#### Distribution Build Assets

**File**: `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig/frontend/dist/logo/logo-blue.svg`
**File**: `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig/frontend/dist/logo/logo-full.svg`
**File**: `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig/frontend/dist/logo/logo-single.jpg`
**File**: `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig/frontend/dist/logo/signinpage.png`

**Type**: Build Artifacts
**Strategy**: Auto-regenerate during build after source assets are updated
**Priority**: LOW (automated)
**Notes**: These are compiled/copied from /frontend/public during build process

---

### 7. Directory Names

#### Root Project Directory
**Current**: `/Users/alexanderfedin/Projects/hapyy/pipeshub-ai-orig`
**New**: `/Users/alexanderfedin/Projects/hapyy/hupyy-kb`

**Type**: Directory Structure
**Strategy**: Rename after all file changes are committed
**Priority**: DEFERRED (do last)
**Notes**:
- This should be the LAST change to preserve git history
- All absolute paths in configs will need updating
- Update CLAUDE.md with new path
- Update docker-compose volume mounts

---

### 8. External References (Non-Modifiable)

These references are to external resources and cannot be directly modified but should be noted:

#### GitHub Organization & Repositories
- github.com/pipeshub-ai/pipeshub-ai (main repository)
- github.com/pipeshub-ai/documentation
- github.com/pipeshub-ai/media-assets

**Strategy**: If migrating to new organization, update all URL references
**Notes**: Consider redirects or maintaining legacy organization for historical continuity

---

#### External URLs
- https://www.pipeshub.com (main website)
- https://docs.pipeshub.com (documentation)
- https://x.com/PipesHub (Twitter/X)
- https://www.linkedin.com/company/pipeshub/
- https://discord.com/invite/K5RskzJBm2
- https://trendshift.io/repositories/14618

**Strategy**: Reference only - external services
**Notes**: Will need to set up equivalent domains for Hupyy KB

---

#### Docker Hub
- pipeshubai/pipeshub-ai (Docker Hub organization and image)

**Strategy**: Create new hupyy/hupyy-kb repository
**Notes**: May want to maintain pipeshubai org with deprecation notice

---

#### Email
- contact@pipeshub.com

**Strategy**: Set up contact@hupyy.com or contact@hupyykb.com
**Notes**: Consider email forwarding from old address

---

## Asset Inventory Summary

### Assets Requiring Regeneration

| Asset Type | Count | Priority | Notes |
|------------|-------|----------|-------|
| SVG Logos | 2 | CRITICAL | logo-blue.svg, logo-full.svg |
| Logo Images | 1 | CRITICAL | logo-single.jpg |
| Favicons | 2 | HIGH | favicon.ico (source + dist) |
| Marketing Graphics | 2 | HIGH | signinpage.png, welcomegif.gif |
| **Total** | **7** | | Excludes build artifacts |

### Assets Not Requiring Changes

| Asset Type | Count | Notes |
|------------|-------|-------|
| Connector Icons | 29+ | Third-party service icons (Gmail, Slack, etc.) |
| UI Icons | 20+ | Generic UI icons (navbar, notifications, etc.) |
| AI Model Icons | 17+ | Provider icons (OpenAI, Claude, etc.) |
| **Total** | **66+** | These are vendor/service specific |

---

## Risk Assessment

### High Risk Changes

1. **Docker Image Names**: Breaking change for deployed instances
   - **Risk**: Production deployments may fail
   - **Mitigation**: Maintain both image names during transition period
   - **Recommendation**: Tag releases and provide migration guide

2. **Volume Names**: Data persistence risk
   - **Risk**: Existing Docker volumes won't be found
   - **Mitigation**: Document volume migration process or use symbolic names
   - **Recommendation**: Provide docker volume migration script

3. **Logo/Asset Changes**: Brand recognition
   - **Risk**: Users may not recognize rebranded application
   - **Mitigation**: Gradual rollout with notices
   - **Recommendation**: Keep visual similarity where appropriate

### Medium Risk Changes

1. **Package Names**: NPM package conflicts
   - **Risk**: Package name already taken in registries
   - **Mitigation**: Check availability first
   - **Recommendation**: Reserve names before migration

2. **GitHub URLs**: Link rot
   - **Risk**: Existing links will break if repo moves
   - **Mitigation**: GitHub redirects if transferring repo
   - **Recommendation**: Use GitHub's transfer feature vs. creating new repo

### Low Risk Changes

1. **Documentation Text**: Easy to update
   - **Risk**: Minimal
   - **Mitigation**: Standard find-replace with review
   - **Recommendation**: Systematic replacement with git tracking

2. **Comments & Metadata**: Non-functional
   - **Risk**: None
   - **Mitigation**: None needed
   - **Recommendation**: Update for consistency

---

## Recommended Execution Order

### Phase 1: Preparation (Non-Destructive)
1. Create new brand assets (logos, favicons, graphics)
2. Reserve new package names (NPM, Docker Hub, GitHub org)
3. Set up new domains and email
4. Prepare migration documentation

### Phase 2: Documentation Updates
1. Update README.md
2. Update CONTRIBUTING.md
3. Update CODE_OF_CONDUCT.md
4. Update CLAUDE.md
5. Update CONNECTOR_INTEGRATION_PLAYBOOK.md (mark as historical if needed)
6. Commit: "docs: rebrand documentation from PipesHub to Hupyy KB"

### Phase 3: Configuration Files
1. Update frontend/index.html (page title)
2. Update package.json files (root and frontend)
3. Update docker-compose files (service names, image names, volumes)
4. Update .env comment
5. Update frontend/package.json author
6. Commit: "config: rebrand configuration from PipesHub to Hupyy KB"

### Phase 4: Asset Replacement
1. Replace logo files in /frontend/public/logo/
2. Replace favicon.ico
3. Replace marketing graphics (signinpage.png, welcomegif.gif)
4. Rebuild frontend to update dist/ artifacts
5. Commit: "assets: replace PipesHub brand assets with Hupyy KB branding"

### Phase 5: Testing & Validation
1. Run frontend build
2. Run backend builds
3. Test Docker compose with new names
4. Run Playwright e2e tests
5. Verify all assets load correctly
6. Commit: "test: validate Hupyy KB rebrand"

### Phase 6: Directory Rename (Final)
1. Commit all changes with PipesHub directory name
2. Push to remote
3. Rename local directory: pipeshub-ai-orig → hupyy-kb
4. Update any remaining absolute path references
5. Update CLAUDE.md with new paths
6. Commit: "chore: rename project directory to hupyy-kb"

### Phase 7: External Updates (Out of Scope)
1. GitHub repository transfer/rename
2. Docker Hub image publishing
3. Domain DNS updates
4. Social media profile updates
5. Documentation site deployment

---

## Special Considerations

### Git History Preservation
All changes should be committed in logical groups with clear commit messages following the pattern:
- `docs: rebrand [files] from PipesHub to Hupyy KB`
- `config: rebrand [component] from PipesHub to Hupyy KB`
- `assets: replace [asset type] with Hupyy KB branding`

This maintains full traceability of the rebrand.

### Docker Volume Migration
Existing deployments will have data in `pipeshub_data` and `pipeshub_root_local` volumes. Options:
1. **Create volume aliases**: Use docker volume inspection and manual mounting
2. **Migration script**: Copy data from old volumes to new volumes
3. **Symlinks**: Create volume symlinks (platform-dependent)

Recommended: Provide migration script in documentation.

### Backward Compatibility
Consider maintaining a `legacy` branch with the PipesHub naming for users who need time to migrate.

### Brand Guidelines Document
Create a new `BRAND_GUIDELINES.md` documenting:
- New logo usage
- Color palette
- Typography
- Naming conventions (Hupyy KB vs Hupyy-KB vs hupyy-kb)

---

## Verification Checklist

After completing the rebrand, verify:

- [ ] All documentation files updated
- [ ] No remaining "pipeshub" references in source code (except historical)
- [ ] All logos and assets replaced
- [ ] Docker images build successfully with new names
- [ ] Frontend builds without errors
- [ ] Backend services start correctly
- [ ] Tests pass with new configuration
- [ ] Docker compose works with new volume names
- [ ] Page title displays "Hupyy KB"
- [ ] Favicon shows new icon
- [ ] All build artifacts regenerated
- [ ] Git history preserved with clear commit messages
- [ ] Migration documentation complete
- [ ] New domains configured (if applicable)
- [ ] New email addresses set up (if applicable)

---

## Summary Statistics

### Files Requiring Manual Updates: 12
- README.md
- CLAUDE.md
- CONTRIBUTING.md
- CODE_OF_CONDUCT.md
- CONNECTOR_INTEGRATION_PLAYBOOK.md
- frontend/index.html
- frontend/package.json
- package.json
- docker-compose.dev.yml
- docker-compose.prod.yml
- deployment/docker-compose/.env

### Assets Requiring Regeneration: 7
- logo-blue.svg
- logo-full.svg
- logo-single.jpg
- favicon.ico (2x)
- signinpage.png
- welcomegif.gif

### Auto-Generated Files (Will Update Automatically): 4
- package-lock.json
- test-results/e2e-results.json
- frontend/dist/* (all build artifacts)

### Total Estimated Time
- Preparation: 4-8 hours (asset creation)
- Implementation: 2-4 hours (file updates)
- Testing: 1-2 hours (validation)
- Documentation: 1-2 hours (migration guide)
- **Total: 8-16 hours**

---

## Next Steps

1. Review this catalog with stakeholders
2. Finalize new brand identity (colors, tagline, positioning)
3. Create new visual assets
4. Reserve new names and domains
5. Proceed with Phase 1 (Preparation)
6. Execute systematic rebrand following recommended order

---

*Document Generated: 2025-12-02*
*Codebase Analyzed: pipeshub-ai-orig*
*Target Brand: Hupyy KB*
