"""
Audit Logging System - Gold Tier

Centralized audit logging for all AI Employee actions.
Provides:
- Action tracking
- Decision logs
- Compliance reporting
- Security audit trail
"""

import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('audit_logger')

# Vault paths
VAULT_BASE = Path('vault')
AUDIT_PATH = VAULT_BASE / 'Audit'


class AuditLogger:
    """Centralized audit logging system"""
    
    def __init__(self):
        self.audit_path = AUDIT_PATH
        self.audit_path.mkdir(parents=True, exist_ok=True)
        
        # Configuration
        self.retention_days = int(os.getenv('AUDIT_RETENTION_DAYS', '90'))
        self.enable_compression = os.getenv('AUDIT_ENABLE_COMPRESSION', 'true').lower() == 'true'
        
    def _get_today_file(self) -> Path:
        """Get today's audit log file path"""
        return self.audit_path / f"audit_{datetime.now().strftime('%Y-%m-%d')}.json"
    
    def _load_daily_logs(self, date: datetime = None) -> List[dict]:
        """Load audit logs for a specific date"""
        if date is None:
            date = datetime.now()
        
        file_path = self.audit_path / f"audit_{date.strftime('%Y-%m-%d')}.json"
        
        if not file_path.exists():
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading audit file {file_path}: {str(e)}")
            return []
    
    def _save_daily_logs(self, logs: List[dict], date: datetime = None):
        """Save audit logs for a specific date"""
        if date is None:
            date = datetime.now()
        
        file_path = self.audit_path / f"audit_{date.strftime('%Y-%m-%d')}.json"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving audit file {file_path}: {str(e)}")
    
    def log(
        self,
        action: str,
        status: str,
        user: str = 'system',
        model: str = None,
        record_id: str = None,
        details: dict = None,
        ip_address: str = None,
        session_id: str = None
    ) -> dict:
        """
        Log an action to the audit trail.
        
        Args:
            action: Action name (e.g., 'send_email', 'create_invoice')
            status: 'success', 'failure', 'pending', 'rejected'
            user: User who performed the action
            model: Model affected (e.g., 'account.move', 'sale.order')
            record_id: Record ID in external system
            details: Additional details dictionary
            ip_address: IP address of the requester
            session_id: Session identifier
        
        Returns:
            dict: The created audit entry
        """
        
        entry = {
            'id': f"audit_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'status': status,
            'user': user,
            'model': model,
            'record_id': record_id,
            'details': details or {},
            'ip_address': ip_address,
            'session_id': session_id,
            'environment': {
                'hostname': os.getenv('COMPUTERNAME', 'unknown'),
                'user': os.getenv('USERNAME', 'unknown'),
                'python_version': os.sys.version
            }
        }
        
        # Add to today's logs
        logs = self._load_daily_logs()
        logs.append(entry)
        self._save_daily_logs(logs)
        
        logger.info(f"Audit log: {action} - {status} by {user}")
        
        return entry
    
    def log_action_start(self, action: str, user: str = 'system', **kwargs) -> dict:
        """Log the start of an action"""
        return self.log(
            action=action,
            status='pending',
            user=user,
            details={'stage': 'started', **kwargs}
        )
    
    def log_action_complete(
        self,
        action: str,
        result: dict,
        user: str = 'system',
        **kwargs
    ) -> dict:
        """Log the completion of an action"""
        status = 'success' if result.get('success', False) else 'failure'
        return self.log(
            action=action,
            status=status,
            user=user,
            details={'stage': 'completed', 'result': result, **kwargs}
        )
    
    def log_approval_decision(
        self,
        task_id: str,
        decision: str,
        user: str = 'system',
        reasoning: str = None
    ) -> dict:
        """Log an approval/rejection decision"""
        return self.log(
            action='approval_decision',
            status='success',
            user=user,
            model='task',
            record_id=task_id,
            details={
                'decision': decision,
                'reasoning': reasoning
            }
        )
    
    def log_error(
        self,
        action: str,
        error: str,
        user: str = 'system',
        stack_trace: str = None,
        **kwargs
    ) -> dict:
        """Log an error"""
        return self.log(
            action=action,
            status='failure',
            user=user,
            details={
                'stage': 'error',
                'error': error,
                'stack_trace': stack_trace,
                **kwargs
            }
        )
    
    def log_security_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        ip_address: str = None,
        user: str = None,
        **kwargs
    ) -> dict:
        """Log a security-related event"""
        return self.log(
            action=f"security_{event_type}",
            status='success',
            user=user or 'system',
            ip_address=ip_address,
            details={
                'security_event': True,
                'event_type': event_type,
                'severity': severity,
                'description': description,
                **kwargs
            }
        )
    
    def query(
        self,
        date_from: datetime = None,
        date_to: datetime = None,
        action: str = None,
        status: str = None,
        user: str = None,
        model: str = None,
        limit: int = 100
    ) -> List[dict]:
        """
        Query audit logs with filters.
        
        Args:
            date_from: Start date (default: 7 days ago)
            date_to: End date (default: today)
            action: Filter by action name
            status: Filter by status
            user: Filter by user
            model: Filter by model
            limit: Maximum results to return
        
        Returns:
            List of matching audit entries
        """
        
        if date_from is None:
            date_from = datetime.now() - timedelta(days=7)
        if date_to is None:
            date_to = datetime.now()
        
        results = []
        current_date = date_from
        
        while current_date <= date_to and len(results) < limit:
            logs = self._load_daily_logs(current_date)
            
            for entry in logs:
                # Apply filters
                if action and entry.get('action') != action:
                    continue
                if status and entry.get('status') != status:
                    continue
                if user and entry.get('user') != user:
                    continue
                if model and entry.get('model') != model:
                    continue
                
                results.append(entry)
                
                if len(results) >= limit:
                    break
            
            current_date += timedelta(days=1)
        
        return results
    
    def get_statistics(
        self,
        date_from: datetime = None,
        date_to: datetime = None
    ) -> dict:
        """Get audit log statistics"""
        
        logs = self.query(date_from=date_from, date_to=date_to, limit=10000)
        
        stats = {
            'total_entries': len(logs),
            'by_status': {},
            'by_action': {},
            'by_user': {},
            'success_rate': 0,
            'error_rate': 0
        }
        
        success_count = 0
        failure_count = 0
        
        for entry in logs:
            # Count by status
            status = entry.get('status', 'unknown')
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            
            # Count by action
            action = entry.get('action', 'unknown')
            stats['by_action'][action] = stats['by_action'].get(action, 0) + 1
            
            # Count by user
            user = entry.get('user', 'unknown')
            stats['by_user'][user] = stats['by_user'].get(user, 0) + 1
            
            # Count success/failure
            if status == 'success':
                success_count += 1
            elif status == 'failure':
                failure_count += 1
        
        total = success_count + failure_count
        if total > 0:
            stats['success_rate'] = round(success_count / total * 100, 2)
            stats['error_rate'] = round(failure_count / total * 100, 2)
        
        stats['period'] = {
            'from': date_from.isoformat() if date_from else None,
            'to': date_to.isoformat() if date_to else None
        }
        
        return stats
    
    def generate_compliance_report(
        self,
        report_type: str = 'daily',
        date: datetime = None
    ) -> dict:
        """
        Generate a compliance report.
        
        Args:
            report_type: 'daily', 'weekly', 'monthly'
            date: Report date (default: today)
        
        Returns:
            dict: Compliance report
        """
        
        if date is None:
            date = datetime.now()
        
        if report_type == 'daily':
            date_from = date
            date_to = date
        elif report_type == 'weekly':
            date_from = date - timedelta(days=date.weekday())
            date_to = date_from + timedelta(days=6)
        else:  # monthly
            date_from = date.replace(day=1)
            if date.month == 12:
                date_to = date.replace(year=date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                date_to = date.replace(month=date.month + 1, day=1) - timedelta(days=1)
        
        stats = self.get_statistics(date_from=date_from, date_to=date_to)
        logs = self.query(date_from=date_from, date_to=date_to, limit=1000)
        
        # Identify security events
        security_events = [
            e for e in logs
            if e.get('details', {}).get('security_event', False)
        ]
        
        # Identify failures
        failures = [e for e in logs if e.get('status') == 'failure']
        
        report = {
            'report_type': report_type,
            'period': {
                'from': date_from.strftime('%Y-%m-%d'),
                'to': date_to.strftime('%Y-%m-%d')
            },
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_actions': stats['total_entries'],
                'success_rate': stats['success_rate'],
                'total_failures': len(failures),
                'security_events': len(security_events)
            },
            'statistics': stats,
            'security_events': security_events[:20],  # First 20
            'failures': failures[:20],
            'recommendations': self._generate_recommendations(stats, failures, security_events)
        }
        
        return report
    
    def _generate_recommendations(
        self,
        stats: dict,
        failures: list,
        security_events: list
    ) -> list:
        """Generate recommendations based on audit data"""
        
        recommendations = []
        
        # Check error rate
        if stats.get('error_rate', 0) > 10:
            recommendations.append({
                'priority': 'high',
                'category': 'reliability',
                'message': f"Error rate is {stats['error_rate']}%. Investigate frequent failures."
            })
        
        # Check for security events
        if security_events:
            recommendations.append({
                'priority': 'high',
                'category': 'security',
                'message': f"{len(security_events)} security events detected. Review immediately."
            })
        
        # Check for high activity users
        if stats.get('by_user'):
            max_user = max(stats['by_user'].items(), key=lambda x: x[1])
            if max_user[1] > stats['total_entries'] * 0.8:
                recommendations.append({
                    'priority': 'medium',
                    'category': 'operations',
                    'message': f"User '{max_user[0]}' performed {max_user[1]} actions. Consider load distribution."
                })
        
        return recommendations
    
    def cleanup_old_logs(self, retention_days: int = None) -> int:
        """
        Remove audit logs older than retention period.
        
        Args:
            retention_days: Days to retain (default: from config)
        
        Returns:
            int: Number of files removed
        """
        
        if retention_days is None:
            retention_days = self.retention_days
        
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        removed_count = 0
        
        for file in self.audit_path.glob('audit_*.json'):
            try:
                # Extract date from filename
                date_str = file.stem.replace('audit_', '')
                file_date = datetime.strptime(date_str, '%Y-%m-%d')
                
                if file_date < cutoff_date:
                    # Compress instead of delete if enabled
                    if self.enable_compression:
                        self._compress_file(file)
                    else:
                        file.unlink()
                    removed_count += 1
                    logger.info(f"Cleaned up old audit log: {file.name}")
            except Exception as e:
                logger.error(f"Error processing {file}: {str(e)}")
        
        return removed_count
    
    def _compress_file(self, file_path: Path):
        """Compress an audit log file"""
        import gzip
        
        try:
            compressed_path = file_path.with_suffix('.json.gz')
            
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    f_out.writelines(f_in)
            
            file_path.unlink()
            logger.info(f"Compressed audit log: {file_path.name} -> {compressed_path.name}")
            
        except Exception as e:
            logger.error(f"Error compressing {file_path}: {str(e)}")
    
    def export_logs(
        self,
        output_path: str,
        date_from: datetime = None,
        date_to: datetime = None,
        format: str = 'json'
    ) -> dict:
        """
        Export audit logs to a file.
        
        Args:
            output_path: Output file path
            date_from: Start date
            date_to: End date
            format: 'json' or 'csv'
        
        Returns:
            dict: Export result
        """
        
        logs = self.query(date_from=date_from, date_to=date_to, limit=100000)
        
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            if format == 'json':
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(logs, f, indent=2, default=str)
            elif format == 'csv':
                import csv
                
                if not logs:
                    return {'success': False, 'error': 'No logs to export'}
                
                fieldnames = ['id', 'timestamp', 'action', 'status', 'user', 'model', 'record_id', 'details']
                
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for entry in logs:
                        writer.writerow({k: entry.get(k, '') for k in fieldnames})
            else:
                return {'success': False, 'error': f'Unsupported format: {format}'}
            
            return {
                'success': True,
                'message': f'Exported {len(logs)} logs to {output_path}',
                'count': len(logs)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}


