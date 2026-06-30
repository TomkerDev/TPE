"""
Model Saving and Loading Utilities
"""
import pandas as pd
import numpy as np
import logging
import joblib
import os
from typing import Dict, Any, Optional
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModelSaver:
    """Utility class for saving and loading models"""
    
    def __init__(self, base_dir: str = 'models'):
        """
        Initialize ModelSaver
        
        Args:
            base_dir: Base directory for saving models
        """
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        
    def save(self, model: Any, model_name: str, metadata: Dict[str, Any] = None,
             filepath: str = None) -> str:
        """
        Save model to file
        
        Args:
            model: Model object to save
            model_name: Name of the model
            metadata: Additional metadata to save
            filepath: Custom filepath (optional)
            
        Returns:
            Path where model was saved
        """
        try:
            if filepath is None:
                filepath = os.path.join(self.base_dir, f'{model_name}.pkl')
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Prepare data to save
            save_data = {
                'model': model,
                'model_name': model_name,
                'metadata': metadata or {}
            }
            
            # Save model
            joblib.dump(save_data, filepath)
            
            logger.info(f"✓ Saved model '{model_name}' to {filepath}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save model '{model_name}': {e}")
            return ""
    
    def load(self, filepath: str) -> Optional[Dict[str, Any]]:
        """
        Load model from file
        
        Args:
            filepath: Path to model file
            
        Returns:
            Dictionary with model and metadata
        """
        try:
            if not os.path.exists(filepath):
                logger.error(f"Model file not found: {filepath}")
                return None
            
            data = joblib.load(filepath)
            
            logger.info(f"✓ Loaded model from {filepath}")
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to load model from {filepath}: {e}")
            return None
    
    def save_metrics(self, metrics: Dict[str, Any], model_name: str,
                     filepath: str = None) -> str:
        """
        Save model metrics to JSON file
        
        Args:
            metrics: Dictionary of metrics
            model_name: Name of the model
            filepath: Custom filepath (optional)
            
        Returns:
            Path where metrics were saved
        """
        try:
            if filepath is None:
                filepath = os.path.join(self.base_dir, f'{model_name}_metrics.json')
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Convert numpy types to Python types
            metrics_serializable = {}
            for key, value in metrics.items():
                if isinstance(value, (np.integer, np.floating)):
                    metrics_serializable[key] = float(value)
                elif isinstance(value, np.ndarray):
                    metrics_serializable[key] = value.tolist()
                elif isinstance(value, dict):
                    metrics_serializable[key] = self._convert_dict(value)
                else:
                    metrics_serializable[key] = value
            
            # Save to JSON
            with open(filepath, 'w') as f:
                json.dump(metrics_serializable, f, indent=2)
            
            logger.info(f"✓ Saved metrics for '{model_name}' to {filepath}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save metrics for '{model_name}': {e}")
            return ""
    
    def load_metrics(self, model_name: str, filepath: str = None) -> Optional[Dict[str, Any]]:
        """
        Load model metrics from JSON file
        
        Args:
            model_name: Name of the model
            filepath: Custom filepath (optional)
            
        Returns:
            Dictionary of metrics
        """
        try:
            if filepath is None:
                filepath = os.path.join(self.base_dir, f'{model_name}_metrics.json')
            
            if not os.path.exists(filepath):
                logger.error(f"Metrics file not found: {filepath}")
                return None
            
            with open(filepath, 'r') as f:
                metrics = json.load(f)
            
            logger.info(f"✓ Loaded metrics for '{model_name}' from {filepath}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to load metrics for '{model_name}': {e}")
            return None
    
    def _convert_dict(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Convert numpy types in dictionary to Python types"""
        result = {}
        for key, value in d.items():
            if isinstance(value, (np.integer, np.floating)):
                result[key] = float(value)
            elif isinstance(value, np.ndarray):
                result[key] = value.tolist()
            elif isinstance(value, dict):
                result[key] = self._convert_dict(value)
            elif isinstance(value, list):
                result[key] = self._convert_list(value)
            else:
                result[key] = value
        return result
    
    def _convert_list(self, lst: list) -> list:
        """Convert numpy types in list to Python types"""
        result = []
        for item in lst:
            if isinstance(item, (np.integer, np.floating)):
                result.append(float(item))
            elif isinstance(item, np.ndarray):
                result.append(item.tolist())
            elif isinstance(item, dict):
                result.append(self._convert_dict(item))
            elif isinstance(item, list):
                result.append(self._convert_list(item))
            else:
                result.append(item)
        return result
    
    def list_saved_models(self) -> list:
        """
        List all saved models
        
        Returns:
            List of model file paths
        """
        try:
            models = []
            for file in os.listdir(self.base_dir):
                if file.endswith('.pkl') or file.endswith('.h5'):
                    models.append(os.path.join(self.base_dir, file))
            
            return sorted(models)
            
        except Exception as e:
            logger.error(f"Failed to list saved models: {e}")
            return []
    
    def delete_model(self, model_name: str) -> bool:
        """
        Delete a saved model
        
        Args:
            model_name: Name of the model to delete
            
        Returns:
            True if deletion successful
        """
        try:
            filepath = os.path.join(self.base_dir, f'{model_name}.pkl')
            
            if not os.path.exists(filepath):
                logger.warning(f"Model file not found: {filepath}")
                return False
            
            os.remove(filepath)
            
            # Also delete metrics file if exists
            metrics_filepath = os.path.join(self.base_dir, f'{model_name}_metrics.json')
            if os.path.exists(metrics_filepath):
                os.remove(metrics_filepath)
            
            logger.info(f"✓ Deleted model '{model_name}'")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete model '{model_name}': {e}")
            return False
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a saved model
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dictionary with model information
        """
        try:
            filepath = os.path.join(self.base_dir, f'{model_name}.pkl')
            
            if not os.path.exists(filepath):
                logger.error(f"Model file not found: {filepath}")
                return None
            
            # Get file stats
            file_stats = os.stat(filepath)
            
            # Load model data
            data = self.load(filepath)
            
            info = {
                'model_name': model_name,
                'filepath': filepath,
                'file_size_mb': file_stats.st_size / (1024 * 1024),
                'created_time': pd.Timestamp(file_stats.st_ctime, unit='s').isoformat(),
                'modified_time': pd.Timestamp(file_stats.st_mtime, unit='s').isoformat(),
                'metadata': data.get('metadata', {}) if data else {}
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get model info for '{model_name}': {e}")
            return None


# Global instance
model_saver = ModelSaver()


def save_model(model: Any, model_name: str, metadata: Dict[str, Any] = None,
               filepath: str = None) -> str:
    """
    Convenience function to save a model
    
    Args:
        model: Model object to save
        model_name: Name of the model
        metadata: Additional metadata
        filepath: Custom filepath
        
    Returns:
        Path where model was saved
    """
    return model_saver.save(model, model_name, metadata, filepath)


def load_model(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Convenience function to load a model
    
    Args:
        filepath: Path to model file
        
    Returns:
        Dictionary with model and metadata
    """
    return model_saver.load(filepath)


def save_metrics(metrics: Dict[str, Any], model_name: str,
                 filepath: str = None) -> str:
    """
    Convenience function to save model metrics
    
    Args:
        metrics: Dictionary of metrics
        model_name: Name of the model
        filepath: Custom filepath
        
    Returns:
        Path where metrics were saved
    """
    return model_saver.save_metrics(metrics, model_name, filepath)


def load_metrics(model_name: str, filepath: str = None) -> Optional[Dict[str, Any]]:
    """
    Convenience function to load model metrics
    
    Args:
        model_name: Name of the model
        filepath: Custom filepath
        
    Returns:
        Dictionary of metrics
    """
    return model_saver.load_metrics(model_name, filepath)


if __name__ == "__main__":
    # Test model saving/loading
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import make_classification
    
    print("Creating test model...")
    X, y = make_classification(n_samples=100, n_features=4, random_state=42)
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)
    
    print("\nSaving model...")
    saver = ModelSaver()
    filepath = saver.save(model, 'test_model', metadata={'accuracy': 0.95})
    
    print("\nLoading model...")
    loaded_data = saver.load(filepath)
    print(f"Loaded model: {loaded_data['model_name']}")
    print(f"Metadata: {loaded_data['metadata']}")
    
    print("\nSaving metrics...")
    metrics = {'accuracy': 0.95, 'f1_score': 0.94}
    metrics_path = saver.save_metrics(metrics, 'test_model')
    
    print("\nLoading metrics...")
    loaded_metrics = saver.load_metrics('test_model')
    print(f"Loaded metrics: {loaded_metrics}")
    
    print("\nListing saved models...")
    models = saver.list_saved_models()
    print(f"Saved models: {models}")
    
    print("\nGetting model info...")
    info = saver.get_model_info('test_model')
    print(f"Model info: {info}")