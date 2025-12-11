# Release Checklist

This document provides a step-by-step guide for creating a new LiteDesk release.

## Pre-Release Checklist

### 1. Code Preparation
- [ ] All features for the release are merged to main branch
- [ ] All tests pass
- [ ] No critical bugs or security issues
- [ ] Code review completed
- [ ] Documentation is up to date

### 2. Version Bump
- [ ] Update version in `setup.py`
- [ ] Update CHANGELOG.md (if exists) or create release notes
- [ ] Update README.md if needed

### 3. Testing
- [ ] Test on Windows (manual or CI)
- [ ] Test on macOS (manual or CI)
- [ ] Test on Linux (manual or CI)
- [ ] Test direct connection mode
- [ ] Test relay server mode
- [ ] Test NAT traversal

## Release Process

### Method 1: Automatic Release (Recommended)

#### Step 1: Create and Push Version Tag

```bash
# Ensure you're on the main branch and it's up to date
git checkout main
git pull origin main

# Create a version tag (use semantic versioning)
# Format: v<MAJOR>.<MINOR>.<PATCH>
git tag v1.0.0

# Push the tag to GitHub
git push origin v1.0.0
```

#### Step 2: GitHub Actions Automatically Builds

Once you push the tag, GitHub Actions will:
1. Build executables for Windows, macOS, and Linux
2. Create a GitHub Release draft
3. Upload all executables as release assets
4. Generate release notes

Progress can be monitored at:
`https://github.com/h123456001/litedesk/actions`

#### Step 3: Edit Release Notes (Optional)

1. Go to https://github.com/h123456001/litedesk/releases
2. Find your newly created release
3. Click "Edit release"
4. Add/modify release notes
5. Add highlights, breaking changes, or upgrade instructions
6. Click "Update release"

### Method 2: Manual Release

If you need to build manually:

#### Step 1: Build Locally

```bash
# On each platform (Windows, macOS, Linux)
git checkout v1.0.0
python build_all.py
```

This creates archives in the `release/` directory.

#### Step 2: Create GitHub Release

1. Go to https://github.com/h123456001/litedesk/releases
2. Click "Draft a new release"
3. Select the tag version (or create new tag)
4. Add release title (e.g., "LiteDesk v1.0.0")
5. Add release notes
6. Upload the build archives from `release/` directory
7. Click "Publish release"

## Release Notes Template

Use this template for release notes:

```markdown
## What's New in v1.0.0

### 🎉 New Features
- Feature 1
- Feature 2

### 🐛 Bug Fixes
- Fix 1
- Fix 2

### 🔧 Improvements
- Improvement 1
- Improvement 2

### 📦 Downloads

Choose the appropriate package for your platform:

- **Windows**: `litedesk-windows-x64.zip`
- **macOS Intel**: `litedesk-macos-x64.zip`
- **macOS Apple Silicon**: `litedesk-macos-arm64.zip`
- **Linux**: `litedesk-linux-x64.zip`

### 🚀 Installation

See [README.md](https://github.com/h123456001/litedesk/blob/main/README.md) for detailed installation instructions.

### ⚠️ Breaking Changes

List any breaking changes here.

### 🙏 Contributors

Thanks to all contributors!
```

## Post-Release Checklist

### 1. Verify Release
- [ ] Download and test Windows executable
- [ ] Download and test macOS executable
- [ ] Download and test Linux executable
- [ ] Verify all release assets are present
- [ ] Verify release notes are correct

### 2. Announcement
- [ ] Announce on project README
- [ ] Update project website (if exists)
- [ ] Announce on social media (if applicable)
- [ ] Notify users via email/newsletter (if applicable)

### 3. Documentation
- [ ] Update README badges with new version
- [ ] Update installation instructions if needed
- [ ] Link to latest release from README

### 4. Cleanup
- [ ] Close issues fixed in this release
- [ ] Update project board/milestones
- [ ] Plan next release

## Version Numbering (Semantic Versioning)

LiteDesk follows semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes or major new features
- **MINOR**: New features, backwards compatible
- **PATCH**: Bug fixes, backwards compatible

Examples:
- `v1.0.0` - Initial stable release
- `v1.1.0` - Add new feature (backwards compatible)
- `v1.1.1` - Bug fix
- `v2.0.0` - Breaking changes

## Troubleshooting Releases

### GitHub Actions Build Failed

1. Check the Actions tab for error details
2. Fix the issue in code
3. Delete the tag: `git tag -d v1.0.0 && git push origin :refs/tags/v1.0.0`
4. Create and push the tag again after fixing

### Release Assets Missing

1. Check GitHub Actions logs
2. Re-run failed jobs in Actions tab
3. If needed, manually build and upload assets

### Wrong Version Released

1. Delete the release on GitHub
2. Delete the tag: `git tag -d v1.0.0 && git push origin :refs/tags/v1.0.0`
3. Fix the version and create tag again

## Rollback a Release

If a critical bug is found:

1. Delete the release on GitHub (keeps the tag)
2. Fix the bug in code
3. Create a patch release (e.g., v1.0.1)
4. Follow the release process again

Or mark as pre-release:
1. Edit the release on GitHub
2. Check "This is a pre-release"
3. Add warning about the issue

## Testing Checklist Template

Copy and use this for each release:

```markdown
## Windows Testing
- [ ] Server starts successfully
- [ ] Client starts successfully
- [ ] Direct connection works
- [ ] Relay mode works
- [ ] Screen capture works
- [ ] Mouse control works
- [ ] Keyboard control works

## macOS Testing
- [ ] Server starts successfully
- [ ] Client starts successfully
- [ ] Direct connection works
- [ ] Relay mode works
- [ ] Screen capture works
- [ ] Mouse control works
- [ ] Keyboard control works
- [ ] Permissions prompt correctly

## Linux Testing
- [ ] Server starts successfully
- [ ] Client starts successfully
- [ ] Direct connection works
- [ ] Relay mode works
- [ ] Screen capture works
- [ ] Mouse control works
- [ ] Keyboard control works

## Relay Server Testing
- [ ] Starts on VPS
- [ ] Accepts connections
- [ ] Peer registration works
- [ ] Connection coordination works
```

## Helpful Commands

```bash
# List all tags
git tag -l

# Delete local tag
git tag -d v1.0.0

# Delete remote tag
git push origin :refs/tags/v1.0.0

# Create annotated tag with message
git tag -a v1.0.0 -m "Release version 1.0.0"

# View tag details
git show v1.0.0

# List releases using GitHub CLI
gh release list

# Create release using GitHub CLI
gh release create v1.0.0 ./release/*.zip --title "v1.0.0" --notes "Release notes"
```

## Resources

- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [GitHub Releases Documentation](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## Support

For questions about the release process:
- Review this checklist
- Check [BUILD.md](BUILD.md) for build details
- Check [GitHub Actions](.github/workflows/build-release.yml) configuration
- Open an issue on GitHub
