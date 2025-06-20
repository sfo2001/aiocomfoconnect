# Upstream Contribution Strategy

## Overview

Plan to reorganize 42 commits (d66b747..HEAD) into 8 logical, reviewable PRs for contributing back to the original aiocomfoconnect repository.

## Current Status
- **Total commits to reorganize:** 42 commits since fork point d66b747 (Release v0.1.14)
- **Strategy:** Interactive rebase + logical grouping
- **Goal:** Create meaningful, reviewable PRs instead of one massive change
- **Status:** IMPLEMENTATION PHASE - PR1 COMPLETED ✅

## Implementation Log

### Option 1 Decision: Plan Integration
**Date:** 2025-06-20  
**Decision:** Copy UPSTREAM_CONTRIBUTION_PLAN.md to working branches for ongoing reference
**Rationale:** 
- Ensures plan accessibility during implementation
- Allows progress tracking and plan updates
- Provides documentation context for future Claude Code sessions
- Alternative considered: Keep in separate planning branch (rejected - creates access barriers)

### Progress Tracking
- ✅ **PR1 COMPLETED** - "Fix connection hang when device not registered" 
  - Branch: `upstream/pr1-fix-connection-hang`
  - Commit: 1b5b442 (cherry-picked from 10a82f5)
  - Status: Merged to clean master, pushed to GitHub
  - Quality Gates: Phase 1 passed (CLI validation, basic import)
- ✅ **PR2 COMPLETED** - "Fix discovery broadcast address issue"
  - Branch: `upstream/pr2-fix-discovery-broadcast`
  - Commit: 4c2fc07 (cherry-picked from 7dd94ad)
  - Status: Merged to clean master, pushed to GitHub
  - Quality Gates: Phase 1 passed (CLI validation, basic import, discovery command tested)

## REVISED Logical Grouping Strategy

### Phase 1: Critical Bug Fixes (PRs 1-3) - **HIGHEST PRIORITY**

#### PR1: "Fix connection hang when device not registered" 
```
Single commit - original repo bug:
- #43: 10a82f5 fix _connect hang when not registered device (#50)

Analysis: External contributor fix for original repo issue
Impact: Critical - prevents connection hangs
Files: aiocomfoconnect/comfoconnect.py (6 lines)
```

#### PR2: "Fix discovery broadcast address issue"
```
Single commit - original repo bug:
- #38: 7dd94ad fix(discovery): correct broadcast address issue in discovery process

Analysis: Discovery process failing with broadcast addresses  
Impact: Critical - enables device discovery in all network setups
Files: aiocomfoconnect/discovery.py, pyproject.toml
```

#### PR3: "Fix bytes concatenation error in ComfoCool mode"
```
Single commit - original repo bug:
- #19: 75d1dbb fix: resolve bytes concatenation error in set_comfocool_mode_enum

Analysis: Method completely broken due to TypeError
Impact: Critical - fixes broken functionality
Files: aiocomfoconnect/comfoconnect.py (1 line)
```

### Phase 2: Infrastructure & Quality Foundation (PRs 4A-5)

#### PR4A: "Modernize build configuration and dependencies"
```
Commits to combine (Build config without conflicts):
- #25: a6b2270 build: restructure pyproject.toml and update lock files
- #23: 995ddd7 chore: add poetry.lock to ensure consistent dependency versions
- #8: 84b339b chore: integrate pylint-protobuf plugin and add mypy dependency

Analysis: Modernizes Python project configuration and dependencies
Impact: Enables modern tooling and consistent dependency management
Strategy: Group all build configuration changes for clean review
```

#### PR4B: "Enhance CI/CD pipeline with comprehensive testing"
```
Commits to combine (CI pipeline enhancements):
- #24: 170dcca ci: update workflow configuration and enhance job steps  
- #20: 8bcf1ec ci: enhance GitHub Actions workflow with comprehensive testing and coverage
- #11: c4d2a9c ci: enhance Poetry setup and caching in CI workflow

Analysis: Modernizes GitHub Actions with quality gates and testing
Impact: Provides automated quality validation for all future PRs
Dependency: Requires PR4A (pyproject.toml setup) to work properly
```

