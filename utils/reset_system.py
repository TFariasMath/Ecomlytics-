"""
System Reset Utility

This utility provides functionality to reset the analytics dashboard system
by cleaning databases, removing credentials, and creating backups.

Usage:
    python utils/reset_system.py [options]

Options:
    --dry-run           Preview what will be deleted without actually deleting
    --databases-only    Only reset databases (keep credentials)
    --credentials-only  Only reset credentials (keep databases)
    --no-backup         Skip backup creation (not recommended)
    --confirm           Skip interactive confirmations (use with caution)
    --quiet             Suppress non-error output
"""

import os
import sys
import shutil
import sqlite3
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import DatabaseConfig


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class SystemReset:
    """Handle system reset operations with backup and safety checks"""
    
    def __init__(self, dry_run: bool = False, quiet: bool = False):
        self.project_root = PROJECT_ROOT
        self.dry_run = dry_run
        self.quiet = quiet
        self.backup_dir: Optional[Path] = None
        
        # Define paths
        self.data_dir = self.project_root / 'data'
        self.env_file = self.project_root / '.env'
        self.env_example = self.project_root / '.env.example'
        self.backups_root = self.project_root / 'backups'
        
        # Database paths
        self.databases = {
            'WooCommerce': DatabaseConfig.get_woocommerce_db_path(),
            'Analytics': DatabaseConfig.get_analytics_db_path(),
            'Facebook': DatabaseConfig.get_facebook_db_path(),
            'Monitoring': DatabaseConfig.get_monitoring_db_path()
        }
        
        # Statistics
        self.stats = {
            'files_backed_up': 0,
            'databases_cleaned': 0,
            'credentials_reset': 0,
            'json_keys_removed': 0
        }
    
    def log(self, message: str, color: str = '', bold: bool = False):
        """Print colored log message"""
        if self.quiet:
            return
        
        prefix = f"{Colors.BOLD}" if bold else ""
        suffix = f"{Colors.ENDC}"
        try:
            print(f"{prefix}{color}{message}{suffix}")
        except UnicodeEncodeError:
            # Fallback for Windows console encoding issues
            # Remove color codes and print as plain text
            print(message.encode('ascii', errors='replace').decode('ascii'))
    
    def log_error(self, message: str):
        """Print error message"""
        print(f"{Colors.FAIL}{Colors.BOLD}ERROR: {message}{Colors.ENDC}", file=sys.stderr)
    
    def log_warning(self, message: str):
        """Print warning message"""
        if not self.quiet:
            print(f"{Colors.WARNING}WARNING: {message}{Colors.ENDC}")
    
    def log_success(self, message: str):
        """Print success message"""
        if not self.quiet:
            print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")
    
    def create_backup(self) -> bool:
        """
        Create backup of all databases and credentials
        
        Returns:
            True if backup successful, False otherwise
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_dir = self.backups_root / f'reset_{timestamp}'
        
        self.log(f"\n{Colors.BOLD}Creating backup...{Colors.ENDC}")
        
        if self.dry_run:
            self.log(f"[DRY RUN] Would create backup at: {self.backup_dir}", Colors.OKCYAN)
            return True
        
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup databases
            for name, db_path in self.databases.items():
                db_file = Path(db_path)
                if db_file.exists():
                    backup_path = self.backup_dir / db_file.name
                    shutil.copy2(db_file, backup_path)
                    self.stats['files_backed_up'] += 1
                    self.log(f"  Backed up {name} database", Colors.OKBLUE)
            
            # Backup .env file
            if self.env_file.exists():
                backup_env = self.backup_dir / '.env'
                shutil.copy2(self.env_file, backup_env)
                self.stats['files_backed_up'] += 1
                self.log(f"  Backed up .env file", Colors.OKBLUE)
            
            # Backup Google Analytics JSON keys
            json_files = self._find_ga_json_files()
            if json_files:
                for json_file in json_files:
                    backup_path = self.backup_dir / json_file.name
                    shutil.copy2(json_file, backup_path)
                    self.stats['files_backed_up'] += 1
                    self.log(f"  Backed up {json_file.name}", Colors.OKBLUE)
            
            self.log_success(f"Backup created at: {self.backup_dir}")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to create backup: {e}")
            return False
    
    def _find_ga_json_files(self) -> List[Path]:
        """Find all Google Analytics service account JSON files"""
        json_files = []
        
        # Look in project root
        for file in self.project_root.glob('*.json'):
            # Skip certain files
            if file.name not in ['package.json', 'tsconfig.json']:
                # Basic check if it looks like a service account key
                try:
                    import json
                    with open(file, 'r') as f:
                        data = json.load(f)
                        if 'type' in data and data.get('type') == 'service_account':
                            json_files.append(file)
                except Exception:
                    pass
        
        return json_files
    
    def clean_databases(self, specific_dbs: Optional[List[str]] = None) -> bool:
        """
        Clean or delete database files
        
        Args:
            specific_dbs: List of database names to clean. If None, clean all.
        
        Returns:
            True if successful, False otherwise
        """
        self.log(f"\n{Colors.BOLD}Cleaning databases...{Colors.ENDC}")
        
        try:
            dbs_to_clean = self.databases if specific_dbs is None else {
                k: v for k, v in self.databases.items() if k in specific_dbs
            }
            
            for name, db_path in dbs_to_clean.items():
                db_file = Path(db_path)
                
                if not db_file.exists():
                    self.log(f"  {name}: Not found (skipping)", Colors.WARNING)
                    continue
                
                if self.dry_run:
                    self.log(f"  [DRY RUN] Would delete {name} database", Colors.OKCYAN)
                    continue
                
                # Delete the database file
                db_file.unlink()
                self.stats['databases_cleaned'] += 1
                self.log_success(f"{name} database deleted")
            
            return True
            
        except Exception as e:
            self.log_error(f"Failed to clean databases: {e}")
            return False
    
    def reset_credentials(self) -> bool:
        """
        Reset .env file to template state
        
        Returns:
            True if successful, False otherwise
        """
        self.log(f"\n{Colors.BOLD}Resetting credentials...{Colors.ENDC}")
        
        if not self.env_example.exists():
            self.log_warning(".env.example not found. Creating basic template.")
            template_content = """# ========================================
