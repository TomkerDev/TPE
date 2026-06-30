"""
Autoencoder for Anomaly Detection
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional
import tensorflow as tf
from tensorflow import keras
from sklearn.metrics import mean_squared_error
import joblib
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AutoencoderModel:
    """Autoencoder for anomaly detection"""
    
    def __init__(self, input_dim: int, encoding_dim: int = 32,
                 hidden_layers: list = None, random_state: int = 42):
        """
        Initialize Autoencoder model
        
        Args:
            input_dim: Input dimension
            encoding_dim: Encoding dimension (bottleneck)
            hidden_layers: List of hidden layer sizes
            random_state: Random seed
        """
        self.input_dim = input_dim
        self.encoding_dim = encoding_dim
        self.hidden_layers = hidden_layers or [64, 32]
        self.random_state = random_state
        self.model = None
        self.encoder = None
        self.decoder = None
        self.history = None
        self.threshold = None
        
        # Set random seeds
        tf.random.set_seed(random_state)
        np.random.seed(random_state)
        
    def build_model(self) -> keras.Model:
        """Build Autoencoder model"""
        try:
            # Build encoder
            input_layer = keras.layers.Input(shape=(self.input_dim,))
            
            # Encoder layers
            encoded = input_layer
            for units in self.hidden_layers:
                encoded = keras.layers.Dense(units, activation='relu')(encoded)
            
            # Bottleneck
            encoded = keras.layers.Dense(self.encoding_dim, activation='relu', name='bottleneck')(encoded)
            
            # Decoder layers (reverse of encoder)
            decoded = encoded
            for units in reversed(self.hidden_layers):
                decoded = keras.layers.Dense(units, activation='relu')(decoded)
            
            # Output layer
            decoded = keras.layers.Dense(self.input_dim, activation='sigmoid', name='output')(decoded)
            
            # Build full autoencoder
            self.model = keras.Model(input_layer, decoded)
            
            # Build encoder model for feature extraction
            self.encoder = keras.Model(input_layer, encoded)
            
            # Compile
            self.model.compile(
                optimizer='adam',
                loss='mse',
                metrics=['mae']
            )
            
            logger.info(f"✓ Built Autoencoder: input_dim={self.input_dim}, encoding_dim={self.encoding_dim}")
            
            return self.model
            
        except Exception as e:
            logger.error(f"Failed to build Autoencoder: {e}")
            return None
    
    def train(self, X_train: np.ndarray, validation_split: float = 0.2,
              epochs: int = 100, batch_size: int = 64, verbose: int = 1) -> bool:
        """
        Train the model
        
        Args:
            X_train: Training features (normal data only)
            validation_split: Validation data split
            epochs: Number of epochs
            batch_size: Batch size
            verbose: Verbosity level
            
        Returns:
            True if training successful
        """
        try:
            if self.model is None:
                self.build_model()
            
            # Train model
            self.history = self.model.fit(
                X_train, X_train,  # Autoencoder: input = output
                validation_split=validation_split,
                epochs=epochs,
                batch_size=batch_size,
                shuffle=True,
                verbose=verbose
            )
            
            # Calculate threshold based on reconstruction error
            reconstructions = self.model.predict(X_train, verbose=0)
            reconstruction_errors = np.mean(np.power(X_train - reconstructions, 2), axis=1)
            self.threshold = np.mean(reconstruction_errors) + 2 * np.std(reconstruction_errors)
            
            logger.info(f"✓ Autoencoder trained successfully. Threshold: {self.threshold:.4f}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to train Autoencoder: {e}")
            return False
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions (1 for normal, -1 for anomaly)
        
        Args:
            X: Features
            
        Returns:
            Predictions (1 = normal, -1 = anomaly)
        """
        try:
            if self.model is None:
                logger.error("Model not trained")
                return np.array([])
            
            if self.threshold is None:
                logger.error("Threshold not set. Train the model first.")
                return np.array([])
            
            # Get reconstruction error
            reconstructions = self.model.predict(X, verbose=0)
            reconstruction_errors = np.mean(np.power(X - reconstructions, 2), axis=1)
            
            # Predict anomalies
            predictions = np.where(reconstruction_errors > self.threshold, -1, 1)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Failed to make predictions: {e}")
            return np.array([])
    
    def get_reconstruction_error(self, X: np.ndarray) -> np.ndarray:
        """
        Get reconstruction error for samples
        
        Args:
            X: Features
            
        Returns:
            Reconstruction errors
        """
        try:
            if self.model is None:
                logger.error("Model not trained")
                return np.array([])
            
            reconstructions = self.model.predict(X, verbose=0)
            reconstruction_errors = np.mean(np.power(X - reconstructions, 2), axis=1)
            
            return reconstruction_errors
            
        except Exception as e:
            logger.error(f"Failed to get reconstruction error: {e}")
            return np.array([])
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """
        Evaluate model performance
        
        Args:
            X_test: Test features
            y_test: Test target (0 = normal, 1 = anomaly)
            
        Returns:
            Dictionary with evaluation metrics
        """
        try:
            if self.model is None:
                logger.error("Model not trained")
                return {}
            
            # Make predictions
            y_pred = self.predict(X_test)
            
            # Convert predictions: -1 (anomaly) -> 1, 1 (normal) -> 0
            y_pred_binary = np.where(y_pred == -1, 1, 0)
            
            # Get reconstruction errors
            reconstruction_errors = self.get_reconstruction_error(X_test)
            
            # Compute metrics
            metrics = {
                'accuracy': float((y_pred_binary == y_test).mean()),
                'mean_reconstruction_error': float(np.mean(reconstruction_errors)),
                'std_reconstruction_error': float(np.std(reconstruction_errors)),
                'threshold': float(self.threshold),
                'anomalies_detected': int((y_pred_binary == 1).sum()),
                'normal_detected': int((y_pred_binary == 0).sum()),
                'total_samples': len(y_test)
            }
            
            logger.info(f"✓ Model evaluation: Accuracy={metrics['accuracy']:.4f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to evaluate model: {e}")
            return {}
    
    def get_anomaly_scores(self, X: np.ndarray) -> pd.DataFrame:
        """
        Get anomaly scores for samples
        
        Args:
            X: Features
            
        Returns:
            DataFrame with anomaly scores and predictions
        """
        try:
            if self.model is None:
                logger.error("Model not trained")
                return pd.DataFrame()
            
            reconstruction_errors = self.get_reconstruction_error(X)
            predictions = self.predict(X)
            
            results = pd.DataFrame({
                'reconstruction_error': reconstruction_errors,
                'is_anomaly': np.where(predictions == -1, True, False)
            })
            
            return results.sort_values('reconstruction_error', ascending=False)
            
        except Exception as e:
            logger.error(f"Failed to get anomaly scores: {e}")
            return pd.DataFrame()
    
    def encode(self, X: np.ndarray) -> np.ndarray:
        """
        Encode data using the encoder
        
        Args:
            X: Features
            
        Returns:
            Encoded representations
        """
        try:
            if self.encoder is None:
                logger.error("Encoder not built")
                return np.array([])
            
            return self.encoder.predict(X, verbose=0)
            
        except Exception as e:
            logger.error(f"Failed to encode data: {e}")
            return np.array([])
    
    def save_model(self, filepath: str = 'models/autoencoder.h5'):
        """Save model to file"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Save Keras model
            self.model.save(filepath)
            
            # Save configuration and threshold
            config = {
                'input_dim': self.input_dim,
                'encoding_dim': self.encoding_dim,
                'hidden_layers': self.hidden_layers,
                'random_state': self.random_state,
                'threshold': self.threshold
            }
            
            config_filepath = filepath.replace('.h5', '_config.pkl')
            joblib.dump(config, config_filepath)
            
            logger.info(f"✓ Saved Autoencoder model to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def load_model(self, filepath: str = 'models/autoencoder.h5'):
        """Load model from file"""
        try:
            if not os.path.exists(filepath):
                logger.error(f"Model file not found: {filepath}")
                return False
            
            # Load Keras model
            self.model = keras.models.load_model(filepath)
            
            # Load configuration
            config_filepath = filepath.replace('.h5', '_config.pkl')
            if os.path.exists(config_filepath):
                config = joblib.load(config_filepath)
                self.input_dim = config.get('input_dim', self.input_dim)
                self.encoding_dim = config.get('encoding_dim', self.encoding_dim)
                self.hidden_layers = config.get('hidden_layers', self.hidden_layers)
                self.random_state = config.get('random_state', 42)
                self.threshold = config.get('threshold')
            
            # Rebuild encoder
            bottleneck_layer = self.model.get_layer('bottleneck')
            self.encoder = keras.Model(
                self.model.input,
                bottleneck_layer.output
            )
            
            logger.info(f"✓ Loaded Autoencoder model from {filepath}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False


def train_autoencoder(X_train: np.ndarray, encoding_dim: int = 32,
                     epochs: int = 100) -> AutoencoderModel:
    """Convenience function to train Autoencoder"""
    input_dim = X_train.shape[1]
    
    model = AutoencoderModel(
        input_dim=input_dim,
        encoding_dim=encoding_dim
    )
    model.build_model()
    model.train(X_train, epochs=epochs)
    return model


if __name__ == "__main__":
    from analytics.load_data import load_sample_data
    from models.preprocessing import preprocess_data
    from sklearn.model_selection import train_test_split
    
    print("Loading data...")
    df = load_sample_data()
    
    X = df.drop(['sensor_type', 'sensor_id', 'timestamp'], axis=1, errors='ignore')
    
    # Normalize data
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)
    
    X_train, X_test = train_test_split(X_scaled, test_size=0.2, random_state=42)
    
    print("\nTraining Autoencoder...")
    ae_model = AutoencoderModel(input_dim=X_train.shape[1], encoding_dim=16)
    ae_model.build_model()
    ae_model.train(X_train, epochs=50, verbose=1)
    
    print("\nDetecting anomalies...")
    predictions = ae_model.predict(X_test)
    n_anomalies = (predictions == -1).sum()
    print(f"Detected {n_anomalies} anomalies out of {len(X_test)} samples")
    
    # Get anomaly scores
    scores = ae_model.get_anomaly_scores(X_test)
    print(f"\nTop 5 most anomalous samples:")
    print(scores.head())