#!/bin/bash

# Script to enable GitHub Pages for the repository
# This script uses the GitHub CLI (gh) to configure Pages

echo "Enabling GitHub Pages for pan-config-viewer repository..."

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI (gh) is not installed. Please install it first:"
    echo "  brew install gh"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "Not authenticated with GitHub CLI. Please run:"
    echo "  gh auth login"
    exit 1
fi

# Enable GitHub Pages using GitHub API
echo "Configuring GitHub Pages..."
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/fahadysf/pan-config-viewer/pages \
  -f source='{"branch":"gh-pages","path":"/"}'

if [ $? -eq 0 ]; then
    echo "GitHub Pages has been enabled!"
    echo ""
    echo "Next steps:"
    echo "1. The GitHub Actions workflow will automatically build and deploy your docs"
    echo "2. Your documentation will be available at: https://fahadysf.github.io/pan-config-viewer"
    echo "3. The first deployment may take a few minutes"
    echo ""
    echo "To trigger the deployment manually, run:"
    echo "  gh workflow run deploy-docs.yml"
else
    echo "Failed to enable GitHub Pages. You may need to:"
    echo "1. Go to https://github.com/fahadysf/pan-config-viewer/settings/pages"
    echo "2. Under 'Source', select 'GitHub Actions'"
    echo "3. Save the settings"
fi