#!/bin/bash

# Squarest Notebook Simple - Deployment Script
# This script helps you deploy to GitHub and Render

echo "======================================"
echo "Squarest Notebook Simple - Deployment"
echo "======================================"

# Check if gh is authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ GitHub CLI not authenticated"
    echo ""
    echo "Please run: gh auth login"
    echo "Then run this script again"
    exit 1
fi

echo "✅ GitHub CLI authenticated"

# Check if repository already exists on GitHub
if git remote get-url origin &> /dev/null; then
    echo "⚠️  Remote origin already exists"
    echo "Pushing to existing repository..."
    git push -u origin main
else
    echo "Creating new GitHub repository..."
    gh repo create squarest-notebook-simple --public --push --source=.
fi

echo ""
echo "======================================"
echo "✅ Repository created/updated on GitHub!"
echo "======================================"
echo ""
echo "Next steps for Render deployment:"
echo ""
echo "1. Go to: https://dashboard.render.com"
echo "2. Click 'New +' -> 'Web Service'"
echo "3. Connect your GitHub account if not already connected"
echo "4. Select 'squarest-notebook-simple' repository"
echo "5. Use these settings:"
echo "   - Name: squarest-notebook-simple"
echo "   - Runtime: Docker"
echo "   - Instance Type: Free"
echo ""
echo "6. Add Environment Variables:"
echo "   - OPENAI_API_KEY: (your OpenAI API key)"
echo "   - ANTHROPIC_API_KEY: (optional)"
echo "   - GOOGLE_API_KEY: (optional)"
echo ""
echo "7. Click 'Create Web Service'"
echo ""
echo "Your app will be live in about 5 minutes!"
echo ""
echo "Repository URL: https://github.com/$(gh api user --jq .login)/squarest-notebook-simple"
