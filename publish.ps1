<#
Publish script for Windows (PowerShell).

Requirements:
- git installed
- optionally GitHub CLI (`gh`) for creating repo remotely

Usage:
  # Edit the variables below, or run interactively
  .\publish.ps1 -GitHubUser "your-username" -RepoName "cyberrecon-ai" -MakePublic

#>

param(
    [string]$GitHubUser,
    [string]$RepoName = "cyberrecon-ai",
    [switch]$MakePublic
)

if (-not $GitHubUser) {
    $GitHubUser = Read-Host "Enter your GitHub username"
}

$remote = "https://github.com/$GitHubUser/$RepoName.git"

if (-not (Test-Path .git)) {
    git init
    git add .
    git commit -m "chore: initial import"
}

if (Get-Command gh -ErrorAction SilentlyContinue) {
    Write-Host "Using GitHub CLI to create repo..."
    $visibility = $MakePublic.IsPresent ? "public" : "private"
    gh repo create $GitHubUser/$RepoName --$visibility --source=. --remote=origin --push
} else {
    Write-Host "gh CLI not found — adding remote and pushing manually."
    git remote add origin $remote
    git branch -M main
    git push -u origin main
}

Write-Host "Repository published to: $remote"
