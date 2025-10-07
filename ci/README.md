# Release Automation with Dagger

This directory contains a Dagger module that automates GitHub releases for tools in the beer-hall Homebrew tap.

## What It Does

When you push a git tag in the format `tool-name/vX.Y.Z`, the CI pipeline will automatically:

1. Parse the tag to extract the tool name and version
2. Find the script file in `scripts/`
3. Calculate the SHA256 hash
4. Create a GitHub release with the script as an asset
5. Generate release notes with installation instructions

## Usage

### Automated (via GitHub Actions)

Simply push a tag:

```bash
git tag gh-pr2org/v1.0.1
git push origin gh-pr2org/v1.0.1
```

The GitHub Actions workflow (`.github/workflows/release-tool.yml`) will automatically:
- Trigger on the tag push
- Run the Dagger pipeline
- Create the GitHub release

### Manual (via Dagger CLI)

You can also run the release pipeline locally:

```bash
# From repository root
cd ci

# Test with dry-run
dagger call create-release \
  --tag "gh-pr2org/v1.0.1" \
  --source .. \
  --token env:GITHUB_TOKEN \
  --dry-run true

# Create actual release
dagger call release \
  --tag "gh-pr2org/v1.0.1" \
  --source .. \
  --token env:GITHUB_TOKEN
```

### Testing Individual Functions

The Dagger module exposes several functions you can test independently:

```bash
# Parse a tag
dagger call parse-tag --tag "gh-pr2org/v1.0.0"

# Find a script
dagger call find-script --source .. --tool-name "gh-pr2org"

# Calculate SHA256
dagger call calculate-sha256 --source .. --file-path "scripts/gh-pr2org.py"
```

## Requirements

- [Dagger](https://docs.dagger.io/install) installed locally (for manual runs)
- GitHub token with `contents: write` permission (for creating releases)

## Module Structure

```
ci/
├── README.md                    # This file
├── dagger.json                  # Dagger module configuration
├── LICENSE                      # Apache-2.0 license
└── src/
    └── release_tool/
        ├── pyproject.toml       # Python dependencies
        ├── uv.lock              # Locked dependencies
        ├── sdk/                 # Vendored Dagger Python SDK
        └── src/
            └── release_tool/
                ├── __init__.py  # Module exports
                └── main.py      # Release automation logic
```

## How It Works

1. **Tag Parsing**: Validates tag format and extracts tool name and version
2. **Script Discovery**: Searches `scripts/` directory for matching tool file
3. **Hash Calculation**: Uses `sha256sum` in an Alpine container
4. **Release Creation**: Uses `gh` CLI in a container to create the GitHub release

## Troubleshooting

**"Invalid tag format" error:**
- Ensure your tag matches the pattern: `tool-name/vX.Y.Z`
- Example: `gh-pr2org/v1.0.0` (not `v1.0.0` or `gh-pr2org-v1.0.0`)

**"No script found" error:**
- Verify the script exists in `scripts/` directory
- Script filename must match the tool name: `tool-name.*`
- Example: for tag `gh-pr2org/v1.0.0`, expect `scripts/gh-pr2org.py`

**GitHub token issues:**
- Ensure `GITHUB_TOKEN` environment variable is set
- Token needs `contents: write` permission
- In GitHub Actions, use the built-in `${{ secrets.GITHUB_TOKEN }}`

## Extending the Pipeline

To add new functionality:

1. Edit `src/release_tool/src/release_tool/main.py`
2. Add new `@function` decorated methods to the `ReleaseTool` class
3. Test locally with `dagger call <function-name>`
4. Functions are automatically available in GitHub Actions

## Future Enhancements

Potential improvements:
- Automatically update formula files with new version/SHA256
- Create a PR with formula updates
- Validate formula before release
- Support for multi-file releases
- Changelog generation from git commits
