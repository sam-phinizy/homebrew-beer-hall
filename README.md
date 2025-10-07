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

## Adding New Tools

See [docs/adding-new-tools.md](docs/adding-new-tools.md) for instructions on adding new scripts to this tap.

## Issues

Report issues at: https://github.com/sam-phinizy/homebrew-beer-hall/issues