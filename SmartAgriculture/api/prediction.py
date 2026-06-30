"""
ML Model Prediction Module for Smart Agriculture API
"""
import joblib
import numpy as np
import pandas as pd
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PredictionEngine:
    """ML model prediction engine"""
    
    def __init__(self, models_dir: str = "data/models"):
        """
        Initialize prediction engine
        
        Args:
            models_dir: Directory containing trained models
        """
        self.models_dir = Path(models_dir)
        self.models: Dict[str, Any] = {}
        self.model_metadata: Dict[str, Dict[str, Any]] = {}
        self._load_models()
        
    def _load_models(self):
        """Load all available models"""
        try:
            if not self.models_dir.exists():
                logger.warning(f"Models directory not found: {self.models_dir}")
                return
            
            # Load all .pkl files
            for model_file in self.models_dir.glob("*.pkl"):
                try:
                    model_name = model_file.stem
                    model = joblib.load(model_file)
                    self.models[model_name] = model
                    
                    # Load metadata if exists
                    metadata_file = model_file.with_suffix('.json')
                    if metadata_file.exists():
                        import json
                        with open(metadata_file, 'r') as f:
                            self.model_metadata[model_name] = json.load(f)
                    else:
                        self.model_metadata[model_name] = {
                            'model_type': model_name,
                            'file_path': str(model_file)
                        }
                    
                    logger.info(f"✓ Loaded model: {model_name}")
                    
                except Exception as e:
                    logger.error(f"Failed to load model {model_file}: {e}")
            
            logger.info(f"✓ Loaded {len(self.models)} models")
            
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models
        
        Returns:
            List of model information
        """
        models_info = []
        
        for model_name, model in self.models.items():
            metadata = self.model_metadata.get(model_name, {})
            
            models_info.append({
                'model_name': model_name,
                'model_type': metadata.get('model_type', model_name),
                'task_type': metadata.get('task_type', 'classification'),
                'file_path': metadata.get('file_path', ''),
                'has_predict_proba': hasattr(model, 'predict_proba')
            })
        
        return models_info
    
    def predict(self, model_name: str, features: List[float], 
                return_probabilities: bool = False) -> Dict[str, Any]:
        """
        Make prediction using specified model
        
        Args:
            model_name: Name of the model to use
            features: List of feature values
            return_probabilities: Whether to return prediction probabilities
            
        Returns:
            Dictionary with prediction results
        """
        try:
            if model_name not in self.models:
                available = list(self.models.keys())
                raise ValueError(f"Model '{model_name}' not found. Available models: {available}")
            
            model = self.models[model_name]
            
            # Convert features to numpy array
            X = np.array(features).reshape(1, -1)
            
            # Make prediction
            prediction = model.predict(X)[0]
            
            result = {
                'model_used': model_name,
                'prediction': prediction.tolist() if hasattr(prediction, 'tolist') else prediction,
                'timestamp': pd.Timestamp.now().isoformat()
            }
            
            # Get probabilities if available and requested
            if return_probabilities and hasattr(model, 'predict_proba'):
                try:
                    probabilities = model.predict_proba(X)[0]
                    result['probabilities'] = probabilities.tolist()
                    result['confidence'] = float(np.max(probabilities))
                    result['predicted_class'] = int(np.argmax(probabilities))
                except Exception as e:
                    logger.warning(f"Could not get probabilities: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise
    
    def predict_with_best_model(self, features: List[float],
                               task_type: str = 'classification',
                               return_probabilities: bool = False) -> Dict[str, Any]:
        """
        Make prediction using the best available model for the task
        
        Args:
            features: List of feature values
            task_type: Type of task ('classification', 'regression', 'anomaly')
            return_probabilities: Whether to return prediction probabilities
            
        Returns:
            Dictionary with prediction results
        """
        try:
            # Select best model based on task type
            if task_type == 'classification':
                # Prefer XGBoost or Random Forest for classification
                preferred_models = ['xgboost', 'random_forest', 'gradient_boosting']
            elif task_type == 'regression':
                # Prefer LSTM or Random Forest for regression
                preferred_models = ['lstm', 'random_forest_regressor', 'linear_regression']
            elif task_type == 'anomaly':
                # Prefer Autoencoder or Isolation Forest
                preferred_models = ['autoencoder', 'isolation_forest']
            else:
                preferred_models = list(self.models.keys())
            
            # Find first available preferred model
            selected_model = None
            for model_name in preferred_models:
                if model_name in self.models:
                    selected_model = model_name
                    break
            
            # If no preferred model found, use first available
            if selected_model is None and self.models:
                selected_model = list(self.models.keys())[0]
            
            if selected_model is None:
                raise ValueError("No models available for prediction")
            
            logger.info(f"Using model: {selected_model} for {task_type}")
            
            return self.predict(
                model_name=selected_model,
                features=features,
                return_probabilities=return_probabilities
            )
            
        except Exception as e:
            logger.error(f"Prediction with best model failed: {e}")
            raise
    
    def batch_predict(self, model_name: str, features_list: List[List[float]]) -> List[Dict[str, Any]]:
        """
        Make batch predictions
        
        Args:
            model_name: Name of the model to use
            features_list: List of feature lists
            
        Returns:
            List of prediction results
        """
        try:
            results = []
            
            for features in features_list:
                result = self.predict(model_name, features)
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Batch prediction failed: {e}")
            raise
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a model
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dictionary with model information
        """
        if model_name not in self.models:
            return None
        
        metadata = self.model_metadata.get(model_name, {})
        model = self.models[model_name]
        
        info = {
            'model_name': model_name,
            'model_type': metadata.get('model_type', model_name),
            'task_type': metadata.get('task_type', 'unknown'),
            'file_path': metadata.get('file_path', ''),
            'has_predict_proba': hasattr(model, 'predict_proba'),
            'has_feature_importance': hasattr(model, 'feature_importances_') or hasattr(model, 'coef_')
        }
        
        # Add metrics if available
        if 'metrics' in metadata:
            info['metrics'] = metadata['metrics']
        
        return info
    
    def reload_models(self):
        """Reload all models from disk"""
        logger.info("Reloading models...")
        self.models.clear()
        self.model_metadata.clear()
        self._load_models()


