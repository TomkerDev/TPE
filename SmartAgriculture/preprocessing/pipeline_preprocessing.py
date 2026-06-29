#!/usr/bin/env python3
"""
Preprocessing Pipeline
Orchestrates the complete data preprocessing workflow:
Validation → Cleaning → Normalization → Outlier Detection → Feature Engineering
"""
import os
import sys
import time
import signal
import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime
from dotenv import load_dotenv

from preprocessing.validator import DataValidator, validate_data, validate_batch
from preprocessing.cleaner import DataCleaner, clean_data, clean_batch_data
from preprocessing.normalizer import DataNormalizer, normalize_data, normalize_batch_data
from preprocessing.outlier_detector import OutlierDetector, detect_outlier, filter_outliers
from preprocessing.feature_engineering import FeatureEngineer, create_features, create_features_batch

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PreprocessingPipeline:
    """
    Complete preprocessing pipeline for sensor data
    """
    
    def __init__(self, remove_outliers: bool = False):
        """
        Initialize preprocessing pipeline
        
        Args:
            remove_outliers: If True, remove outliers; if False, keep them but mark them
        """
        self.remove_outliers = remove_outliers
        
        # Initialize components
        self.validator = DataValidator()
        self.cleaner = DataCleaner()
        self.normalizer = DataNormalizer()
        self.outlier_detector = OutlierDetector()
        self.feature_engineer = FeatureEngineer()
        
        # Statistics
        self.pipeline_stats = {
            'total_received': 0,
            'validation_failed': 0,
            'cleaning_failed': 0,
            'normalization_failed': 0,
            'outliers_detected': 0,
            'feature_engineering_failed': 0,
            'successful': 0,
            'by_sensor_type': {}
        }
        
    def process(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], bool, str]:
        """
        Process a single data point through the complete pipeline
        
        Args:
            data: Raw sensor data dictionary
            
        Returns:
            Tuple of (processed_data, is_success, message)
        """
        self.pipeline_stats['total_received'] += 1
        
        if not data:
            return data, False, "Données vides"
        
        sensor_type = data.get('sensor_type', 'unknown')
        
        try:
            # Step 1: Validation
            is_valid, validation_msg = self.validator.validate(data)
            if not is_valid:
                self.pipeline_stats['validation_failed'] += 1
                logger.warning(f"Validation failed: {validation_msg}")
                return data, False, f"Validation échouée: {validation_msg}"
            
            logger.debug(f"✓ Validation passed for {sensor_type}")
            
            # Step 2: Cleaning
            data = self.cleaner.clean(data)
            if data is None:
                self.pipeline_stats['cleaning_failed'] += 1
                logger.warning("Cleaning failed: duplicate detected")
                return data, False, "Doublon détecté"
            
            logger.debug(f"✓ Cleaning passed for {sensor_type}")
            
            # Step 3: Normalization
            data = self.normalizer.normalize(data)
            logger.debug(f"✓ Normalization passed for {sensor_type}")
            
            # Step 4: Outlier Detection
            is_outlier, outlier_reason = self.outlier_detector.detect(data)
            if is_outlier:
                self.pipeline_stats['outliers_detected'] += 1
                data['is_outlier'] = True
                data['outlier_reason'] = outlier_reason
                logger.warning(f"Outlier detected for {sensor_type}: {outlier_reason}")
                
                if self.remove_outliers:
                    return data, False, f"Valeur aberrante détectée: {outlier_reason}"
            else:
                data['is_outlier'] = False
            
            logger.debug(f"✓ Outlier detection passed for {sensor_type}")
            
            # Step 5: Feature Engineering
            data = self.feature_engineer.create_features(data)
            logger.debug(f"✓ Feature engineering passed for {sensor_type}")
            
            # Mark as successful
            self.pipeline_stats['successful'] += 1
            
            # Update sensor type stats
            if sensor_type not in self.pipeline_stats['by_sensor_type']:
                self.pipeline_stats['by_sensor_type'][sensor_type] = 0
            self.pipeline_stats['by_sensor_type'][sensor_type] += 1
            
            logger.info(f"✓ Successfully processed {sensor_type} data from sensor {data.get('sensor_id')}")
            return data, True, "Succès"
            
        except Exception as e:
            logger.error(f"Pipeline error for {sensor_type}: {e}", exc_info=True)
            return data, False, f"Erreur du pipeline: {str(e)}"
    
    def process_batch(self, data_list: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Process a batch of data through the pipeline
        
        Args:
            data_list: List of raw sensor data dictionaries
            
        Returns:
            Tuple of (processed_data, failed_data)
        """
        processed_data = []
        failed_data = []
        
        for data in data_list:
            processed, is_success, message = self.process(data)
            
            if is_success:
                processed_data.append(processed)
            else:
                processed['error_message'] = message
                failed_data.append(processed)
        
        return processed_data, failed_data
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics"""
        stats = self.pipeline_stats.copy()
        
        # Add component stats
        stats['validator'] = {}  # Validator doesn't track stats in current implementation
        stats['cleaner'] = self.cleaner.get_stats()
        stats['normalizer'] = self.normalizer.get_stats()
        stats['outlier_detector'] = self.outlier_detector.get_stats()
        stats['feature_engineer'] = self.feature_engineer.get_stats()
        
        # Calculate success rate
        if stats['total_received'] > 0:
            stats['success_rate'] = (stats['successful'] / stats['total_received']) * 100
        else:
            stats['success_rate'] = 0
        
        return stats
    
    def reset_stats(self):
        """Reset all statistics"""
        self.pipeline_stats = {
            'total_received': 0,
            'validation_failed': 0,
            'cleaning_failed': 0,
            'normalization_failed': 0,
            'outliers_detected': 0,
            'feature_engineering_failed': 0,
            'successful': 0,
            'by_sensor_type': {}
        }
        
        self.cleaner.reset_stats()
        self.normalizer.reset_stats()
        self.outlier_detector.reset_stats()
        self.feature_engineer.reset_stats()
    
    def print_report(self):
        """Print preprocessing report"""
        stats = self.get_stats()
        
        print("\n" + "=" * 60)
        print("RAPPORT DE PRÉTRAITEMENT")
        print("=" * 60)
        
        print(f"\nTotal reçu: {stats['total_received']}")
        print(f"Succès: {stats['successful']}")
        print(f"Échecs: {stats['total_received'] - stats['successful']}")
        print(f"Taux de réussite: {stats['success_rate']:.2f}%")
        
        print(f"\n--- Détails des échecs ---")
        print(f"Validation échouée: {stats['validation_failed']}")
        print(f"Nettoyage échoué: {stats['cleaning_failed']}")
        print(f"Détection d'anomalies: {stats['outliers_detected']}")
        
        print(f"\n--- Statistiques par type de capteur ---")
        for sensor_type, count in stats['by_sensor_type'].items():
            print(f"  {sensor_type}: {count}")
        
        print(f"\n--- Statistiques des composants ---")
        print(f"Nettoyage:")
        print(f"  - Total traité: {stats['cleaner']['total_processed']}")
        print(f"  - Valeurs nulles nettoyées: {stats['cleaner']['null_values_cleaned']}")
        print(f"  - Conversions de type: {stats['cleaner']['type_conversions']}")
        print(f"  - Doublons supprimés: {stats['cleaner']['duplicates_removed']}")
        
        print(f"\nNormalisation:")
        print(f"  - Total traité: {stats['normalizer']['total_processed']}")
        print(f"  - Unités normalisées: {stats['normalizer']['units_normalized']}")
        print(f"  - Valeurs converties: {stats['normalizer']['values_converted']}")
        
        print(f"\nDétection d'anomalies:")
        print(f"  - Total vérifié: {stats['outlier_detector']['total_checked']}")
        print(f"  - Anomalies détectées: {stats['outlier_detector']['outliers_detected']}")
        if stats['outlier_detector']['outliers_by_type']:
            print(f"  - Par type:")
            for sensor_type, count in stats['outlier_detector']['outliers_by_type'].items():
                print(f"      {sensor_type}: {count}")
        
        print(f"\nFeature Engineering:")
        print(f"  - Total traité: {stats['feature_engineer']['total_processed']}")
        print(f"  - Features créées: {stats['feature_engineer']['features_created']}")
        
        print("=" * 60 + "\n")


def main():
    """Main function for testing"""
    
    print("=" * 60)
    print("TEST DU PIPELINE DE PRÉTRAITEMENT")
    print("=" * 60)
    
    # Create pipeline
    pipeline = PreprocessingPipeline(remove_outliers=False)
    
    # Test data samples
    test_data_samples = [
        {
            'sensor_id': 'temp_sensor_001',
            'sensor_type': 'temperature',
            'temperature': 25.5,
            'unit': 'celsius',
            'timestamp': '2024-01-01T12:00:00'
        },
        {
            'sensor_id': 'temp_sensor_001',
            'sensor_type': 'temperature',
            'temperature': 26.0,
            'unit': 'celsius',
            'timestamp': '2024-01-01T12:00:00'  # Duplicate
        },
        {
            'sensor_id': 'temp_sensor_002',
            'sensor_type': 'temperature',
            'temperature': 150.0,  # Outlier
            'unit': 'celsius',
            'timestamp': '2024-01-01T12:01:00'
        },
        {
            'sensor_id': 'humidity_sensor_001',
            'sensor_type': 'humidity',
            'humidity': 65.0,
            'unit': 'percent',
            'timestamp': '2024-01-01T12:02:00'
        },
        {
            'sensor_id': 'ph_sensor_001',
            'sensor_type': 'ph',
            'ph': 6.5,
            'unit': 'pH',
            'timestamp': '2024-01-01T12:03:00'
        }
    ]
    
    print("\nTraitement des données de test...\n")
    
    # Process each sample
    for i, data in enumerate(test_data_samples, 1):
        print(f"\n--- Test {i} ---")
        print(f"Entrée: {data}")
        
        processed, is_success, message = pipeline.process(data)
        
        print(f"Sortie: {processed}")
        print(f"Succès: {is_success}")
        print(f"Message: {message}")
    
    # Print final report
    pipeline.print_report()


if __name__ == "__main__":
    main()