# Adding New Tools to beer-hall Tap

This guide walks through adding a new script/tool to the beer-hall Homebrew tap.

## Overview

beer-hall (homebrew-beer-hall on GitHub) is a monorepo Homebrew tap that distributes multiple tools. Each tool:
- Lives in `scripts/` directory
- Has its own versioned GitHub release (e.g., `tool-name/v1.0.0`)
- Has a formula in `Formula/tool-name.rb`
- Can be installed with `brew install sam-phinizy/beer-hall/tool-name`

## Step-by-Step Process

### 1. Add Your Script

Place your script in the `scripts/` directory:
```bash
# Example for a Python script using uv
cp my-script.py scripts/
```

Make sure the script has proper shebang and is executable:
```python
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
```

### 2. Create a GitHub Release

#### Option A: Automated (Recommended)

Simply push a git tag and let CI handle everything:

```bash
# Commit your script first
git add scripts/your-script.py
git commit -m "Add your-script"
git push

# Create and push a tag
git tag your-tool/v1.0.0
git push origin your-tool/v1.0.0
```

The GitHub Actions workflow will automatically:
- Create the GitHub release
- Upload the script as an asset
- Calculate and display the SHA256 hash
- Generate release notes

Check the Actions tab on GitHub to see the pipeline run and get the SHA256 hash.

#### Option B: Manual

If you prefer manual control:

**Calculate SHA256 hash:**
```bash
shasum -a 256 scripts/your-script.py
```

**Create the release:**
```bash
# Replace YOUR_TOOL with the tool name (e.g., gh-pr2org)
# Replace X.Y.Z with version (e.g., 1.0.0)
gh release create YOUR_TOOL/vX.Y.Z \
  --title "YOUR_TOOL vX.Y.Z" \
  --notes "Initial release of YOUR_TOOL" \
  scripts/your-script.py
```

**Or test locally with Dagger:**
```bash
cd ci
dagger call release \
  --tag "your-tool/v1.0.0" \
  --source .. \
  --token env:GITHUB_TOKEN
```

### 3. Create a Homebrew Formula

Create `Formula/your-tool.rb` based on the script type:

#### For Python Scripts with uv

```ruby
class YourTool < Formula
  desc "Brief description of your tool"
  homepage "https://github.com/sam-phinizy/homebrew-beer-hall"
  version "X.Y.Z"
  url "https://github.com/sam-phinizy/homebrew-beer-hall/releases/download/your-tool/v#{version}/your-script.py"
  sha256 "PASTE_SHA256_HERE"
  license "MIT"

  depends_on "gh"           # If you need gh CLI
  depends_on "python@3.12"  # For Python scripts
  depends_on "uv"           # For uv-managed scripts

  def install
    # Install the script
    libexec.install "your-script.py"

    # Create a wrapper that calls uv run
    (bin/"your-tool").write <<~EOS
      #!/bin/bash
      exec uv run "#{libexec}/your-script.py" "$@"
    EOS
  end

  test do
    assert_match "usage", shell_output("#{bin}/your-tool --help", 0)
  end
end
```

#### For Shell Scripts

```ruby
class YourTool < Formula
  desc "Brief description of your tool"
  homepage "https://github.com/sam-phinizy/homebrew-beer-hall"
  version "X.Y.Z"
  url "https://github.com/sam-phinizy/homebrew-beer-hall/releases/download/your-tool/v#{version}/your-script.sh"
  sha256 "PASTE_SHA256_HERE"
  license "MIT"

  def install
    bin.install "your-script.sh" => "your-tool"
  end

  test do
    system "#{bin}/your-tool", "--version"
  end
end
```

#### For Compiled Binaries (like git-stack)

See `Formula/git-stack.rb` for reference. This pattern is for tools with separate binaries per platform.

### 4. Update Documentation

**Add to README.md:**

Add your tool to the Available Formulae table:
```markdown
| `your-tool` | [sam-phinizy/homebrew-beer-hall](https://github.com/sam-phinizy/homebrew-beer-hall) | Brief description |
```

