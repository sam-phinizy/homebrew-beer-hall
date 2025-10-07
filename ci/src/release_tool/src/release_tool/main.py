"""Release automation for beer-hall tools"""

import re
from pathlib import Path
import dagger
from dagger import dag, function, object_type, field


@object_type
class ReleaseTool:
    """Automate GitHub releases for beer-hall tools"""

    repo_dir: dagger.Directory = field(default=lambda: dag.directory())
    github_token: dagger.Secret | None = field(default=None)

    @function
    def parse_tag(self, tag: str) -> dict[str, str]:
        """
        Parse a tool release tag into tool name and version.

        Tag format: tool-name/vX.Y.Z
        Example: gh-pr2org/v1.0.0

        Args:
            tag: The git tag to parse (e.g., "gh-pr2org/v1.0.0")

        Returns:
            Dict with 'tool_name' and 'version' keys
        """
        pattern = r'^([a-z0-9-]+)/v(\d+\.\d+\.\d+)$'
        match = re.match(pattern, tag)

        if not match:
            raise ValueError(
                f"Invalid tag format: {tag}. "
                "Expected format: tool-name/vX.Y.Z (e.g., gh-pr2org/v1.0.0)"
            )

        tool_name, version = match.groups()
        return {"tool_name": tool_name, "version": version}

    @function
    async def calculate_sha256(
        self,
        source: dagger.Directory,
        file_path: str,
    ) -> str:
        """
        Calculate SHA256 hash of a file.

        Args:
            source: Directory containing the file
            file_path: Path to file relative to source directory

        Returns:
            SHA256 hash as hex string
        """
        return await (
            dag.container()
            .from_("alpine:latest")
            .with_mounted_directory("/work", source)
            .with_workdir("/work")
            .with_exec(["sha256sum", file_path])
            .stdout()
        )

    @function
    async def find_script(
        self,
        source: dagger.Directory,
        tool_name: str,
    ) -> str:
        """
        Find the script file for a tool in the scripts/ directory.

        Args:
            source: Repository root directory
            tool_name: Name of the tool

        Returns:
            Relative path to the script file
        """
        # List files in scripts directory
        entries = await source.directory("scripts").entries()

        # Find files that match tool_name with any extension
        matches = [e for e in entries if e.startswith(f"{tool_name}.")]

        if not matches:
            raise ValueError(
                f"No script found for tool '{tool_name}' in scripts/ directory. "
                f"Available files: {entries}"
            )

        if len(matches) > 1:
            raise ValueError(
                f"Multiple scripts found for tool '{tool_name}': {matches}. "
                "Please ensure only one script exists per tool."
            )

        return f"scripts/{matches[0]}"

    @function
    async def create_release(
        self,
        tag: str,
        source: dagger.Directory,
        token: dagger.Secret,
        dry_run: bool = False,
    ) -> str:
        """
        Create a GitHub release for a tool.

        This function:
        1. Parses the tag to extract tool name and version
        2. Finds the script file in scripts/
        3. Calculates the SHA256 hash
        4. Creates a GitHub release with the script as an asset

        Args:
            tag: Git tag (e.g., "gh-pr2org/v1.0.0")
            source: Repository root directory
            token: GitHub token for authentication
            dry_run: If true, print what would be done without creating release

        Returns:
            Success message with release URL or dry-run information
        """
        # Parse tag
        parsed = self.parse_tag(tag)
        tool_name = parsed["tool_name"]
        version = parsed["version"]

        # Find script
        script_path = await self.find_script(source, tool_name)
        script_filename = Path(script_path).name

        # Calculate SHA256
        sha256_output = await self.calculate_sha256(source, script_path)
        sha256_hash = sha256_output.split()[0]

        # Prepare release notes
        release_notes = f"""Release of {tool_name} v{version}

**Installation:**
```bash
brew install sam-phinizy/beer-hall/{tool_name}
```

**SHA256:** `{sha256_hash}`

---
*This release was automatically created by the beer-hall CI pipeline.*
"""

        if dry_run:
            return f"""DRY RUN - Would create release:
Tag: {tag}
Tool: {tool_name}
Version: {version}
Script: {script_path}
SHA256: {sha256_hash}

Release Notes:
{release_notes}
"""

        # Create container with gh CLI
        container = (
            dag.container()
            .from_("ghcr.io/cli/cli:latest")
            .with_secret_variable("GH_TOKEN", token)
            .with_mounted_directory("/repo", source)
            .with_workdir("/repo")
        )

        # Create the release
        result = await container.with_exec([
            "gh", "release", "create", tag,
            script_path,
            "--title", f"{tool_name} v{version}",
            "--notes", release_notes,
        ]).stdout()

        return f"""Release created successfully!
{result}

SHA256 hash for formula: {sha256_hash}

Next steps:
1. Update Formula/{tool_name}.rb with:
   - version = "{version}"
   - sha256 = "{sha256_hash}"
2. Commit and push the formula update
"""

    @function
    async def release(
        self,
        tag: str,
        source: dagger.Directory,
        token: dagger.Secret,
    ) -> str:
        """
        Main entry point for releasing a tool.

        Args:
            tag: Git tag (e.g., "gh-pr2org/v1.0.0")
            source: Repository root directory
            token: GitHub token

        Returns:
            Release result message
        """
        return await self.create_release(tag, source, token, dry_run=False)