#### PR5: "Add comprehensive test suite"
```
Single commit - enables quality validation:
- #22: 59ccba0 test: create comprehensive unit test suite from scratch  
- #21: 0e56a02 chore: add test cache and coverage files to .gitignore

Analysis: Creates testing foundation (288 tests)
Impact: Enables validation of all future changes
Dependency: Requires PR4A (pytest setup) to work properly
```

### Phase 3: Core Modernization - **DEPENDENCY ORDER** (PRs 6-8)

#### PR6: "Modernize exceptions and error handling"
```
Combine with its fix:
- #33: e89bd12 refactor(aiocomfoconnect): modernize exceptions and improve documentation
- #32: d06d9a7 feat(aiocomfoconnect): enhance bridge API and add decorators  
- #5: 5618a9f feat(aiocomfoconnect): enhance bridge API and add decorators (CLEANUP)

Analysis: #5 fixes bugs introduced by #32 (missing pass, logging format, duplicate self.message)
Strategy: Combine all three to create one clean bridge enhancement
```

#### PR7: "Modernize core data modules (sensors, properties, utilities)"
```
Standalone modernizations:
- #35: b298b7f refactor(aiocomfoconnect): modernize and document sensors module
- #34: 52102a0 refactor(aiocomfoconnect): modernize properties.py and improve docs
- #6: 9d9698c feat(aiocomfoconnect): add airflow constraints and utility enhancements

Analysis: Core data structures with comprehensive docstrings/type hints  
Strategy: Include const.py constants needed by util.py enhancements
Dependency: Must come after PR6 (exceptions) but before PR8 (bridge)
```

#### PR8: "Eliminate code duplication and improve bridge architecture"  
```
Sequential refactoring commits:
- #18: 46bc95b refactor: extract methods from complex connect function
- #17: 9ccc90c refactor: extract methods from complex _send function in Bridge
- #16: 3697505 refactor: eliminate duplicate enum conversion pattern with utility function
- #15: 9723c61 refactor: massive code duplication elimination with generic RMI helpers

Analysis: Systematic refactoring for maintainability
Strategy: Keep sequential to show evolution of improvements  
Dependency: Requires PR6 (ComfoConnectNotAllowed exception import)
```

### Phase 4: CLI & Documentation (PRs 9-10)

#### PR9: "Expand and modernize CLI functionality"
```  
CLI evolution commits:
- #28: 522ba64 refactor(CLI): improve CLI structure and add helper function
- #27: 02e4c83 feat(CLI): expand CLI functionality and improve documentation
- #10: c2098f3 refactor: clean up CLI implementation and add missing commands
- #12: c3db4ae refactor: eliminate major code smells in CLI module with factory patterns

Analysis: CLI improvements with factory patterns
Strategy: Group all CLI changes to avoid command conflicts
```

#### PR10: "Comprehensive documentation improvements"
```
Documentation commits:
- #31: 012ed7d docs(aiocomfoconnect): enhance class and method documentation
- #26: 0783129 docs: enhance README and protocol documentation
- #14: c847103 docs: enhance README with development commands and fix documentation links
- #37: 9beba9f style(markdown): fix linting issues and formatting errors

Analysis: Project documentation overhaul
Strategy: Group all documentation to avoid README conflicts
```

### Updated Priority Order: **FIXES → FOUNDATION → CORE → FEATURES**
**Total PRs: 11 (was 10) due to PR4 split**

#### PR1: "Add comprehensive test suite"
```
Commits to combine:
- #22: 59ccba0 test: create comprehensive unit test suite from scratch
- #21: 0e56a02 chore: add test cache and coverage files to .gitignore

Implementation:
git checkout d66b747
git checkout -b feature/comprehensive-test-suite
git cherry-pick 59ccba0 0e56a02
# Test: make test && make check
```

