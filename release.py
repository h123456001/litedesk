#!/usr/bin/env python3
"""
Release helper script for LiteDesk
Helps automate the release process
"""
import os
import sys
import subprocess
import re
from pathlib import Path


def run_command(cmd, capture_output=False):
    """Run a shell command"""
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        else:
            subprocess.run(cmd, shell=True, check=True)
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error: {e}")
        if capture_output and e.stderr:
            print(f"stderr: {e.stderr}")
        sys.exit(1)


def get_current_version():
    """Get current version from setup.py"""
    setup_py = Path('setup.py')
    if not setup_py.exists():
        print("Error: setup.py not found")
        sys.exit(1)
    
    content = setup_py.read_text()
    match = re.search(r'version="([^"]+)"', content)
    if match:
        return match.group(1)
    return None


def update_version(new_version):
    """Update version in setup.py"""
    setup_py = Path('setup.py')
    content = setup_py.read_text()
    content = re.sub(r'version="[^"]+"', f'version="{new_version}"', content)
    setup_py.write_text(content)
    print(f"✓ Updated version in setup.py to {new_version}")


def validate_version_format(version):
    """Validate semantic version format"""
    pattern = r'^\d+\.\d+\.\d+$'
    return re.match(pattern, version) is not None


def check_git_status():
    """Check if git working directory is clean"""
    status = run_command('git status --porcelain', capture_output=True)
    return len(status) == 0


def get_git_branch():
    """Get current git branch"""
    return run_command('git rev-parse --abbrev-ref HEAD', capture_output=True)


def create_release():
    """Interactive release creation"""
    print("=" * 60)
    print("LiteDesk Release Helper")
    print("=" * 60)
    
    # Check git status
    if not check_git_status():
        print("\n⚠ Warning: Working directory has uncommitted changes")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(0)
    
    # Check branch
    branch = get_git_branch()
    print(f"\nCurrent branch: {branch}")
    if branch != 'main' and branch != 'master':
        print("⚠ Warning: Not on main/master branch")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(0)
    
    # Get current version
    current_version = get_current_version()
    if current_version:
        print(f"Current version: {current_version}")
    else:
        print("Could not detect current version")
    
    # Get new version
    print("\nEnter new version number (e.g., 1.0.0)")
    new_version = input("New version: ").strip()
    
    if not validate_version_format(new_version):
        print("Error: Invalid version format. Use semantic versioning (X.Y.Z)")
        sys.exit(1)
    
    # Confirm
    print(f"\n{'='*60}")
    print("Release Summary:")
    print(f"{'='*60}")
    print(f"Current version: {current_version or 'unknown'}")
    print(f"New version: {new_version}")
    print(f"Tag: v{new_version}")
    print(f"{'='*60}")
    
    response = input("\nCreate this release? (y/N): ")
    if response.lower() != 'y':
        print("Aborted.")
        sys.exit(0)
    
    # Update version
    print("\nUpdating version...")
    update_version(new_version)
    
    # Commit version change
    print("Committing version change...")
    run_command('git add setup.py')
    run_command(f'git commit -m "Bump version to {new_version}"')
    
    # Create tag
    print(f"Creating tag v{new_version}...")
    run_command(f'git tag -a v{new_version} -m "Release version {new_version}"')
    
    # Push
    print("\nReady to push. This will:")
    print("1. Push the version commit")
    print("2. Push the tag (triggers GitHub Actions build)")
    print("3. GitHub Actions will create the release")
    
    response = input("\nPush now? (y/N): ")
    if response.lower() == 'y':
        print("\nPushing to GitHub...")
        run_command('git push origin')
        run_command(f'git push origin v{new_version}')
        
        print("\n" + "="*60)
        print("✓ Release process initiated!")
        print("="*60)
        print("\nNext steps:")
        print("1. Monitor GitHub Actions: https://github.com/h123456001/litedesk/actions")
        print("2. Once complete, edit release notes: https://github.com/h123456001/litedesk/releases")
        print("3. Test the released executables")
        print("4. Announce the release")
    else:
        print("\nNot pushed. To push manually:")
        print(f"  git push origin {branch}")
        print(f"  git push origin v{new_version}")


def undo_last_release():
    """Undo the last release (delete tag)"""
    print("=" * 60)
    print("Undo Last Release")
    print("=" * 60)
    
    # Get latest tag
    try:
        latest_tag = run_command('git describe --tags --abbrev=0', capture_output=True)
        print(f"\nLatest tag: {latest_tag}")
    except:
        print("\nNo tags found")
        sys.exit(1)
    
    response = input(f"Delete tag {latest_tag}? (y/N): ")
    if response.lower() != 'y':
        print("Aborted.")
        sys.exit(0)
    
    # Delete local tag
    print(f"Deleting local tag {latest_tag}...")
    run_command(f'git tag -d {latest_tag}')
    
    # Delete remote tag
    response = input("Delete remote tag as well? (y/N): ")
    if response.lower() == 'y':
        print(f"Deleting remote tag {latest_tag}...")
        run_command(f'git push origin :refs/tags/{latest_tag}')
        print("\n✓ Tag deleted locally and remotely")
        print("Note: You may need to manually delete the GitHub Release")
    else:
        print("\n✓ Local tag deleted")


def list_releases():
    """List all releases"""
    print("=" * 60)
    print("LiteDesk Releases")
    print("=" * 60)
    
    tags = run_command('git tag -l', capture_output=True)
    if tags:
        print("\nTags:")
        for tag in tags.split('\n'):
            print(f"  {tag}")
    else:
        print("\nNo tags found")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("LiteDesk Release Helper")
        print("\nUsage:")
        print("  python release.py create    - Create a new release")
        print("  python release.py undo      - Undo last release")
        print("  python release.py list      - List all releases")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'create':
        create_release()
    elif command == 'undo':
        undo_last_release()
    elif command == 'list':
        list_releases()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