**Add to Brewfile (optional):**

For local testing convenience:
```ruby
brew "your-tool"
```

### 5. Test the Formula

```bash
# Tap your local repo (if not already)
brew tap sam-phinizy/beer-hall /Users/sphinizy/src/github.com/sam-phinizy/beer-hall

# Install your tool
brew install sam-phinizy/beer-hall/your-tool

# Test it works
your-tool --help

# Uninstall for cleanup
brew uninstall your-tool
```

### 6. Commit and Push

```bash
git add Formula/your-tool.rb scripts/your-script.py README.md Brewfile
git commit -m "Add your-tool vX.Y.Z formula"
git push
```

## Updating an Existing Tool

1. Update the script in `scripts/`
2. Increment version in `Formula/your-tool.rb`
3. Create new release with new version tag
4. Update SHA256 in formula
5. Test and commit

```bash
# Example: Update gh-pr2org to v1.0.1
shasum -a 256 scripts/gh-pr2org.py

gh release create gh-pr2org/v1.0.1 \
  --title "gh-pr2org v1.0.1" \
  --notes "Bug fixes and improvements" \
  scripts/gh-pr2org.py

# Edit Formula/gh-pr2org.rb:
# - Update version = "1.0.1"
# - Update sha256 = "NEW_HASH"

brew upgrade sam-phinizy/beer-hall/gh-pr2org
```

## Naming Conventions

- **Script files**: `kebab-case` (e.g., `gh-pr2org.py`)
- **Formula class**: `PascalCase` (e.g., `GhPr2org`)
- **Formula file**: `kebab-case.rb` (e.g., `gh-pr2org.rb`)
- **Release tags**: `tool-name/vX.Y.Z` (e.g., `gh-pr2org/v1.0.0`)
- **Command name**: `kebab-case` (e.g., `gh-pr2org`)

## Common Dependencies

- `gh` - GitHub CLI
- `python@3.12` - Python runtime
- `uv` - Python package and script runner
- `git` - Usually already present, rarely needed to declare

## Troubleshooting

**Formula won't install:**
- Check SHA256 hash matches the release asset
- Verify URL points to correct release tag
- Ensure all dependencies are declared

**Command not found after install:**
- Check wrapper script in bin/ is executable
- Verify binary name matches expected command

**Python script fails:**
- Ensure shebang is correct for uv
- Check Python version requirement
- Verify dependencies in PEP 723 header

**Automated release fails:**
- Verify tag format is exactly: `tool-name/vX.Y.Z`
- Ensure script exists in `scripts/` directory
- Check GitHub Actions logs for detailed error messages
- See `ci/README.md` for more troubleshooting tips

## CI/CD Pipeline

The repository uses Dagger for automated releases. Here's how it works:

### Architecture

- **Dagger Module** (`ci/`): Python-based automation for releases
- **GitHub Actions** (`.github/workflows/release-tool.yml`): Triggers on tag push
- **Workflow**: Tag push → Parse tag → Find script → Calculate SHA256 → Create release

### Benefits

1. **Consistency**: Same SHA256 calculation every time
2. **Automation**: No manual steps for releases
3. **Transparency**: All actions visible in GitHub Actions logs
4. **Testability**: Can test locally with Dagger CLI before pushing

### Local Testing

Before pushing a tag, test the release locally:

```bash
cd ci

# Dry run to see what would happen
dagger call create-release \
  --tag "your-tool/v1.0.0" \
  --source .. \
  --token env:GITHUB_TOKEN \
  --dry-run true

# Test individual functions
dagger call parse-tag --tag "your-tool/v1.0.0"
dagger call find-script --source .. --tool-name "your-tool"
```

### Extending the Pipeline

Want to add more automation? Edit `ci/src/release_tool/src/release_tool/main.py`:

- Add formula auto-update
- Generate changelogs from commits
- Run validation tests before release
- Send notifications

See `ci/README.md` for detailed documentation on the Dagger module.
