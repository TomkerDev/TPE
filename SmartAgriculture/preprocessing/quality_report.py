"""
Data Quality Report Module
Generates comprehensive quality reports for sensor data
"""
import json
from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class QualityReport:
    """Generates data quality reports"""
    
    def __init__(self):
        self.report_data = {
            'generated_at': None,
            'summary': {},
            'validation': {},
            'cleaning': {},
            'normalization': {},
            'outliers': {},
            'features': {},
            'recommendations': []
        }
        
    def generate_report(self, pipeline_stats: Dict[str, Any], 
                       sample_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate comprehensive quality report
        
        Args:
            pipeline_stats: Statistics from preprocessing pipeline
            sample_data: Optional sample of processed data
            
        Returns:
            Quality report dictionary
        """
        self.report_data['generated_at'] = datetime.utcnow().isoformat()
        
        # Generate summary
        self._generate_summary(pipeline_stats)
        
        # Generate validation section
        self._generate_validation_report(pipeline_stats)
        
        # Generate cleaning section
        self._generate_cleaning_report(pipeline_stats)
        
        # Generate normalization section
        self._generate_normalization_report(pipeline_stats)
        
        # Generate outlier section
        self._generate_outlier_report(pipeline_stats)
        
        # Generate feature engineering section
        self._generate_feature_report(pipeline_stats)
        
        # Generate recommendations
        self._generate_recommendations(pipeline_stats)
        
        # Analyze sample data if provided
        if sample_data:
            self._analyze_sample_data(sample_data)
        
        return self.report_data
    
    def _generate_summary(self, stats: Dict[str, Any]):
        """Generate summary section"""
        total = stats.get('total_received', 0)
        successful = stats.get('successful', 0)
        
        self.report_data['summary'] = {
            'total_records_processed': total,
            'successful_records': successful,
            'failed_records': total - successful,
            'success_rate_percent': round((successful / total * 100) if total > 0 else 0, 2),
            'sensor_types_count': len(stats.get('by_sensor_type', {})),
            'processing_timestamp': datetime.utcnow().isoformat()
        }
    
    def _generate_validation_report(self, stats: Dict[str, Any]):
        """Generate validation section"""
        total = stats.get('total_received', 0)
        failed = stats.get('validation_failed', 0)
        
        self.report_data['validation'] = {
            'total_validated': total,
            'passed': total - failed,
            'failed': failed,
            'success_rate_percent': round(((total - failed) / total * 100) if total > 0 else 0, 2),
            'common_issues': [
                'Champ timestamp manquant',
                'Champ sensor_id manquant',
                'Champ sensor_type manquant',
                'Timestamp invalide',
                'Valeur numérique invalide'
            ]
        }
    
    def _generate_cleaning_report(self, stats: Dict[str, Any]):
        """Generate cleaning section"""
        cleaner_stats = stats.get('cleaner', {})
        
        self.report_data['cleaning'] = {
            'total_processed': cleaner_stats.get('total_processed', 0),
            'null_values_cleaned': cleaner_stats.get('null_values_cleaned', 0),
            'type_conversions': cleaner_stats.get('type_conversions', 0),
            'duplicates_removed': cleaner_stats.get('duplicates_removed', 0),
            'data_quality_improvement': self._calculate_quality_improvement(cleaner_stats)
        }
    
    def _generate_normalization_report(self, stats: Dict[str, Any]):
        """Generate normalization section"""
        normalizer_stats = stats.get('normalizer', {})
        
        self.report_data['normalization'] = {
            'total_processed': normalizer_stats.get('total_processed', 0),
            'units_normalized': normalizer_stats.get('units_normalized', 0),
            'values_converted': normalizer_stats.get('values_converted', 0),
            'standardization_rate_percent': round(
                (normalizer_stats.get('units_normalized', 0) / normalizer_stats.get('total_processed', 1) * 100)
                if normalizer_stats.get('total_processed', 0) > 0 else 0,
                2
            )
        }
    
    def _generate_outlier_report(self, stats: Dict[str, Any]):
        """Generate outlier detection section"""
        outlier_stats = stats.get('outlier_detector', {})
        total_checked = outlier_stats.get('total_checked', 0)
        outliers_detected = outlier_stats.get('outliers_detected', 0)
        
        self.report_data['outliers'] = {
            'total_checked': total_checked,
            'outliers_detected': outliers_detected,
            'outlier_rate_percent': round((outliers_detected / total_checked * 100) if total_checked > 0 else 0, 2),
            'by_sensor_type': outlier_stats.get('outliers_by_type', {}),
            'thresholds_applied': {
                'temperature': '[-20, 60] °C',
                'humidity': '[0, 100] %',
                'soil_moisture': '[0, 100] %',
                'ph': '[0, 14] pH',
                'wind': '[0, 150] km/h',
                'light': '[0, 120000] Lux',
                'rainfall': '[0, 500] mm'
            }
        }
    
    def _generate_feature_report(self, stats: Dict[str, Any]):
        """Generate feature engineering section"""
        feature_stats = stats.get('feature_engineer', {})
        
        self.report_data['features'] = {
            'total_processed': feature_stats.get('total_processed', 0),
            'features_created': feature_stats.get('features_created', 0),
            'feature_types': [
                'Time-based: year, month, day, hour, minute, weekday, season',
                'Cyclic: hour_sin, hour_cos, month_sin, month_cos',
                'Categorical: temp_category, humidity_category, ph_category',
                'Derived: heat_index, gdd, water_quality_index',
                'Binary: is_weekend, is_night, has_rain, is_moving'
            ]
        }
    
    def _generate_recommendations(self, stats: Dict[str, Any]):
        """Generate recommendations based on statistics"""
        recommendations = []
        
        # Check success rate
        total = stats.get('total_received', 0)
        successful = stats.get('successful', 0)
        success_rate = (successful / total * 100) if total > 0 else 0
        
        if success_rate < 90:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Data Quality',
                'issue': f'Taux de succès bas: {success_rate:.2f}%',
                'recommendation': 'Vérifier les sources de données et améliorer la validation'
            })
        
        # Check outlier rate
        outlier_stats = stats.get('outlier_detector', {})
        total_checked = outlier_stats.get('total_checked', 0)
        outliers_detected = outlier_stats.get('outliers_detected', 0)
        outlier_rate = (outliers_detected / total_checked * 100) if total_checked > 0 else 0
        
        if outlier_rate > 10:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Outliers',
                'issue': f'Taux d\'anomalies élevé: {outlier_rate:.2f}%',
                'recommendation': 'Vérifier les capteurs et calibrer les seuils de détection'
            })
        
        # Check duplicate rate
        cleaner_stats = stats.get('cleaner', {})
        duplicates = cleaner_stats.get('duplicates_removed', 0)
        total_processed = cleaner_stats.get('total_processed', 0)
        duplicate_rate = (duplicates / total_processed * 100) if total_processed > 0 else 0
        
        if duplicate_rate > 5:
            recommendations.append({
                'priority': 'LOW',
                'category': 'Duplicates',
                'issue': f'Taux de doublons: {duplicate_rate:.2f}%',
                'recommendation': 'Vérifier la fréquence d\'envoi des capteurs'
            })
        
        # Check validation failures
        validation_failed = stats.get('validation_failed', 0)
        if validation_failed > 0:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Validation',
                'issue': f'{validation_failed} échecs de validation',
                'recommendation': 'Vérifier la structure des données et les champs obligatoires'
            })
        
        if not recommendations:
            recommendations.append({
                'priority': 'INFO',
                'category': 'Quality',
                'issue': 'Aucun problème détecté',
                'recommendation': 'Continuer le monitoring régulier'
            })
        
        self.report_data['recommendations'] = recommendations
    
    def _calculate_quality_improvement(self, cleaner_stats: Dict[str, int]) -> float:
        """Calculate data quality improvement percentage"""
        total = cleaner_stats.get('total_processed', 0)
        if total == 0:
            return 0.0
        
        issues_fixed = (
            cleaner_stats.get('null_values_cleaned', 0) +
            cleaner_stats.get('type_conversions', 0) +
            cleaner_stats.get('duplicates_removed', 0)
        )
        
        return round((issues_fixed / total * 100), 2)
    
    def _analyze_sample_data(self, sample_data: List[Dict[str, Any]]):
        """Analyze sample data for additional insights"""
        
        if not sample_data:
            return
        
        # Analyze sensor types distribution
        sensor_type_counts = {}
        for data in sample_data:
            sensor_type = data.get('sensor_type', 'unknown')
            sensor_type_counts[sensor_type] = sensor_type_counts.get(sensor_type, 0) + 1
        
        self.report_data['sample_analysis'] = {
            'sample_size': len(sample_data),
            'sensor_type_distribution': sensor_type_counts,
            'completeness': self._calculate_completeness(sample_data),
            'data_types': self._analyze_data_types(sample_data)
        }
    
    def _calculate_completeness(self, sample_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate data completeness for each field"""
        if not sample_data:
            return {}
        
        field_counts = {}
        for data in sample_data:
            for field in data.keys():
                field_counts[field] = field_counts.get(field, 0) + 1
        
        completeness = {}
        for field, count in field_counts.items():
            completeness[field] = round((count / len(sample_data)) * 100, 2)
        
        return completeness
    
    def _analyze_data_types(self, sample_data: List[Dict[str, Any]]) -> Dict[str, str]:
        """Analyze data types in sample"""
        if not sample_data:
            return {}
        
        # Use first record to infer types
        data_types = {}
        for field, value in sample_data[0].items():
            if value is None:
                data_types[field] = 'null'
            elif isinstance(value, bool):
                data_types[field] = 'boolean'
            elif isinstance(value, int):
                data_types[field] = 'integer'
            elif isinstance(value, float):
                data_types[field] = 'float'
            elif isinstance(value, str):
                data_types[field] = 'string'
            elif isinstance(value, datetime):
                data_types[field] = 'datetime'
            else:
                data_types[field] = type(value).__name__
        
        return data_types
    
    def print_report(self):
        """Print formatted quality report"""
        report = self.report_data
        
        print("\n" + "=" * 70)
        print("RAPPORT DE QUALITÉ DES DONNÉES")
        print("=" * 70)
        
        # Summary
        print(f"\nGénéré le: {report['generated_at']}")
        summary = report['summary']
        print(f"\n--- RÉSUMÉ ---")
        print(f"Total enregistrements: {summary['total_records_processed']}")
        print(f"Enregistrements réussis: {summary['successful_records']}")
        print(f"Enregistrements échoués: {summary['failed_records']}")
        print(f"Taux de réussite: {summary['success_rate_percent']}%")
        print(f"Types de capteurs: {summary['sensor_types_count']}")
        
        # Validation
        print(f"\n--- VALIDATION ---")
        validation = report['validation']
        print(f"Total validé: {validation['total_validated']}")
        print(f"Réussi: {validation['passed']}")
        print(f"Échoué: {validation['failed']}")
        print(f"Taux de réussite: {validation['success_rate_percent']}%")
        
        # Cleaning
        print(f"\n--- NETTOYAGE ---")
        cleaning = report['cleaning']
        print(f"Total traité: {cleaning['total_processed']}")
        print(f"Valeurs nulles nettoyées: {cleaning['null_values_cleaned']}")
        print(f"Conversions de type: {cleaning['type_conversions']}")
        print(f"Doublons supprimés: {cleaning['duplicates_removed']}")
        print(f"Amélioration qualité: {cleaning['data_quality_improvement']}%")
        
        # Normalization
        print(f"\n--- NORMALISATION ---")
        normalization = report['normalization']
        print(f"Total traité: {normalization['total_processed']}")
        print(f"Unités normalisées: {normalization['units_normalized']}")
        print(f"Valeurs converties: {normalization['values_converted']}")
        print(f"Taux de standardisation: {normalization['standardization_rate_percent']}%")
        
        # Outliers
        print(f"\n--- DÉTECTION D'ANOMALIES ---")
        outliers = report['outliers']
        print(f"Total vérifié: {outliers['total_checked']}")
        print(f"Anomalies détectées: {outliers['outliers_detected']}")
        print(f"Taux d'anomalies: {outliers['outlier_rate_percent']}%")
        if outliers['by_sensor_type']:
            print(f"Par type de capteur:")
            for sensor_type, count in outliers['by_sensor_type'].items():
                print(f"  - {sensor_type}: {count}")
        
        # Features
        print(f"\n--- FEATURE ENGINEERING ---")
        features = report['features']
        print(f"Total traité: {features['total_processed']}")
        print(f"Features créées: {features['features_created']}")
        
        # Recommendations
        print(f"\n--- RECOMMANDATIONS ---")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"\n{i}. [{rec['priority']}] {rec['category']}")
            print(f"   Problème: {rec['issue']}")
            print(f"   Recommandation: {rec['recommendation']}")
        
        # Sample analysis
        if 'sample_analysis' in report:
            print(f"\n--- ANALYSE DE L'ÉCHANTILLON ---")
            sample = report['sample_analysis']
            print(f"Taille de l'échantillon: {sample['sample_size']}")
            print(f"Distribution par type:")
            for sensor_type, count in sample['sensor_type_distribution'].items():
                print(f"  - {sensor_type}: {count}")
            print(f"Complétude des champs:")
            for field, completeness in sample['completeness'].items():
                print(f"  - {field}: {completeness}%")
        
        print("\n" + "=" * 70 + "\n")
    
    def export_to_json(self, filepath: str):
        """Export report to JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.report_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Report exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export report: {e}")
            return False
    
    def export_to_html(self, filepath: str):
        """Export report to HTML file"""
        try:
            report = self.report_data
            
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Data Quality Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 2px solid #ddd; padding-bottom: 10px; }}
        .summary {{ background-color: #f0f0f0; padding: 15px; border-radius: 5px; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #fff; border: 1px solid #ddd; border-radius: 5px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #333; }}
        .metric-label {{ font-size: 14px; color: #666; }}
        .success {{ color: #28a745; }}
        .warning {{ color: #ffc107; }}
        .danger {{ color: #dc3545; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .recommendation {{ padding: 10px; margin: 10px 0; border-radius: 5px; }}
        .priority-HIGH {{ background-color: #f8d7da; }}
        .priority-MEDIUM {{ background-color: #fff3cd; }}
        .priority-LOW {{ background-color: #d1ecf1; }}
        .priority-INFO {{ background-color: #d4edda; }}
    </style>
</head>
<body>
    <h1>📊 Rapport de Qualité des Données</h1>
    <p>Généré le: {report['generated_at']}</p>
    
    <div class="summary">
        <h2>Résumé</h2>
        <div class="metric">
            <div class="metric-value">{report['summary']['total_records_processed']}</div>
            <div class="metric-label">Total traité</div>
        </div>
        <div class="metric">
            <div class="metric-value success">{report['summary']['successful_records']}</div>
            <div class="metric-label">Réussis</div>
        </div>
        <div class="metric">
            <div class="metric-value danger">{report['summary']['failed_records']}</div>
            <div class="metric-label">Échoués</div>
        </div>
        <div class="metric">
            <div class="metric-value">{report['summary']['success_rate_percent']}%</div>
            <div class="metric-label">Taux de réussite</div>
        </div>
    </div>
    
    <h2>Validation</h2>
    <p>Réussite: {report['validation']['success_rate_percent']}%</p>
    
    <h2>Nettoyage</h2>
    <p>Valeurs nulles nettoyées: {report['cleaning']['null_values_cleaned']}</p>
    <p>Doublons supprimés: {report['cleaning']['duplicates_removed']}</p>
    
    <h2>Détection d'Anomalies</h2>
    <p>Anomalies détectées: {report['outliers']['outliers_detected']} ({report['outliers']['outlier_rate_percent']}%)</p>
    
    <h2>Recommandations</h2>
"""
            
            for rec in report['recommendations']:
                html_content += f"""
    <div class="recommendation priority-{rec['priority']}">
        <strong>[{rec['priority']}] {rec['category']}</strong><br>
        {rec['issue']}<br>
        <em>{rec['recommendation']}</em>
    </div>
"""
            
            html_content += """
</body>
</html>
"""
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML report exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export HTML report: {e}")
            return False


def generate_quality_report(pipeline_stats: Dict[str, Any], 
                           sample_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convenience function to generate quality report
    
    Args:
        pipeline_stats: Statistics from preprocessing pipeline
        sample_data: Optional sample of processed data
        
    Returns:
        Quality report dictionary
    """
    report = QualityReport()
    return report.generate_report(pipeline_stats, sample_data)


def print_quality_report(pipeline_stats: Dict[str, Any], 
                        sample_data: List[Dict[str, Any]] = None):
    """
    Convenience function to print quality report
    
    Args:
        pipeline_stats: Statistics from preprocessing pipeline
        sample_data: Optional sample of processed data
    """
    report = QualityReport()
    report.generate_report(pipeline_stats, sample_data)
    report.print_report()