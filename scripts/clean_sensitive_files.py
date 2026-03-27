"""
Security Cleanup Script - Remove Sensitive Files

This script helps clean up sensitive data from the project:
1. Removes test files with hardcoded tokens
2. Backs up and removes credential files
3. Reports on sensitive data locations

IMPORTANT: Creates backups before deletion
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Files and patterns to check
SENSITIVE_FILES = {
    'test_fb_token.py': 'Test file with exposed Facebook token',
    'config/credentials/*.json': 'Google Cloud service account keys',
}

SENSITIVE_DIRS = [
    'config/credentials',
]


def create_backup(file_path, backup_dir):
    """Create timestamped backup of file"""
    if not os.path.exists(file_path):
        return None
    
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_name = os.path.basename(file_path)
    backup_name = f"{timestamp}_{file_name}"
    backup_path = os.path.join(backup_dir, backup_name)
    
    shutil.copy2(file_path, backup_path)
    return backup_path


def check_file_exists(pattern):
    """Check if files matching pattern exist"""
    if '*' in pattern:
        # Handle glob patterns
        from glob import glob
        matches = glob(str(PROJECT_ROOT / pattern))
        return matches
    else:
        path = PROJECT_ROOT / pattern
        return [str(path)] if path.exists() else []


def main():
    """Main security cleanup"""
    print("=" * 70)
    print("🔒 SECURITY CLEANUP SCRIPT")
    print("=" * 70)
    
    backup_dir = PROJECT_ROOT / 'security_backups' / datetime.now().strftime('%Y%m%d_%H%M%S')
    
    print(f"\n📁 Backups will be saved to: {backup_dir}\n")
    
    found_files = []
    
    # Check for sensitive files
    print("🔍 Scanning for sensitive files...\n")
    
    for pattern, description in SENSITIVE_FILES.items():
        matches = check_file_exists(pattern)
        
        if matches:
            print(f"⚠️  Found: {pattern}")
            print(f"   Description: {description}")
            print(f"   Files:")
            for match in matches:
                size = os.path.getsize(match) / 1024
                print(f"     - {os.path.basename(match)} ({size:.2f} KB)")
                found_files.append((match, description))
            print()
    
    if not found_files:
        print("✅ No sensitive files found in standard locations")
        return
    
    print("=" * 70)
    print(f"\n⚠️  Found {len(found_files)} sensitive file(s)")
    print("\nActions:")
    print("  1. Create backups in security_backups/")
    print("  2. Remove original files")
    print("  3. Generate security report")
    
    response = input("\nProceed with cleanup? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("\n❌ Cleanup cancelled")
        print("\n⚠️  SECURITY REMINDER:")
        print("   - These files contain sensitive credentials")
        print("   - Do NOT commit them to version control")
        print("   - Consider revoking exposed credentials")
        return
    
    print("\n🚀 Starting cleanup...\n")
    
    removed_count = 0
    backed_up_count = 0
    
    for file_path, description in found_files:
        file_name = os.path.basename(file_path)
        
        # Create backup
        backup_path = create_backup(file_path, str(backup_dir))
        if backup_path:
            print(f"✅ Backed up: {file_name}")
            backed_up_count += 1
        
        # Remove original
        try:
            os.remove(file_path)
            print(f"🗑️  Removed: {file_name}")
            removed_count += 1
        except Exception as e:
            print(f"❌ Error removing {file_name}: {e}")
    
    print("\n" + "=" * 70)
    print("✅ CLEANUP COMPLETE")
    print("=" * 70)
    print(f"\n📊 Summary:")
    print(f"  - Files backed up: {backed_up_count}")
    print(f"  - Files removed: {removed_count}")
    print(f"  - Backup location: {backup_dir}")
    
    print(f"\n⚠️  IMPORTANT NEXT STEPS:")
    print("\n1. **Revoke Exposed Credentials:**")
    print("   - Facebook: https://developers.facebook.com/ > App Settings > Access Tokens")
    print("   - Google Cloud: https://console.cloud.google.com/ > IAM > Service Accounts")
    
    print("\n2. **Generate New Credentials:**")
    print("   - Follow SETUP_GUIDE.md for each service")
    print("   - Store in .env file (already gitignored)")
    
    print("\n3. **Verify .gitignore:**")
    print("   - Ensure .env is listed")
    print("   - Check *.json is excluded (except specific files)")
    print("   - Run: git status --ignored")
    
    print("\n4. **If Repository is Public:**")
    print("   - Review git history for exposed credentials")
    print("   - Consider using BFG Repo-Cleaner or git-filter-repo")
    print("   - Rotate ALL credentials as precaution")


if __name__ == "__main__":
    main()
