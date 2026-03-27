"""
ETL Runner Module

Executes ETL extractors from the dashboard with progress tracking.
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime

def run_etl_extractor(extractor_name: str, project_root: Path) -> tuple[bool, str, str]:
    """
    Run a single ETL extractor script.
    
    Args:
        extractor_name: Name of extractor ('woocommerce', 'analytics', 'facebook')
        project_root: Path to project root directory
        
    Returns:
        Tuple of (success, stdout, stderr)
    """
    script_path = project_root / 'etl' / f'extract_{extractor_name}.py'
    
    if not script_path.exists():
        return False, "", f"Script not found: {script_path}"
    
    try:
        # Run the extractor script
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        success = result.returncode == 0
        return success, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        return False, "", "Timeout: Extractor took more than 5 minutes"
    except Exception as e:
        return False, "", f"Error executing extractor: {str(e)}"


def run_all_etl_extractors(project_root: Path = None) -> dict:
    """
    Run all configured ETL extractors.
    
    Args:
        project_root: Path to project root (auto-detected if None)
        
    Returns:
        Dict with results for each extractor
    """
    if project_root is None:
        project_root = Path(__file__).parent.parent
    
    # Check which extractors are configured
    from config.settings import check_configuration_status
    config_status = check_configuration_status()
    
    extractors = {
        'woocommerce': config_status.get('woocommerce', False),
        'analytics': config_status.get('google_analytics', False),
        'facebook': config_status.get('facebook', False)
    }
    
    results = {}
    
    for extractor_name, is_configured in extractors.items():
        if not is_configured:
            results[extractor_name] = {
                'status': 'skipped',
                'message': 'Not configured',
                'success': None,
                'timestamp': datetime.now().isoformat()
            }
            continue
        
        # Run extractor
        success, stdout, stderr = run_etl_extractor(extractor_name, project_root)
        
        results[extractor_name] = {
            'status': 'success' if success else 'error',
            'message': stderr if not success else 'Completed successfully',
            'success': success,
            'output': stdout[-500:] if stdout else '',  # Last 500 chars
            'timestamp': datetime.now().isoformat()
        }
    
    return results
