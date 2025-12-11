# Making Your First Release

Congratulations! The build system is ready. Here's how to create your first LiteDesk release.

## 🎯 Quick Start (TL;DR)

```bash
# After merging this PR to main:
git checkout main
git pull
python release.py create
# Follow the prompts, enter version (e.g., 1.0.0)
# GitHub Actions will automatically build and create the release
```

## 📋 Step-by-Step Guide

### Step 1: Merge This PR

1. Review the PR at: https://github.com/h123456001/litedesk/pulls
2. Ensure all checks pass (build test should be green)
3. Merge the PR to main branch

### Step 2: Prepare for Release

```bash
# Update your local repository
git checkout main
git pull origin main

# Verify everything is up to date
git status  # Should show "nothing to commit, working tree clean"
```

### Step 3: Create Release Tag

**Option A: Using the release helper (Recommended)**

```bash
# Run the interactive release helper
python release.py create

# It will ask you:
# - Confirm your branch is clean
# - Enter new version number (e.g., 1.0.0)
# - Confirm the release
# - Push to GitHub
```

**Option B: Manual process**

```bash
# Update version in setup.py (if needed)
# Edit setup.py and change version="1.0.0"

# Commit version change
git add setup.py
git commit -m "Bump version to 1.0.0"

# Create and push tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin main
git push origin v1.0.0
```

### Step 4: Monitor Build

1. Go to GitHub Actions: https://github.com/h123456001/litedesk/actions
2. You should see "Build and Release" workflow running
3. Wait for all jobs to complete (Windows, macOS, Linux builds)
4. This typically takes 15-30 minutes

### Step 5: Review Release

1. Once builds complete, go to: https://github.com/h123456001/litedesk/releases
2. You'll see a new release "v1.0.0" (or your version)
3. It will have:
   - `litedesk-windows-x64.zip`
   - `litedesk-macos-x64.zip`
   - `litedesk-linux-x64.zip`
4. Auto-generated release notes

### Step 6: Edit Release Notes (Optional)

1. Click "Edit release" on the release page
2. Enhance the release notes with:
   - Major features
   - Bug fixes
   - Breaking changes
   - Upgrade instructions
3. Use the template in RELEASE_CHECKLIST.md

Example:
```markdown
## 🎉 LiteDesk v1.0.0 - First Official Release

### What's New
- ✨ Pre-built executables for Windows, macOS, and Linux
- 🖥️ Remote desktop control with screen sharing
- 🌐 NAT traversal support via relay server
- 🎨 Cross-platform GUI with PyQt5

### 📦 Installation
Download the appropriate package for your system and extract it. 
No Python installation required!

### 🚀 Quick Start
See [QUICKSTART.md](https://github.com/h123456001/litedesk/blob/main/QUICKSTART.md)

### 🙏 Thanks
Thanks to all contributors!
```

### Step 7: Test the Release

Download and test each platform's executable:

**Windows:**
1. Download `litedesk-windows-x64.zip`
2. Extract it
3. Run `litedesk-server.exe`
4. Verify it starts without errors

**macOS:**
1. Download `litedesk-macos-x64.zip`
2. Extract it
3. Run `./litedesk-server`
4. Grant necessary permissions
5. Verify it works

**Linux:**
1. Download `litedesk-linux-x64.zip`
2. Extract it
3. Run `chmod +x litedesk-* && ./litedesk-server`
4. Verify it works

### Step 8: Announce

Once tested, announce your release:
- Update the README badges (if any)
- Tweet about it (if applicable)
- Post on forums/communities
- Update project website

## 🔄 For Subsequent Releases

The process is the same, just increment the version number:
- `v1.0.0` → `v1.0.1` (bug fixes)
- `v1.0.0` → `v1.1.0` (new features)
- `v1.0.0` → `v2.0.0` (breaking changes)

## 📝 Release Notes Template

For each release, consider including:

```markdown
## What's New in v1.x.x

### 🎉 New Features
- Feature 1
- Feature 2

### 🐛 Bug Fixes
- Fix 1
- Fix 2

### 🔧 Improvements
- Improvement 1
- Improvement 2

### ⚠️ Breaking Changes
- Change 1 (if any)

### 📦 Downloads
[See assets below]

### 🙏 Contributors
Thanks to @username1, @username2
```

## ❗ Troubleshooting

### Build Failed in GitHub Actions

1. Check the Actions tab for error details
2. Look at the failing job's logs
3. Common issues:
   - Missing dependencies
   - Python version mismatch
   - PyInstaller errors
4. Fix the issue, delete the tag, and try again:
   ```bash
   git tag -d v1.0.0
   git push origin :refs/tags/v1.0.0
   # Fix the issue, commit, then create tag again
   ```

### Release Not Created

1. Make sure the tag starts with 'v' (e.g., v1.0.0, not 1.0.0)
2. Check workflow permissions (should be set correctly)
3. Check GitHub Actions logs for errors

### Executables Don't Work

1. Test locally first using `python build_all.py`
2. Check PyInstaller logs for missing dependencies
3. Update the .spec files if needed
4. Create a new release with fixes

## 🎯 Best Practices

1. **Test Locally First**: Run `python build_all.py` before creating a tag
2. **Version Carefully**: Follow semantic versioning (MAJOR.MINOR.PATCH)
3. **Write Good Notes**: Clear release notes help users understand changes
4. **Test Downloads**: Always test the released executables
5. **Communicate**: Let users know about the release

## 📚 Resources

- **Release Helper**: `python release.py --help`
- **Build Docs**: See BUILD.md
- **Release Checklist**: See RELEASE_CHECKLIST.md
- **Architecture**: See ARCHITECTURE.md

## 🆘 Need Help?

If you encounter issues:
1. Check TROUBLESHOOTING.md
2. Review RELEASE_CHECKLIST.md
3. Check GitHub Actions logs
4. Review this guide again
5. Open an issue if stuck

## ✅ Success!

Once your first release is live:
- Users can download pre-built executables
- No Python installation required
- Automatic updates for future releases
- Professional software distribution

**Congratulations on your first release!** 🎊

---

*This guide is part of the LiteDesk build system implementation.*
*Created: December 11, 2024*