#### PR2: "Fix critical connection bugs"
```
Commits to combine:
- #43: 10a82f5 fix _connect hang when not registered device (#50)
- #38: 7dd94ad fix(discovery): correct broadcast address issue in discovery process
- #19: 75d1dbb fix: resolve bytes concatenation error in set_comfocool_mode_enum

Implementation:
git checkout d66b747
git checkout -b fix/connection-stability
git cherry-pick 10a82f5 7dd94ad 75d1dbb
# May need rebase -i to squash/reorder
```

### Group 2: Code Quality & Modernization (PRs 3-5)

#### PR3: "Modernize core modules with Python 3.10+ patterns"
```
Commits to combine:
- #35: b298b7f refactor(aiocomfoconnect): modernize and document sensors module
- #34: 52102a0 refactor(aiocomfoconnect): modernize properties.py and improve docs  
- #33: e89bd12 refactor(aiocomfoconnect): modernize exceptions and improve documentation

Implementation:
git checkout d66b747
git checkout -b refactor/modernize-core-modules
git cherry-pick b298b7f 52102a0 e89bd12
```

#### PR4: "Improve code quality and eliminate duplication"
```
Commits to combine:
- #18: 46bc95b refactor: extract methods from complex connect function
- #17: 9ccc90c refactor: extract methods from complex _send function in Bridge
- #16: 3697505 refactor: eliminate duplicate enum conversion pattern with utility function
- #15: 9723c61 refactor: massive code duplication elimination with generic RMI helpers
- #12: c3db4ae refactor: eliminate major code smells in CLI module with factory patterns

Implementation:
git checkout d66b747
git checkout -b refactor/code-quality-improvements
# Cherry-pick in logical order, may need interactive rebase
```

#### PR5: "Add decorators and enhanced bridge API"
```
Commits to combine:
- #32: d06d9a7 feat(aiocomfoconnect): enhance bridge API and add decorators
- #5: 5618a9f feat(aiocomfoconnect): enhance bridge API and add decorators (POTENTIAL DUPLICATE)
- #6: 9d9698c feat(aiocomfoconnect): add airflow constraints and utility enhancements

Note: Check if #32 and #5 are duplicates - may need to compare content
```

### Group 3: CLI & Documentation (PRs 6-7)

#### PR6: "Expand CLI functionality"
```
Commits to combine:
- #28: 522ba64 refactor(CLI): improve CLI structure and add helper function
- #27: 02e4c83 feat(CLI): expand CLI functionality and improve documentation
- #10: c2098f3 refactor: clean up CLI implementation and add missing commands

Implementation:
git checkout d66b747
git checkout -b feat/enhanced-cli
```

#### PR7: "Comprehensive documentation improvements"
```
Commits to combine:
- #31: 012ed7d docs(aiocomfoconnect): enhance class and method documentation
- #26: 0783129 docs: enhance README and protocol documentation  
- #14: c847103 docs: enhance README with development commands and fix documentation links
- #37: 9beba9f style(markdown): fix linting issues and formatting errors

Implementation:
git checkout d66b747
git checkout -b docs/comprehensive-improvements
```

### Group 4: CI/CD & Build (PR 8)

#### PR8: "Modernize CI/CD pipeline and build configuration"
```
Commits to combine:
- #25: a6b2270 build: restructure pyproject.toml and update lock files
- #24: 170dcca ci: update workflow configuration and enhance job steps
- #20: 8bcf1ec ci: enhance GitHub Actions workflow with comprehensive testing and coverage
- #11: c4d2a9c ci: enhance Poetry setup and caching in CI workflow
- #8: 84b339b chore: integrate pylint-protobuf plugin and add mypy dependency
- #23: 995ddd7 chore: add poetry.lock to ensure consistent dependency versions

Implementation:
git checkout d66b747  
git checkout -b ci/modernize-pipeline
```

## STRATEGY ADVANTAGES

### Fix-First Approach Benefits:
1. **Immediate Value**: Critical bugs fixed first provide immediate benefit to users
2. **Clean Foundation**: Infrastructure setup enables quality gates for later PRs  
3. **Reduced Conflicts**: Phased approach by module/functionality type
4. **Reviewability**: Each PR has clear, focused purpose and manageable size

