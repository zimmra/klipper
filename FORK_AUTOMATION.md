# Automated Fork Maintenance

This repository includes an automated system for maintaining a Klipper fork with eddy-ng integration.

## Overview

The automation system:
- **Updates daily** from upstream Klipper3D/klipper
- **Updates eddy-ng** from vvuk/eddy-ng
- **Reapplies eddy-ng integration** after updates
- **Handles merge conflicts** gracefully
- **Commits changes** automatically when updates are available

## GitHub Action Workflow

The automation is handled by `.github/workflows/update-fork.yml` which:

### Triggers
- **Scheduled**: Runs daily at 2 AM UTC
- **Manual**: Can be triggered manually from the Actions tab

### Process
1. **Checkout** the repository with full history
2. **Set up** Python environment
3. **Configure** Git for automated commits
4. **Add upstream** remote (Klipper3D/klipper)
5. **Fetch** upstream changes
6. **Update** eddy-ng to latest version
7. **Merge** upstream changes (if available)
8. **Uninstall** eddy-ng integration before merge (to avoid conflicts)
9. **Reinstall** eddy-ng integration after merge
10. **Commit** and push changes (if any)
11. **Generate** summary report

### Smart Features
- **Conflict Resolution**: Temporarily removes eddy-ng files before merging to avoid conflicts
- **Change Detection**: Only commits when there are actual changes
- **Intelligent Commit Messages**: Describes what was updated
- **Force Update**: Manual trigger option to force updates even without changes
- **Detailed Logging**: Provides clear logs of what happened

## Manual Usage

### Trigger Manual Update
1. Go to the **Actions** tab in your GitHub repository
2. Select **"Update Fork with Eddy-NG"** workflow
3. Click **"Run workflow"**
4. Optionally check **"Force update even if no changes"** if needed
5. Click **"Run workflow"**

### Monitor Results
- Check the **Actions** tab for workflow runs
- Each run provides a summary showing:
  - Whether upstream had updates
  - Whether eddy-ng had updates
  - Whether changes were committed
  - Current upstream hash
  - Trigger type (scheduled vs manual)

## Local Development

You can still work on the repository locally:

```bash
# Make your changes
git add .
git commit -m "Your changes"
git push origin main

# The automation will continue to work
# Your changes will be preserved during automated updates
```

## Troubleshooting

### Workflow Failures
If the workflow fails:
1. Check the **Actions** tab for error logs
2. Common issues:
   - Merge conflicts that couldn't be auto-resolved
   - Permission issues
   - Network connectivity problems

### Manual Recovery
If you need to manually fix issues:

```bash
# Clone your repository
git clone https://github.com/yourusername/your-klipper-fork.git
cd your-klipper-fork

# Add upstream remote
git remote add upstream https://github.com/Klipper3D/klipper.git

# Fetch all changes
git fetch --all

# Update eddy-ng
cd eddy-ng
git pull origin main
cd ..

# Manually merge if needed
git merge upstream/master

# Reinstall eddy-ng
python3 scripts/install_eddy_ng.py

# Commit and push
git add .
git commit -m "Manual fix after workflow failure"
git push origin main
```

### Disable Automation
To temporarily disable the automation:
1. Go to **Actions** tab
2. Select the workflow
3. Click **"Disable workflow"**
4. Re-enable when ready

## Files Involved

- `.github/workflows/update-fork.yml` - Main automation workflow
- `scripts/install_eddy_ng.py` - Repository installation script
- `scripts/install_eddy_ng.sh` - Shell wrapper for the installer
- `eddy-ng/` - Git submodule containing eddy-ng source code
- `FORK_AUTOMATION.md` - This documentation file

## Benefits

- **Stay Current**: Always have the latest Klipper features and fixes
- **Automatic Integration**: eddy-ng integration is maintained automatically
- **Conflict-Free**: Smart handling of merge conflicts
- **Transparent**: Clear logs and summaries of all changes
- **Flexible**: Manual override capability when needed

## Security Considerations

- Uses `GITHUB_TOKEN` for authentication (automatically provided)
- Commits are made by `github-actions[bot]`
- Only updates from trusted upstream sources:
  - Klipper3D/klipper (official Klipper repository)
  - vvuk/eddy-ng (specified eddy-ng repository) 