# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is `aiocomfoconnect`, a Python 3.10+ asyncio library and CLI for communicating with Zehnder ComfoAir Q350/450/600 ventilation units via the ComfoConnect LAN C bridge. It provides both a high-level API and low-level protocol access for controlling ventilation systems.

## Development Commands

### Setup and Dependencies
- `poetry install` - Install dependencies
- `poetry install --with dev` - Install with development dependencies  

### Code Quality and Linting
- `make check` - Run both pylint and black checks
- `make check-pylint` - Run pylint only: `poetry run pylint aiocomfoconnect/*.py`
- `make check-black` - Run black format check: `poetry run black --check aiocomfoconnect/*.py`
- `make codefix` - Auto-format code: `poetry run isort aiocomfoconnect/*.py && poetry run black aiocomfoconnect/*.py`

### Testing
- `make test` - Run tests: `poetry run pytest`

### Protocol Buffer Generation
- `python3 -m grpc_tools.protoc -Iprotobuf --python_out=aiocomfoconnect/protobuf protobuf/*.proto` - Regenerate protobuf files from .proto definitions

### CLI Usage
- `python -m aiocomfoconnect --help` - Show CLI help
- `python -m aiocomfoconnect discover` - Discover bridges on network
- `python -m aiocomfoconnect register --host <IP>` - Register application with bridge

### Docker
- `make build` - Build Docker image: `docker build -t aiocomfoconnect .`

## Architecture

### Core Components

- **Bridge** (`bridge.py`): Low-level protocol communication with ComfoConnect LAN C bridge
- **ComfoConnect** (`comfoconnect.py`): High-level API abstraction for ventilation control
- **Discovery** (`discovery.py`): Network discovery of ComfoConnect LAN C bridges
- **Sensors** (`sensors.py`): Sensor definitions and data structures  
- **Properties** (`properties.py`): Device property definitions and mappings
- **Constants** (`const.py`): Enums and constants for ventilation modes, speeds, etc.

### Protocol Implementation

- **protobuf/**: Generated Protocol Buffer classes from zehnder.proto and nanopb.proto
- **Protocol docs**: docs/PROTOCOL*.md files document the reverse-engineered ComfoConnect protocol
- **Packet decoding**: script/decode_pcap.py for analyzing network traffic

### Key Design Patterns

- Asyncio-based communication with async/await throughout
- Sensor callback system for real-time updates
- Decorator-based connection management (`decorators.py`)
- Exception hierarchy for different error conditions (`exceptions.py`)

### Main Classes

- `ComfoConnect`: Main API class for high-level ventilation control
- `Bridge`: Low-level protocol implementation
- `SENSORS`: Dictionary of all available sensor definitions
- `PROPERTIES`: Dictionary of all available property definitions

## Git Workflow

### Branching Strategy: GitHub Flow

This project uses **GitHub Flow** for clean, simple development:

1. **master branch**: Always stable and deployable
2. **Feature branches**: Short-lived branches for specific work
3. **Pull Request workflow**: All changes reviewed before merge

### Standard Development Workflow

```bash
# 1. Start new feature
git checkout master
git pull origin master  
git checkout -b feature/description-of-work

# 2. Develop with quality checks
# ... make changes ...
make test && make check  # Always run before committing

# 3. Commit with conventional commit messages
git add .
git commit -m "feat: add new functionality"
# OR: fix:, refactor:, docs:, test:, etc.

# 4. Push and create PR
git push origin feature/description-of-work
# Create Pull Request on GitHub

# 5. After approval, merge and cleanup
git checkout master
git pull origin master
git branch -d feature/description-of-work
git push origin --delete feature/description-of-work
```

### Branch Naming Conventions

- `feature/description` - New features or enhancements
- `fix/description` - Bug fixes
- `refactor/description` - Code improvements without behavior change
- `docs/description` - Documentation updates
- `test/description` - Test improvements

### Commit Message Standards

Follow conventional commits:
- `feat:` - New features
- `fix:` - Bug fixes  
- `refactor:` - Code refactoring
- `docs:` - Documentation changes
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks
- `ci:` - CI/CD changes

### Quality Gates

Before any commit to master:
1. ✅ All tests pass (`make test`)
2. ✅ Code quality checks pass (`make check`)
3. ✅ Pylint score remains 10.00/10
4. ✅ CLI functionality verified if applicable

### Repository Maintenance

Periodically clean up:
```bash
# Remove merged feature branches
git branch --merged master | grep -v master | xargs -n 1 git branch -d

# Clean up unreferenced commits
git reflog expire --expire=30.days --all
git gc --aggressive
```

## Code Style

- Black formatter with 180 character line length
- isort for import sorting with black profile
- Pylint for code quality (extensive disable list in pyproject.toml)
- Target Python 3.10+ with modern async/await patterns