# CONFIGURACIÓN DE CREDENCIALES
# ========================================
# Completa con tus credenciales reales

# WOOCOMMERCE API
WC_URL=https://tu-tienda.com
WC_CONSUMER_KEY=ck_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WC_CONSUMER_SECRET=cs_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# GOOGLE ANALYTICS 4
GA4_KEY_FILE=your-service-account-key.json
GA4_PROPERTY_ID=123456789

# FACEBOOK PAGE INSIGHTS
FB_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
FB_PAGE_ID=1234567890123456
FB_API_VERSION=v19.0
"""
        else:
            with open(self.env_example, 'r', encoding='utf-8') as f:
                template_content = f.read()
        
        if self.dry_run:
            self.log(f"[DRY RUN] Would reset .env file to template", Colors.OKCYAN)
            return True
        
        try:
            with open(self.env_file, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            self.stats['credentials_reset'] += 1
            self.log_success(".env file reset to template")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to reset credentials: {e}")
            return False
    
    def remove_json_keys(self) -> bool:
        """
        Remove Google Analytics service account JSON files
        
        Returns:
            True if successful, False otherwise
        """
        self.log(f"\n{Colors.BOLD}Removing Google Analytics JSON keys...{Colors.ENDC}")
        
        json_files = self._find_ga_json_files()
        
        if not json_files:
            self.log("  No JSON key files found", Colors.OKBLUE)
            return True
        
        try:
            for json_file in json_files:
                if self.dry_run:
                    self.log(f"  [DRY RUN] Would delete {json_file.name}", Colors.OKCYAN)
                else:
                    json_file.unlink()
                    self.stats['json_keys_removed'] += 1
                    self.log_success(f"Removed {json_file.name}")
            
            return True
            
        except Exception as e:
            self.log_error(f"Failed to remove JSON keys: {e}")
            return False
    
    def get_reset_summary(self) -> Dict[str, List[str]]:
        """
        Get summary of what will be reset
        
        Returns:
            Dictionary with categories and items to be reset
        """
        summary = {
            'databases': [],
            'credentials': [],
            'json_keys': []
        }
        
        # Check databases
        for name, db_path in self.databases.items():
            if Path(db_path).exists():
                size = Path(db_path).stat().st_size
                size_mb = size / (1024 * 1024)
                summary['databases'].append(f"{name} ({size_mb:.2f} MB)")
        
        # Check .env
        if self.env_file.exists():
            summary['credentials'].append(".env file")
        
        # Check JSON keys
        json_files = self._find_ga_json_files()
        for json_file in json_files:
            summary['json_keys'].append(json_file.name)
        
        return summary
    
    def print_summary(self, summary: Dict[str, List[str]]):
        """Print reset summary"""
        self.log(f"\n{Colors.BOLD}{Colors.HEADER}{'='*50}{Colors.ENDC}")
        self.log(f"{Colors.BOLD}{Colors.HEADER}       SYSTEM RESET SUMMARY{Colors.ENDC}")
        self.log(f"{Colors.BOLD}{Colors.HEADER}{'='*50}{Colors.ENDC}\n")
        
        if summary['databases']:
            self.log(f"{Colors.BOLD}Databases to be deleted:{Colors.ENDC}")
            for item in summary['databases']:
                self.log(f"  • {item}", Colors.FAIL)
        else:
            self.log(f"Databases: {Colors.OKGREEN}None found{Colors.ENDC}")
        
        if summary['credentials']:
            self.log(f"\n{Colors.BOLD}Credentials to be reset:{Colors.ENDC}")
            for item in summary['credentials']:
                self.log(f"  • {item}", Colors.WARNING)
        else:
            self.log(f"\nCredentials: {Colors.OKGREEN}None found{Colors.ENDC}")
        
        if summary['json_keys']:
            self.log(f"\n{Colors.BOLD}JSON keys to be removed:{Colors.ENDC}")
            for item in summary['json_keys']:
                self.log(f"  • {item}", Colors.WARNING)
        else:
            self.log(f"\nJSON keys: {Colors.OKGREEN}None found{Colors.ENDC}")
        
        if self.dry_run:
            self.log(f"\n{Colors.OKCYAN}{Colors.BOLD}This is a DRY RUN - no files will be deleted{Colors.ENDC}")
    
    def print_stats(self):
        """Print final statistics"""
        self.log(f"\n{Colors.BOLD}{Colors.OKGREEN}{'='*50}{Colors.ENDC}")
        self.log(f"{Colors.BOLD}{Colors.OKGREEN}         RESET COMPLETE{Colors.ENDC}")
        self.log(f"{Colors.BOLD}{Colors.OKGREEN}{'='*50}{Colors.ENDC}\n")
        
        self.log(f"Statistics:")
        self.log(f"  • Files backed up: {self.stats['files_backed_up']}", Colors.OKBLUE)
        self.log(f"  • Databases cleaned: {self.stats['databases_cleaned']}", Colors.OKBLUE)
        self.log(f"  • Credentials reset: {self.stats['credentials_reset']}", Colors.OKBLUE)
        self.log(f"  • JSON keys removed: {self.stats['json_keys_removed']}", Colors.OKBLUE)
        
        if self.backup_dir and not self.dry_run:
            self.log(f"\n{Colors.BOLD}Backup location:{Colors.ENDC} {self.backup_dir}", Colors.OKCYAN)


def confirm_action(message: str) -> bool:
    """Ask user for confirmation"""
    response = input(f"{Colors.WARNING}{message} (yes/no): {Colors.ENDC}").strip().lower()
    return response in ['yes', 'y']


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Reset analytics dashboard system (databases and credentials)',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview what will be deleted without actually deleting')
    parser.add_argument('--databases-only', action='store_true',
                       help='Only reset databases (keep credentials)')
    parser.add_argument('--credentials-only', action='store_true',
                       help='Only reset credentials (keep databases)')
    parser.add_argument('--no-backup', action='store_true',
                       help='Skip backup creation (not recommended)')
    parser.add_argument('--confirm', action='store_true',
                       help='Skip interactive confirmations (use with caution)')
    parser.add_argument('--quiet', action='store_true',
                       help='Suppress non-error output')
    
    args = parser.parse_args()
    
    # Create reset instance
    reset = SystemReset(dry_run=args.dry_run, quiet=args.quiet)
    
    # Print banner
    if not args.quiet:
        reset.log(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
        reset.log(f"{Colors.BOLD}{Colors.HEADER}   Analytics Dashboard - System Reset Utility{Colors.ENDC}")
        reset.log(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
    
    # Get and print summary
    summary = reset.get_reset_summary()
    reset.print_summary(summary)
    
    # Check if there's anything to reset
    has_items = any(summary.values())
    if not has_items:
        reset.log(f"\n{Colors.OKGREEN}Nothing to reset. System is already clean.{Colors.ENDC}")
        return 0
    
    # Confirm action
    if not args.confirm and not args.dry_run:
        reset.log(f"\n{Colors.BOLD}{Colors.FAIL}⚠️  WARNING: This action cannot be undone!{Colors.ENDC}")
        if not confirm_action("Are you sure you want to proceed?"):
            reset.log("Reset cancelled.")
            return 0
    
    # Create backup (unless --no-backup or --dry-run)
    if not args.no_backup:
        if not reset.create_backup():
            reset.log_error("Backup failed. Aborting reset for safety.")
            return 1
    else:
        reset.log_warning("Skipping backup creation (--no-backup flag)")
    
    # Perform reset operations
    success = True
    
    if not args.credentials_only:
        success = reset.clean_databases() and success
    
    if not args.databases_only:
        success = reset.reset_credentials() and success
        success = reset.remove_json_keys() and success
    
    # Print final statistics
    if not args.dry_run:
        reset.print_stats()
    else:
        reset.log(f"\n{Colors.OKCYAN}{Colors.BOLD}DRY RUN COMPLETE - No files were actually deleted{Colors.ENDC}")
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