# Global prediction engine instance
prediction_engine = PredictionEngine()


def get_prediction_engine() -> PredictionEngine:
    """Get prediction engine instance"""
    return prediction_engine


def predict(features: List[float], model_name: str = None,
            task_type: str = 'classification') -> Dict[str, Any]:
    """
    Convenience function for making predictions
    
    Args:
        features: List of feature values
        model_name: Name of the model (uses best model if None)
        task_type: Type of task
        
    Returns:
        Prediction results
    """
    engine = get_prediction_engine()
    
    if model_name:
        return engine.predict(model_name, features, return_probabilities=True)
    else:
        return engine.predict_with_best_model(features, task_type, return_probabilities=True)


if __name__ == "__main__":
    # Test prediction engine
    print("Testing Prediction Engine...")
    print("="*80)
    
    engine = PredictionEngine(models_dir="data/models")
    
    # List available models
    print("\n1. Available Models:")
    models = engine.get_available_models()
    for model in models:
        print(f"  - {model['model_name']} ({model['model_type']})")
    
    if not models:
        print("  No models found. Please train models first.")
        exit(0)
    
    # Test prediction with best model
    print("\n2. Testing Prediction (Best Model):")
    test_features = [25.0, 70.0, 45.0, 6.5, 10.0, 5000.0, 15.0, 7.0, 35.0, 0.8]
    
    result = engine.predict_with_best_model(
        features=test_features,
        task_type='classification',
        return_probabilities=True
    )
    
    print(f"  Model used: {result['model_used']}")
    print(f"  Prediction: {result['prediction']}")
    if 'confidence' in result:
        print(f"  Confidence: {result['confidence']:.4f}")
    
    # Test prediction with specific model
    if len(models) > 0:
        print(f"\n3. Testing Prediction (Specific Model - {models[0]['model_name']}):")
        result = engine.predict(
            model_name=models[0]['model_name'],
            features=test_features,
            return_probabilities=True
        )
        
        print(f"  Prediction: {result['prediction']}")
        if 'confidence' in result:
            print(f"  Confidence: {result['confidence']:.4f}")
    
    # Get model info
    print("\n4. Model Information:")
    info = engine.get_model_info(models[0]['model_name'])
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\n✓ Prediction engine test complete!")