# Global audit logger instance
audit_logger = AuditLogger()


def log_action(action: str, status: str, **kwargs) -> dict:
    """Convenience function to log an action"""
    return audit_logger.log(action, status, **kwargs)


def log_error(action: str, error: str, **kwargs) -> dict:
    """Convenience function to log an error"""
    return audit_logger.log_error(action, error, **kwargs)


def log_security_event(event_type: str, severity: str, description: str, **kwargs) -> dict:
    """Convenience function to log a security event"""
    return audit_logger.log_security_event(event_type, severity, description, **kwargs)


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Audit Logging System')
    parser.add_argument('--query', action='store_true', help='Query audit logs')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--report', choices=['daily', 'weekly', 'monthly'], help='Generate compliance report')
    parser.add_argument('--export', type=str, help='Export logs to file')
    parser.add_argument('--cleanup', action='store_true', help='Clean up old logs')
    parser.add_argument('--from', dest='date_from', type=str, help='From date (YYYY-MM-DD)')
    parser.add_argument('--to', dest='date_to', type=str, help='To date (YYYY-MM-DD)')
    parser.add_argument('--action', type=str, help='Filter by action')
    parser.add_argument('--status', type=str, help='Filter by status')
    
    args = parser.parse_args()
    
    logger = AuditLogger()
    
    # Parse dates
    date_from = None
    date_to = None
    
    if args.date_from:
        date_from = datetime.strptime(args.date_from, '%Y-%m-%d')
    if args.date_to:
        date_to = datetime.strptime(args.date_to, '%Y-%m-%d')
    
    if args.query:
        results = logger.query(
            date_from=date_from,
            date_to=date_to,
            action=args.action,
            status=args.status
        )
        print(json.dumps(results, indent=2, default=str))
    
    elif args.stats:
        stats = logger.get_statistics(date_from=date_from, date_to=date_to)
        print(json.dumps(stats, indent=2))
    
    elif args.report:
        report = logger.generate_compliance_report(args.report)
        print(json.dumps(report, indent=2, default=str))
    
    elif args.export:
        result = logger.export_logs(args.export, date_from=date_from, date_to=date_to)
        print(json.dumps(result, indent=2))
    
    elif args.cleanup:
        count = logger.cleanup_old_logs()
        print(f"Cleaned up {count} old audit log files")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
