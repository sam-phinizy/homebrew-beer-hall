#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Sync GitHub PRs where you're tagged into an Emacs org-mode file.
Uses the gh CLI tool for authentication.
Requires: gh CLI installed and authenticated
"""

import subprocess
import json
import re
import argparse
from datetime import datetime
from collections import defaultdict

def run_gh_command(query):
    """Run gh search prs command and return JSON results."""
    cmd = ['gh', 'search', 'prs', '--json', 
           'number,title,url,repository,author,createdAt,updatedAt,state',
           query]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"gh command failed: {result.stderr}")
    return json.loads(result.stdout)

def get_tagged_prs(username):
    """Get all open PRs where the user is mentioned or requested for review."""
    prs = []
    pr_urls = set()
    
    # Get PRs where you're requested as a reviewer
    review_prs = run_gh_command(f'review-requested:{username} is:open')
    for pr in review_prs:
        pr_urls.add(pr['url'])
        prs.append({
            'repo': pr['repository']['nameWithOwner'],
            'number': pr['number'],
            'title': pr['title'],
            'url': pr['url'],
            'author': pr['author']['login'],
            'created': pr['createdAt'],
            'updated': pr['updatedAt'],
            'state': pr['state']
        })
    
    # Get PRs where you're mentioned
    mention_prs = run_gh_command(f'mentions:{username} is:open')
    for pr in mention_prs:
        # Avoid duplicates
        if pr['url'] not in pr_urls:
            pr_urls.add(pr['url'])
            prs.append({
                'repo': pr['repository']['nameWithOwner'],
                'number': pr['number'],
                'title': pr['title'],
                'url': pr['url'],
                'author': pr['author']['login'],
                'created': pr['createdAt'],
                'updated': pr['updatedAt'],
                'state': pr['state']
            })
    
    return prs

def parse_org_file(filename):
    """Parse existing org file and extract PR section."""
    try:
        with open(filename, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        return '', '', {}
    
    # Find the PR section
    pr_section_start = content.find('* Pull Requests to Review')
    
    if pr_section_start == -1:
        # No PR section exists yet
        return content, '', {}
    
    # Find the next top-level heading or end of file
    next_section = content.find('\n* ', pr_section_start + 1)
    if next_section == -1:
        before_section = content[:pr_section_start]
        pr_section = content[pr_section_start:]
        after_section = ''
    else:
        before_section = content[:pr_section_start]
        pr_section = content[pr_section_start:next_section]
        after_section = content[next_section:]
    
    # Extract existing PRs (identified by URL)
    existing_prs = {}
    pr_pattern = r'\*\* (TODO|DONE) .*?\n   :PROPERTIES:.*?:PR_URL: (https://github\.com/[^\n]+).*?:END:'
    for match in re.finditer(pr_pattern, pr_section, re.DOTALL):
        status = match.group(1)
        url = match.group(2)
        existing_prs[url] = {
            'status': status,
            'full_entry': match.group(0)
        }
    
    return before_section, after_section, existing_prs

def format_org_entry(pr):
    """Format a PR as an org-mode TODO entry."""
    created_dt = datetime.fromisoformat(pr['created'].replace('Z', '+00:00'))
    created_date = created_dt.strftime('%Y-%m-%d %a')
    
    repo_tag = pr['repo'].replace('/', '_')
    
    entry = f"""** TODO Review PR #{pr['number']}: {pr['title']}
   DEADLINE: <{created_date}>
   :PROPERTIES:
   :PR_URL: {pr['url']}
   :REPO: {pr['repo']}
   :PR_NUMBER: {pr['number']}
   :AUTHOR: {pr['author']}
   :END:
   :{repo_tag}:
   [[{pr['url']}][View PR on GitHub]]
"""
    return entry

def build_pr_section(prs):
    """Build the PR section grouped by repository."""
    # Group by repository
    repos = defaultdict(list)
    for pr in prs:
        repos[pr['repo']].append(pr)
    
    lines = ["* Pull Requests to Review\n"]
    
    # Sort repos alphabetically
    for repo in sorted(repos.keys()):
        lines.append(f"** {repo}\n")
        # Sort PRs by created date (oldest first, since they're deadlines)
        for pr in sorted(repos[repo], key=lambda x: x['created']):
            lines.append(format_org_entry(pr))
        lines.append("\n")
    
    return ''.join(lines)

def sync_prs(org_file, username):
    """Main sync function."""
    print(f"Fetching PRs for {username}...")
    current_prs = get_tagged_prs(username)
    print(f"Found {len(current_prs)} open PRs")
    
    # Parse existing org file
    before_section, after_section, existing_prs = parse_org_file(org_file)
    
    # Build current PR URL set
    current_pr_urls = {pr['url'] for pr in current_prs}
    
    # Determine what changed
    new_prs = [pr for pr in current_prs if pr['url'] not in existing_prs]
    still_open_prs = [pr for pr in current_prs if pr['url'] in existing_prs]
    closed_pr_urls = set(existing_prs.keys()) - current_pr_urls
    
    print(f"  - New PRs: {len(new_prs)}")
    print(f"  - Still open: {len(still_open_prs)}")
    print(f"  - Closed/merged: {len(closed_pr_urls)}")
    
    # Build new PR section
    pr_section = build_pr_section(current_prs)
    
    # Reconstruct file
    new_content = before_section.rstrip('\n') + '\n\n' + pr_section
    if after_section:
        new_content += '\n' + after_section.lstrip('\n')
    
    # Write back
    with open(org_file, 'w') as f:
        f.write(new_content)
    
    print(f"Updated {org_file}")

def main():
    parser = argparse.ArgumentParser(
        description='Sync GitHub PRs to org-mode file'
    )
    parser.add_argument('org_file', help='Path to org-mode file')
    parser.add_argument('--username', help='GitHub username (defaults to gh CLI user)')
    
    args = parser.parse_args()
    
    # Get username from gh CLI if not provided
    username = args.username
    if not username:
        result = subprocess.run(['gh', 'api', 'user', '--jq', '.login'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("Error: Could not get username from gh CLI")
            print("Make sure gh CLI is installed and authenticated")
            return 1
        username = result.stdout.strip()
    
    try:
        sync_prs(args.org_file, username)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == '__main__':
    exit(main())