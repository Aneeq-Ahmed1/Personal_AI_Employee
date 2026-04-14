"""
Utility functions for retry logic, health checks, and service monitoring
"""

import time
import logging
import requests
from typing import Callable, Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path
import json

logger = logging.getLogger(__name__)


def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 2.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    *args,
    **kwargs
) -> Any:
    """
    Execute function with exponential backoff retry logic
    
    Args:
        func: Function to execute
        max_retries: Maximum number of retries
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential calculation
        jitter: Add random jitter to delay
        *args: Positional arguments for function
        **kwargs: Keyword arguments for function
        
    Returns:
        Function result
        
    Raises:
        Last exception if all retries fail
    """
    import random
    
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            
            if attempt < max_retries - 1:
                # Calculate delay with exponential backoff
                delay = min(base_delay * (exponential_base ** attempt), max_delay)
                
                # Add jitter to prevent thundering herd
                if jitter:
                    delay = delay * (0.5 + random.random() * 0.5)
                
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}. "
                    f"Retrying in {delay:.2f}s..."
                )
                time.sleep(delay)
            else:
                logger.error(f"All {max_retries} attempts failed. Last error: {str(e)}")
    
    raise last_exception


class ServiceHealthChecker:
    """Check health status of all services"""
    
    def __init__(self):
        self.services = {
            'dashboard_frontend': {
                'url': 'http://localhost:3000',
                'name': 'Next.js Dashboard',
                'port': 3000
            },
            'dashboard_api': {
                'url': 'http://localhost:8000/health',
                'name': 'Dashboard API',
                'port': 8000
            },
            'odoo_mcp': {
                'url': 'http://localhost:5001/health',
                'name': 'Odoo MCP Server',
                'port': 5001
            },
            'social_media_mcp': {
                'url': 'http://localhost:5002/health',
                'name': 'Social Media MCP Server',
                'port': 5002
            },
            'odoo': {
                'url': 'http://localhost:8069',
                'name': 'Odoo 19',
                'port': 8069
            }
        }
    
    def check_service(self, service_key: str) -> Dict[str, Any]:
        """Check individual service health"""
        service = self.services.get(service_key)
        if not service:
            return {
                'name': service_key,
                'status': 'unknown',
                'error': 'Service not configured'
            }
        
        try:
            response = requests.get(service['url'], timeout=5)
            
            if response.status_code == 200:
                return {
                    'name': service['name'],
                    'port': service['port'],
                    'status': 'healthy',
                    'response_time_ms': int(response.elapsed.total_seconds() * 1000),
                    'status_code': response.status_code
                }
            else:
                return {
                    'name': service['name'],
                    'port': service['port'],
                    'status': 'degraded',
                    'status_code': response.status_code,
                    'response_time_ms': int(response.elapsed.total_seconds() * 1000)
                }
                
        except requests.exceptions.ConnectionError:
            return {
                'name': service['name'],
                'port': service['port'],
                'status': 'unreachable',
                'error': 'Connection refused'
            }
        except requests.exceptions.Timeout:
            return {
                'name': service['name'],
                'port': service['port'],
                'status': 'timeout',
                'error': 'Request timed out'
            }
        except Exception as e:
            return {
                'name': service['name'],
                'port': service['port'],
                'status': 'error',
                'error': str(e)
            }
    
    def check_all_services(self) -> Dict[str, Any]:
        """Check all services and return summary"""
        results = {}
        healthy_count = 0
        total_count = len(self.services)
        
        for service_key in self.services.keys():
            results[service_key] = self.check_service(service_key)
            if results[service_key]['status'] == 'healthy':
                healthy_count += 1
        
        return {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy' if healthy_count == total_count else 'degraded',
            'healthy_services': healthy_count,
            'total_services': total_count,
            'services': results
        }
    
    def generate_report(self) -> str:
        """Generate human-readable health report"""
        health = self.check_all_services()
        
        report = []
        report.append("=" * 60)
        report.append("SERVICE HEALTH CHECK REPORT")
        report.append("=" * 60)
        report.append(f"Timestamp: {health['timestamp']}")
        report.append(f"Overall Status: {health['overall_status'].upper()}")
        report.append(f"Healthy Services: {health['healthy_services']}/{health['total_services']}")
        report.append("-" * 60)
        
        for service_key, service_data in health['services'].items():
            status_icon = {
                'healthy': '✅',
                'degraded': '⚠️',
                'unreachable': '❌',
                'timeout': '⏰',
                'error': '❌'
            }.get(service_data['status'], '❓')
            
            report.append(f"{status_icon} {service_data['name']} (Port {service_data['port']})")
            report.append(f"   Status: {service_data['status']}")
            
            if 'response_time_ms' in service_data:
                report.append(f"   Response Time: {service_data['response_time_ms']}ms")
            
            if 'error' in service_data:
                report.append(f"   Error: {service_data['error']}")
            
            report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)


class VaultStatsChecker:
    """Check vault statistics"""
    
    def __init__(self, vault_path: str = None):
        if vault_path:
            self.vault_path = Path(vault_path)
        else:
            self.vault_path = Path(__file__).parent.parent / 'vault'
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vault statistics"""
        stats = {
            'inbox': 0,
            'needs_action': 0,
            'plans': 0,
            'completed': 0,
            'approvals': 0,
            'total_files': 0
        }
        
        directories = {
            'inbox': self.vault_path / 'Inbox',
            'needs_action': self.vault_path / 'Needs_Action',
            'plans': self.vault_path / 'Plans',
            'completed': self.vault_path / 'Completed',
            'approvals': self.vault_path / 'Approvals'
        }
        
        for key, dir_path in directories.items():
            if dir_path.exists():
                count = len(list(dir_path.glob('*.md')))
                stats[key] = count
                stats['total_files'] += count
        
        return stats


def create_health_endpoint():
    """Create health check endpoint data"""
    checker = ServiceHealthChecker()
    vault_stats = VaultStatsChecker()
    
    return {
        'services': checker.check_all_services(),
        'vault': vault_stats.get_stats(),
        'timestamp': datetime.now().isoformat()
    }


if __name__ == '__main__':
    # Test health checker
    checker = ServiceHealthChecker()
    report = checker.generate_report()
    print(report)
    
    # Save report
    report_file = Path(__file__).parent.parent / 'vault' / 'Logs' / f"health_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\nReport saved to: {report_file}")
