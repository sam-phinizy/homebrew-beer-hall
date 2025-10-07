# Sam Phinizy's Homebrew Tap (beer-hall)

This tap is a monorepo distribution hub for Sam Phinizy's scripts and tools.

## Installation

### Option 1: Using Brewfile (Recommended)

```bash
git clone https://github.com/sam-phinizy/beer-hall.git
cd beer-hall
brew bundle
```

### Option 2: Manual Installation

```bash
brew tap sam-phinizy/beer-hall
```

## Available Formulae

| name | repo link | description |
|---|---|---|
| `git-stack` | [sam-phinizy/git-stack](https://github.com/sam-phinizy/git-stack) | Git stack management tool with interactive TUI |
| `gh-pr2org` | [sam-phinizy/homebrew-beer-hall](https://github.com/sam-phinizy/homebrew-beer-hall) | Sync GitHub PRs to Emacs org-mode files |

To install, run:
```bash
brew install git-stack
brew install gh-pr2org
```

## Usage

After installation, you can use:
- `git-stack` - Interactive git stack management
- `gh-pr2org <org-file>` - Sync GitHub PRs where you're tagged to an org-mode file

## For Developers

### Quick Release with mise

This repo uses [mise](https://mise.jdx.dev) for task automation:

```bash
# Install mise
brew install mise

# Deploy a new version (creates tag and triggers CI)
mise run deploy gh-pr2org 1.0.1

# Update formula after release completes
mise run update-formula gh-pr2org 1.0.1 <SHA256>
```

See [docs/mise-usage.md](docs/mise-usage.md) for all available tasks.

### Adding New Tools

This tap includes automated CI/CD for releasing new tools:

1. Add your script to `scripts/`
2. Push a tag like `tool-name/v1.0.0` (or use `mise run deploy`)
3. GitHub Actions automatically creates the release
4. Update the formula with the new version and SHA256 hash

See [docs/adding-new-tools.md](docs/adding-new-tools.md) for detailed instructions.

### CI/CD

Releases are automated using [Dagger](https://dagger.io):
- **Pipeline**: `ci/` contains a Dagger module for release automation
- **Trigger**: Push tags matching `tool-name/v*.*.*`
- **Process**: Automatic SHA256 calculation, release creation, and asset upload

See [ci/README.md](ci/README.md) for CI/CD documentation.

## Issues

Report issues at: https://github.com/sam-phinizy/homebrew-beer-hall/issues