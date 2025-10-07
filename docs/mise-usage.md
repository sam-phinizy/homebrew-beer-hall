# Using mise with beer-hall

This repository uses [mise](https://mise.jdx.dev) for task automation and development environment management.

## Installation

Install mise:

```bash
# macOS
brew install mise

# Other platforms: https://mise.jdx.dev/getting-started.html
```

Activate mise in your shell (add to ~/.zshrc or ~/.bashrc):

```bash
eval "$(mise activate zsh)"  # or bash, fish, etc.
```

## Quick Start

```bash
# List all available tasks
mise tasks

# Deploy a new tool version
mise run deploy gh-pr2org 1.0.1

# Test a release locally before pushing
mise run test-release -- --tag gh-pr2org/v1.0.1

# List available tools
mise run list-tools
```

## Available Tasks

### Release Management

#### `mise run deploy <tool> <version>`

Deploy a new version of a tool. This will:
1. Validate the tag format
2. Check if the script exists
3. Ensure changes are committed
4. Create and push the release tag
5. Trigger the GitHub Actions workflow

**Example:**
```bash
mise run deploy gh-pr2org 1.0.1
# Creates and pushes tag: gh-pr2org/v1.0.1
```

#### `mise run release <tool> <version>`

Full release workflow including deployment and watching the GitHub Actions run.

**Example:**
```bash
mise run release my-tool 2.0.0
```

#### `mise run test-release -- --tag <tag>`

Test a release locally with Dagger dry-run (doesn't create actual release).

**Example:**
```bash
mise run test-release -- --tag gh-pr2org/v1.0.1
```

**Note:** The `--` separates mise arguments from task arguments.

### Formula Management

#### `mise run update-formula <tool> <version> <sha256>`

Update a formula with new version and SHA256 hash.

**Example:**
```bash
# Get SHA256 from GitHub Actions output, then:
mise run update-formula gh-pr2org 1.0.1 d2026bb663f53e9cee6c85030dc11586a21a21694fb652131a028b7cd0eaf803
```

This task will:
- Update version and SHA256 in the formula
- Show a diff of changes
- Prompt to commit and push

### Utility Tasks

#### `mise run list-tools`

List all available tools in the scripts/ directory.

**Example:**
```bash
$ mise run list-tools
gh-pr2org
```

#### `mise run validate-tag -- --tag <tag>`

Validate a tag format.

**Example:**
```bash
mise run validate-tag -- --tag gh-pr2org/v1.0.0
✅ Tag format valid: gh-pr2org/v1.0.0
```

#### `mise run calculate-sha -- --tool <tool-name>`

Calculate SHA256 for a script.

**Example:**
```bash
$ mise run calculate-sha -- --tool gh-pr2org
📊 SHA256 for scripts/gh-pr2org.py:
d2026bb663f53e9cee6c85030dc11586a21a21694fb652131a028b7cd0eaf803  scripts/gh-pr2org.py
```

#### `mise run watch-release -- --tag <tag>`

Watch the GitHub Actions workflow for a release.

**Example:**
```bash
mise run watch-release -- --tag gh-pr2org/v1.0.0
```

### Development Tasks

#### `mise run install-local`

Install the tap locally for testing.

**Example:**
```bash
mise run install-local
# Then: brew install sam-phinizy/beer-hall/my-tool
```

#### `mise run lint-formulas`

Lint all Homebrew formulas.

**Example:**
```bash
mise run lint-formulas
```

#### `mise run ci-test`

Test the Dagger module functions.

**Example:**
```bash
mise run ci-test
```

## Typical Workflows

### Release a New Version

```bash
# 1. Update your script
vim scripts/gh-pr2org.py

# 2. Commit changes
git add scripts/gh-pr2org.py
git commit -m "Update gh-pr2org: add new feature"
git push

# 3. Deploy (creates tag and triggers CI)
mise run deploy gh-pr2org 1.0.1

# 4. Watch the workflow
mise run watch-release -- --tag gh-pr2org/v1.0.1

# 5. Get SHA256 from GitHub Actions output and update formula
mise run update-formula gh-pr2org 1.0.1 <SHA256_FROM_ACTIONS>
```

### Add a New Tool

```bash
# 1. Add script
cp my-script.py scripts/my-tool.py
git add scripts/my-tool.py
git commit -m "Add my-tool"
git push

# 2. Create formula (see docs/adding-new-tools.md)
vim Formula/my-tool.rb

# 3. Deploy first version
mise run deploy my-tool 1.0.0

# 4. Update formula with SHA256
mise run update-formula my-tool 1.0.0 <SHA256_FROM_ACTIONS>
```

### Test Before Releasing

```bash
# Test the release process locally
mise run test-release -- --tag my-tool/v1.0.0

# Validate tag format
mise run validate-tag -- --tag my-tool/v1.0.0

# Calculate SHA256 manually
mise run calculate-sha -- --tool my-tool
```

## Environment Variables

The `.mise.toml` configuration sets:

- `GITHUB_REPO=sam-phinizy/homebrew-beer-hall` - Used by tasks that interact with GitHub

You can override or add more in `.mise.local.toml` (not committed):

```toml
[env]
GITHUB_TOKEN = "ghp_..."  # For local Dagger testing
```

## Tool Version Management

mise can also manage tool versions. Uncomment in `.mise.toml`:

```toml
[tools]
python = "3.12"
gh = "latest"
uv = "latest"
dagger = "latest"
```

Then mise will automatically install and use these versions when you're in the repository.

## Customization

You can add your own tasks or override existing ones in `.mise.local.toml`:

```toml
[tasks.my-custom-task]
description = "My custom workflow"
run = "echo 'Hello from my task'"
```

Local tasks are gitignored and won't be committed.

## Troubleshooting

**Task not found:**
```bash
mise tasks  # List all available tasks
```

**Arguments not passed correctly:**
```bash
# Use -- to separate mise args from task args
mise run test-release -- --tag my-tool/v1.0.0
```

**Environment variable not set:**
```bash
# Check environment
mise env

# Set temporarily
GITHUB_TOKEN=xxx mise run test-release -- --tag my-tool/v1.0.0
```

## Further Reading

- [mise Documentation](https://mise.jdx.dev)
- [mise Tasks Documentation](https://mise.jdx.dev/tasks/)
- [mise Configuration](https://mise.jdx.dev/configuration.html)
