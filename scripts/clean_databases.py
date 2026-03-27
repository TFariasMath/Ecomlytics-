"""
Database Cleanup Script

IMPORTANT: This script will DELETE ALL DATA from the databases.
Only run this if you want to clean sensitive production data and start fresh.

Creates empty database structures ready for new data extraction.
"""

import sqlite3
import os
import shutil
from datetime import datetime

# Database paths
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
BACKUP_DIR = os.path.join(os.path.dirname(__file__), '..', 'backups')

DATABASES = {
    'woocommerce.db': [
        'wc_orders',
        'wc_order_items',
        'wc_products',
        'wc_customers'
    ],
    'analytics.db': [
        'ga4_ecommerce',
        'ga4_traffic_sources',
        'ga4_user_behavior'
    ],
    'facebook.db': [
        'fb_page_insights'
    ],
    'monitoring.db': [
        'etl_executions'
    ]
}


def create_backup(db_name):
    """Create backup of database before cleaning"""
    source = os.path.join(DATA_DIR, db_name)
    
    if not os.path.exists(source):
        print(f"⚠️  {db_name} does not exist, skipping backup")
        return False
    
    # Create backup directory
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Create timestamped backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"{db_name.replace('.db', '')}_{timestamp}.db"
    destination = os.path.join(BACKUP_DIR, backup_name)
    
    shutil.copy2(source, destination)
    print(f"✅ Backup created: {backup_name}")
    return True


def get_table_count(cursor, table_name):
    """Get row count from table"""
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        return cursor.fetchone()[0]
    except sqlite3.OperationalError:
        return 0


def clean_database(db_name, tables):
    """Clean all tables in a database"""
    db_path = os.path.join(DATA_DIR, db_name)
    
    if not os.path.exists(db_path):
        print(f"\n⚠️  {db_name} does not exist, skipping")
        return
    
    print(f"\n📊 Cleaning {db_name}...")
    
    # Create backup first
    create_backup(db_name)
    
    # Connect and clean
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    total_rows_deleted = 0
    
    for table in tables:
        # Get current count
        count = get_table_count(cursor, table)
        
        if count > 0:
            # Delete all rows
            cursor.execute(f"DELETE FROM {table}")
            print(f"  🗑️  {table}: {count:,} rows deleted")
            total_rows_deleted += count
        else:
            print(f"  ⚪ {table}: already empty")
    
    # Commit changes
    conn.commit()
    
    # Vacuum to reclaim space
    print(f"  🔧 Vacuuming database...")
    cursor.execute("VACUUM")
    
    conn.close()
    
    print(f"✅ {db_name}: {total_rows_deleted:,} total rows deleted")


def main():
    """Main cleanup function"""
    print("=" * 60)
    print("🔒 DATABASE CLEANUP SCRIPT")
    print("=" * 60)
    print("\n⚠️  WARNING: This will DELETE ALL DATA from databases!")
    print("⚠️  Backups will be created in backups/ directory")
    print("\nDatabases to clean:")
    
    for db_name in DATABASES.keys():
        db_path = os.path.join(DATA_DIR, db_name)
        if os.path.exists(db_path):
            size_mb = os.path.getsize(db_path) / (1024 * 1024)
            print(f"  - {db_name} ({size_mb:.2f} MB)")
    
    print("\n" + "=" * 60)
    response = input("\nAre you sure you want to continue? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("\n❌ Cleanup cancelled")
        return
    
    print("\n🚀 Starting cleanup...\n")
    
    # Clean each database
    for db_name, tables in DATABASES.items():
        clean_database(db_name, tables)
    
    print("\n" + "=" * 60)
    print("✅ CLEANUP COMPLETE!")
    print("=" * 60)
    print("\n📁 Backups saved in: backups/")
    print("\n🔄 Next steps:")
    print("  1. Run ETL extractors to populate with new data")
    print("  2. Verify configuration in .env file")
    print("  3. Check dashboard displays correctly")
    print("\nCommands:")
    print("  python etl/extract_woocommerce.py")
    print("  python etl/extract_analytics.py")
    print("  python etl/extract_facebook.py")


if __name__ == "__main__":
    main()
