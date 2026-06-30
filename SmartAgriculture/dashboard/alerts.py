"""
Alert Management Module for Smart Agriculture Dashboard
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertType(Enum):
    """Alert types"""
    TEMPERATURE_HIGH = "temperature_high"
    TEMPERATURE_LOW = "temperature_low"
    HUMIDITY_LOW = "humidity_low"
    HUMIDITY_HIGH = "humidity_high"
    SOIL_MOISTURE_LOW = "soil_moisture_low"
    SOIL_MOISTURE_HIGH = "soil_moisture_high"
    PH_HIGH = "ph_high"
    PH_LOW = "ph_low"
    LIGHT_LOW = "light_low"
    LIGHT_HIGH = "light_high"
    SENSOR_OFFLINE = "sensor_offline"
    ANOMALY_DETECTED = "anomaly_detected"


@dataclass
class Alert:
    """Alert data structure"""
    alert_id: str
    alert_type: AlertType
    severity: AlertSeverity
    sensor_id: str
    sensor_type: str
    message: str
    value: float
    threshold: float
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AlertManager:
    """Manage alerts for the dashboard"""
    
    def __init__(self):
        """Initialize alert manager"""
        self.alerts: List[Alert] = []
        self.alert_rules: Dict[AlertType, Dict] = {}
        self.notification_handlers: List[Callable] = []
        self._load_default_rules()
        
    def _load_default_rules(self):
        """Load default alert rules"""
        self.alert_rules = {
            AlertType.TEMPERATURE_HIGH: {
                'sensor_type': 'temperature',
                'condition': lambda x: x > 35,
                'severity': AlertSeverity.CRITICAL,
                'message': 'High temperature detected: {value:.1f}°C (threshold: {threshold}°C)'
            },
            AlertType.TEMPERATURE_LOW: {
                'sensor_type': 'temperature',
                'condition': lambda x: x < 10,
                'severity': AlertSeverity.WARNING,
                'message': 'Low temperature detected: {value:.1f}°C (threshold: {threshold}°C)'
            },
            AlertType.HUMIDITY_LOW: {
                'sensor_type': 'humidity',
                'condition': lambda x: x < 40,
                'severity': AlertSeverity.WARNING,
                'message': 'Low humidity: {value:.1f}% - Irrigation recommended (threshold: {threshold}%)'
            },
            AlertType.HUMIDITY_HIGH: {
                'sensor_type': 'humidity',
                'condition': lambda x: x > 90,
                'severity': AlertSeverity.WARNING,
                'message': 'High humidity: {value:.1f}% (threshold: {threshold}%)'
            },
            AlertType.SOIL_MOISTURE_LOW: {
                'sensor_type': 'soil_moisture',
                'condition': lambda x: x < 30,
                'severity': AlertSeverity.CRITICAL,
                'message': 'Very low soil moisture: {value:.1f}% (threshold: {threshold}%)'
            },
            AlertType.SOIL_MOISTURE_HIGH: {
                'sensor_type': 'soil_moisture',
                'condition': lambda x: x > 80,
                'severity': AlertSeverity.WARNING,
                'message': 'High soil moisture: {value:.1f}% (threshold: {threshold}%)'
            },
            AlertType.PH_HIGH: {
                'sensor_type': 'ph',
                'condition': lambda x: x > 8.0,
                'severity': AlertSeverity.WARNING,
                'message': 'High pH level: {value:.2f} (threshold: {threshold})'
            },
            AlertType.PH_LOW: {
                'sensor_type': 'ph',
                'condition': lambda x: x < 5.5,
                'severity': AlertSeverity.WARNING,
                'message': 'Low pH level: {value:.2f} (threshold: {threshold})'
            },
            AlertType.LIGHT_LOW: {
                'sensor_type': 'light',
                'condition': lambda x: x < 100,
                'severity': AlertSeverity.INFO,
                'message': 'Low light intensity: {value:.0f} lux (threshold: {threshold} lux)'
            },
            AlertType.LIGHT_HIGH: {
                'sensor_type': 'light',
                'condition': lambda x: x > 10000,
                'severity': AlertSeverity.WARNING,
                'message': 'High light intensity: {value:.0f} lux (threshold: {threshold} lux)'
            }
        }
    
    def add_rule(self, alert_type: AlertType, sensor_type: str,
                 condition: Callable[[float], bool],
                 severity: AlertSeverity,
                 message: str,
                 threshold: float):
        """
        Add custom alert rule
        
        Args:
            alert_type: Type of alert
            sensor_type: Type of sensor to monitor
            condition: Function that takes value and returns True if alert should trigger
            severity: Alert severity level
            message: Alert message template
            threshold: Threshold value
        """
        self.alert_rules[alert_type] = {
            'sensor_type': sensor_type,
            'condition': condition,
            'severity': severity,
            'message': message,
            'threshold': threshold
        }
        logger.info(f"✓ Added alert rule: {alert_type.value}")
    
    def check_alerts(self, df: pd.DataFrame) -> List[Alert]:
        """
        Check for alert conditions in sensor data
        
        Args:
            df: DataFrame with sensor data
            
        Returns:
            List of triggered alerts
        """
        try:
            triggered_alerts = []
            
            if df.empty:
                return triggered_alerts
            
            # Group by sensor type
            for sensor_type, group in df.groupby('sensor_type'):
                # Get latest value for each sensor
                latest_values = group.sort_values('timestamp').groupby('sensor_id').last()
                
                for sensor_id, row in latest_values.iterrows():
                    value = row['value']
                    
                    # Check all rules for this sensor type
                    for alert_type, rule in self.alert_rules.items():
                        if rule['sensor_type'] == sensor_type:
                            try:
                                if rule['condition'](value):
                                    # Create alert
                                    alert = Alert(
                                        alert_id=f"{alert_type.value}_{sensor_id}_{datetime.now().timestamp()}",
                                        alert_type=alert_type,
                                        severity=rule['severity'],
                                        sensor_id=sensor_id,
                                        sensor_type=sensor_type,
                                        message=rule['message'].format(
                                            value=value,
                                            threshold=rule.get('threshold', 'N/A')
                                        ),
                                        value=value,
                                        threshold=rule.get('threshold', 0.0),
                                        timestamp=datetime.now(),
                                        metadata={
                                            'location': row.get('location', 'Unknown'),
                                            'unit': row.get('unit', '')
                                        }
                                    )
                                    
                                    triggered_alerts.append(alert)
                                    
                            except Exception as e:
                                logger.error(f"Error checking rule {alert_type}: {e}")
            
            # Add new alerts to list
            self.alerts.extend(triggered_alerts)
            
            # Trigger notifications
            for alert in triggered_alerts:
                self._trigger_notifications(alert)
            
            if triggered_alerts:
                logger.info(f"✓ Generated {len(triggered_alerts)} alerts")
            
            return triggered_alerts
            
        except Exception as e:
            logger.error(f"Failed to check alerts: {e}")
            return []
    
    def _trigger_notifications(self, alert: Alert):
        """Trigger notification handlers"""
        try:
            for handler in self.notification_handlers:
                try:
                    handler(alert)
                except Exception as e:
                    logger.error(f"Notification handler failed: {e}")
        except Exception as e:
            logger.error(f"Failed to trigger notifications: {e}")
    
    def add_notification_handler(self, handler: Callable[[Alert], None]):
        """
        Add notification handler
        
        Args:
            handler: Function that takes an Alert object
        """
        self.notification_handlers.append(handler)
        logger.info(f"✓ Added notification handler: {handler.__name__}")
    
    def acknowledge_alert(self, alert_id: str, user: str = "system") -> bool:
        """
        Acknowledge an alert
        
        Args:
            alert_id: ID of alert to acknowledge
            user: User acknowledging the alert
            
        Returns:
            True if successful
        """
        try:
            for alert in self.alerts:
                if alert.alert_id == alert_id:
                    alert.acknowledged = True
                    alert.acknowledged_by = user
                    alert.acknowledged_at = datetime.now()
                    logger.info(f"✓ Alert acknowledged: {alert_id} by {user}")
                    return True
            
            logger.warning(f"Alert not found: {alert_id}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to acknowledge alert: {e}")
            return False
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """
        Get active (unacknowledged) alerts
        
        Args:
            severity: Filter by severity (optional)
            
        Returns:
            List of active alerts
        """
        active_alerts = [a for a in self.alerts if not a.acknowledged]
        
        if severity:
            active_alerts = [a for a in active_alerts if a.severity == severity]
        
        # Sort by timestamp (newest first)
        active_alerts.sort(key=lambda x: x.timestamp, reverse=True)
        
        return active_alerts
    
    def get_alerts_by_sensor(self, sensor_id: str) -> List[Alert]:
        """Get alerts for a specific sensor"""
        return [a for a in self.alerts if a.sensor_id == sensor_id]
    
    def get_alerts_by_type(self, alert_type: AlertType) -> List[Alert]:
        """Get alerts by type"""
        return [a for a in self.alerts if a.alert_type == alert_type]
    
    def get_alerts_by_time_range(self, start_time: datetime, 
                                 end_time: datetime) -> List[Alert]:
        """Get alerts within time range"""
        return [
            a for a in self.alerts 
            if start_time <= a.timestamp <= end_time
        ]
    
    def clear_old_alerts(self, hours: int = 24):
        """
        Clear alerts older than specified hours
        
        Args:
            hours: Age threshold in hours
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            old_count = len(self.alerts)
            
            self.alerts = [
                a for a in self.alerts 
                if a.timestamp >= cutoff_time or not a.acknowledged
            ]
            
            cleared_count = old_count - len(self.alerts)
            logger.info(f"✓ Cleared {cleared_count} old alerts")
            
        except Exception as e:
            logger.error(f"Failed to clear old alerts: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get alert statistics"""
        try:
            active_alerts = self.get_active_alerts()
            
            stats = {
                'total_alerts': len(self.alerts),
                'active_alerts': len(active_alerts),
                'acknowledged_alerts': len([a for a in self.alerts if a.acknowledged]),
                'by_severity': {
                    'critical': len([a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]),
                    'warning': len([a for a in active_alerts if a.severity == AlertSeverity.WARNING]),
                    'info': len([a for a in active_alerts if a.severity == AlertSeverity.INFO])
                },
                'by_type': {},
                'by_sensor': {}
            }
            
            # Count by type
            for alert in active_alerts:
                alert_type = alert.alert_type.value
                stats['by_type'][alert_type] = stats['by_type'].get(alert_type, 0) + 1
            
            # Count by sensor
            for alert in active_alerts:
                sensor_id = alert.sensor_id
                stats['by_sensor'][sensor_id] = stats['by_sensor'].get(sensor_id, 0) + 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def export_alerts(self, filepath: str, format: str = 'json'):
        """
        Export alerts to file
        
        Args:
            filepath: Path to export file
            format: Export format ('json', 'csv')
        """
        try:
            if format == 'json':
                alerts_data = []
                for alert in self.alerts:
                    alerts_data.append({
                        'alert_id': alert.alert_id,
                        'alert_type': alert.alert_type.value,
                        'severity': alert.severity.value,
                        'sensor_id': alert.sensor_id,
                        'sensor_type': alert.sensor_type,
                        'message': alert.message,
                        'value': alert.value,
                        'threshold': alert.threshold,
                        'timestamp': alert.timestamp.isoformat(),
                        'acknowledged': alert.acknowledged,
                        'acknowledged_by': alert.acknowledged_by,
                        'acknowledged_at': alert.acknowledged_at.isoformat() if alert.acknowledged_at else None
                    })
                
                with open(filepath, 'w') as f:
                    json.dump(alerts_data, f, indent=2)
                
                logger.info(f"✓ Exported {len(alerts_data)} alerts to {filepath}")
                
            elif format == 'csv':
                alerts_data = []
                for alert in self.alerts:
                    alerts_data.append({
                        'alert_id': alert.alert_id,
                        'alert_type': alert.alert_type.value,
                        'severity': alert.severity.value,
                        'sensor_id': alert.sensor_id,
                        'sensor_type': alert.sensor_type,
                        'message': alert.message,
                        'value': alert.value,
                        'threshold': alert.threshold,
                        'timestamp': alert.timestamp.isoformat(),
                        'acknowledged': alert.acknowledged
                    })
                
                df = pd.DataFrame(alerts_data)
                df.to_csv(filepath, index=False)
                
                logger.info(f"✓ Exported {len(alerts_data)} alerts to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to export alerts: {e}")


# Global alert manager instance
alert_manager = AlertManager()


def get_alert_manager() -> AlertManager:
    """Get alert manager instance"""
    return alert_manager


# Example notification handlers
def console_notification_handler(alert: Alert):
    """Print alert to console"""
    severity_emoji = {
        AlertSeverity.INFO: "ℹ️",
        AlertSeverity.WARNING: "⚠️",
        AlertSeverity.CRITICAL: "🚨"
    }
    
    emoji = severity_emoji.get(alert.severity, "📢")
    print(f"{emoji} [{alert.severity.value.upper()}] {alert.message}")


def email_notification_handler(alert: Alert):
    """Send email notification (placeholder)"""
    # Implement email sending logic here
    logger.info(f"Email notification sent for alert: {alert.alert_id}")


def sms_notification_handler(alert: Alert):
    """Send SMS notification (placeholder)"""
    # Implement SMS sending logic here
    logger.info(f"SMS notification sent for alert: {alert.alert_id}")


if __name__ == "__main__":
    # Test alert manager
    print("Testing Alert Manager...")
    print("="*80)
    
    # Create alert manager
    manager = AlertManager()
    
    # Add notification handlers
    manager.add_notification_handler(console_notification_handler)
    
    # Create sample data
    from datetime import datetime, timedelta
    
    timestamps = [datetime.now() - timedelta(hours=i) for i in range(50, 0, -1)]
    
    data = []
    
    # Normal temperature data
    for i, ts in enumerate(timestamps[:40]):
        data.append({
            'sensor_id': 'TEMP_001',
            'sensor_type': 'temperature',
            'value': 25 + 2 * np.sin(i / 5) + np.random.normal(0, 0.5),
            'timestamp': ts,
            'location': 'Field A'
        })
    
    # High temperature data (should trigger alert)
    for i, ts in enumerate(timestamps[40:]):
        data.append({
            'sensor_id': 'TEMP_001',
            'sensor_type': 'temperature',
            'value': 36 + np.random.normal(0, 0.5),  # Above 35°C threshold
            'timestamp': ts,
            'location': 'Field A'
        })
    
    # Low humidity data (should trigger alert)
    for i, ts in enumerate(timestamps[45:]):
        data.append({
            'sensor_id': 'HUM_001',
            'sensor_type': 'humidity',
            'value': 35 + np.random.normal(0, 2),  # Below 40% threshold
            'timestamp': ts,
            'location': 'Field A'
        })
    
    df = pd.DataFrame(data)
    
    # Check alerts
    print("\n1. Checking alerts...")
    alerts = manager.check_alerts(df)
    
    print(f"\nGenerated {len(alerts)} alerts")
    
    # Display alerts
    print("\n2. Active alerts:")
    active_alerts = manager.get_active_alerts()
    for alert in active_alerts[:5]:  # Show first 5
        print(f"  [{alert.severity.value.upper()}] {alert.message}")
    
    # Get statistics
    print("\n3. Alert statistics:")
    stats = manager.get_statistics()
    print(f"  Total alerts: {stats['total_alerts']}")
    print(f"  Active alerts: {stats['active_alerts']}")
    print(f"  By severity: {stats['by_severity']}")
    
    # Acknowledge an alert
    if active_alerts:
        print(f"\n4. Acknowledging alert: {active_alerts[0].alert_id}")
        manager.acknowledge_alert(active_alerts[0].alert_id, user="admin")
    
    # Export alerts
    print("\n5. Exporting alerts...")
    manager.export_alerts('results/alerts.json', format='json')
    manager.export_alerts('results/alerts.csv', format='csv')
    
    print("\n✓ Alert manager test complete!")