### Conflict Avoidance Strategy:
1. **Module Separation**: Group changes by affected modules to minimize conflicts
2. **Sequential Dependencies**: Earlier PRs create foundation for later ones
3. **Size Management**: Largest PR has 6 commits, most have 1-4 commits
4. **Bug Fix Integration**: Self-introduced bugs merged with causing refactor

## RESOLVED REVIEW QUESTIONS

- ✅ **Bug Fix Independence**: All three are original repo bugs, can be separate PRs
- ✅ **Duplicate Resolution**: #32 and #5 combined to eliminate self-introduced bugs  
- ✅ **Test Suite Placement**: Moved to Phase 2 after infrastructure setup
- ✅ **Dependency Order**: FIXES → FOUNDATION → CORE → FEATURES
- ✅ **Conflict Management**: Grouped by module type and functionality

## RESOLVED ANALYSIS QUESTIONS

- ✅ **Q1**: Should PR4 (6 CI/build commits) be split into 2 smaller PRs?
  - **Answer**: YES - Split into PR4A (Build Config) + PR4B (CI Pipeline) for better reviewability
  - **PR4A**: pyproject.toml, poetry.lock, pylint plugins (3 commits)  
  - **PR4B**: GitHub Actions workflow enhancements (3 commits)

- ✅ **Q2**: Are there any hidden dependencies between Phase 3 modernization PRs?
  - **Answer**: YES - Critical dependency: Bridge refactoring imports ComfoConnectNotAllowed from exceptions
  - **Required Order**: PR6 → PR7 → PR8 (exceptions → data modules → bridge refactoring)
  - **Additional**: util.py enhancements need const.py constants added with PR7

- ✅ **Q3**: Should some documentation come earlier to explain new features?
  - **Answer**: NO - Documentation supports existing features, no critical explanatory content needed earlier
  - **Recommendation**: Keep documentation in Phase 4 as planned

## Commits to Exclude from Upstream (Keep in Fork Only)
```
- #1: 2091b3b docs: add comprehensive Git workflow and development guidelines (fork-specific)
- #39: b5c9570 Release v0.1.15 (version management)
- #40: 7937e99 Update README.md (may be duplicate)
- #41: 4ce9a4c Update protobuf to 6.31 (#56) (version bump)
- #42: 3a8cae6 Update FUNDING.yml (project meta)
- #36: e4b46a6 chore: expand .gitignore for better project hygiene (minor)
```

## Implementation Steps (After Review Complete)

### Phase 1: Preparation
1. Backup current state: `git branch backup/before-rebase HEAD`
2. Study original repo: Check current state, recent changes, contribution guidelines
3. Test baseline: Ensure d66b747 builds and tests pass

### Phase 2: Create Feature Branches
For each PR group:
1. `git checkout d66b747`
2. `git checkout -b feature/group-name`
3. Cherry-pick relevant commits
4. Interactive rebase to clean up: `git rebase -i d66b747`
5. Test independently: `make test && make check`
6. Push branch: `git push origin feature/group-name`

### Phase 3: Quality Gates
Each PR must pass:
- ✅ Independent build/test (`make test` passes)
- ✅ Code quality maintained/improved
- ✅ Clear, focused purpose
- ✅ No breaking changes
- ✅ Appropriate documentation

### Phase 4: Upstream Submission
1. Create PRs in logical order (foundation first)
2. Reference related issues if any exist
3. Provide clear description of changes and benefits
4. Be prepared to iterate based on maintainer feedback

## Next Session Commands

To resume this work:
```bash
# Switch to planning branch
git checkout planning/upstream-contribution-strategy

# Review this plan
cat UPSTREAM_CONTRIBUTION_PLAN.md

# Start with first group (after review complete)
git checkout d66b747
git checkout -b feature/comprehensive-test-suite
# ... continue with implementation
```

## Notes
- Original repo fork point: d66b747 (Release v0.1.14)
- Current total commits: 42
- Target: 8 focused PRs
- Strategy: Cherry-pick + interactive rebase + independent testing