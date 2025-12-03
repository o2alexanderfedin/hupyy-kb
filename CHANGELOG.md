# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-12-03

### Changed - MAJOR REBRAND

**PipesHub is now Hupyy KB**

This is a comprehensive rebrand of the entire project. All functionality remains the same, but the name, branding, and visual identity have been updated.

#### Brand Changes
- Project name: PipesHub → Hupyy KB
- Domain: pipeshub.com → hupyy.com
- Documentation: docs.pipeshub.com → docs.hupyy.com
- Contact email: contact@pipeshub.com → contact@hupyy.com
- Docker image: pipeshubai/pipeshub-ai → hupyy/hupyy-kb
- Package names: pipeshub-* → hupyy-*
- Social media: x.com/PipesHub → x.com/HupyyKB

#### Visual Identity
- New logo and brand assets (SVG)
- Updated page title and meta tags
- New branding throughout UI

#### Technical Updates
- Docker service names updated: pipeshub-ai → hupyy-kb
- Volume names updated: pipeshub_* → hupyy_*
- Configuration files updated
- All documentation updated (180+ references)
- Migration guide provided (MIGRATION-GUIDE.md)

#### Breaking Changes
- Docker image name changed (see MIGRATION-GUIDE.md)
- Docker volume names changed (migration required for existing deployments)
- Package names changed (update dependencies)

#### Migration
See MIGRATION-GUIDE.md for detailed migration instructions for self-hosted users.

#### What Hasn't Changed
- All features and functionality
- API endpoints and responses
- Database schemas
- Connector integrations
- User data and settings

## [0.1.11] - 2025-11-XX

### Added
- Hupyy verification testing suite
- Local Filesystem connector improvements

### Fixed
- Kafka consumer offset commit fix

---

*For earlier versions, see git history*
