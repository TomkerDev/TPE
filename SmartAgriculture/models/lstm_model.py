"""
LSTM (Long Short-Term Memory) Model for Time Series Forecasting
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional, Tuple
import tensorflow as tf
from tensorflow import keras
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LSTMModel:
    """LSTM model for time series forecasting"""
    
    def __init__(self, sequence_length: int = 10, n_features: int = 1,
                 lstm_units: int = 64, dense_units: int = 32,
                 random_state: int = 42):
        """
        Initialize LSTM model
        
        Args:
            sequence_length: Length of input sequences
            n_features: Number of features
            lstm_units: Number of LSTM units
            dense_units: Number of dense layer units
            random_state: Random seed
        """
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.lstm_units = lstm_units
        self.dense_units = dense_units
        self.random_state = random_state
        self.model = None
        self.history = None
        
        # Set random seeds
        tf.random.set_seed(random_state)
        np.random.seed(random_state)
        
    def build_model(self) -> keras.Sequential:
        """Build LSTM model"""
        try:
            self.model = keras.Sequential([
                keras.layers.LSTM(
                    self.lstm_units,
                    input_shape=(self.sequence_length, self.n_features),
                    return_sequences=False
                ),
                keras.layers.Dense(self.dense_units, activation='relu'),
                keras.layers.Dense(1)
            ])
            
            self.model.compile(
                optimizer='adam',
                loss='mse',
                metrics=['mae']
            )
            
            logger.info(f"✓ Built LSTM model: {self.lstm_units} LSTM units, {self.dense_units} dense units")
            
            return self.model
            
        except Exception as e:
            logger.error(f"Failed to build LSTM model: {e}")
            return None
    
    def prepare_sequences(self, X: np.ndarray, y: np.ndarray = None) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Prepare sequences for LSTM
        
        Args:
            X: Features array
            y: Target array (optional)
            
        Returns:
            Tuple of (X_sequences, y_sequences)
        """
        try:
            X_seq = []
            y_seq = [] if y is not None else None
            
            for i in range(len(X) - self.sequence_length):
                X_seq.append(X[i:i + self.sequence_length])
                if y is not None:
                    y_seq.append(y[i + self.sequence_length])
            
            X_seq = np.array(X_seq)
            
            # Reshape for LSTM [samples, time steps, features]
            if len(X_seq.shape) == 2:
                X_seq = X_seq.reshape((X_seq.shape[0], X_seq.shape[1], 1))
            
            if y_seq is not None:
                y_seq = np.array(y_seq)
            
            return X_seq, y_seq
            
        except Exception as e:
            logger.error(f"Failed to prepare sequences: {e}")
            return np.array([]), None
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              validation_split: float = 0.2, epochs: int = 50,
              batch_size: int = 64, verbose: int = 1) -> bool:
        """
        Train the model
        
        Args:
            X_train: Training features
            y_train: Training target
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
            
            # Prepare sequences
            X_seq, y_seq = self.prepare_sequences(X_train, y_train)
            
            if len(X_seq) == 0:
                logger.error("No sequences prepared")
                return False
            
            # Train model
            self.history = self.model.fit(
                X_seq, y_seq,
                validation_split=validation_split,
                epochs=epochs,
                batch_size=batch_size,
                verbose=verbose
            )
            
            logger.info("✓ LSTM model trained successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to train LSTM model: {e}")
            return False
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        try:
            if self.model is None:
                logger.error("Model not trained")
                return np.array([])
            
            # Prepare sequences
            X_seq, _ = self.prepare_sequences(X)
            
            if len(X_seq) == 0:
                return np.array([])
            
            predictions = self.model.predict(X_seq, verbose=0)
            
            return predictions.flatten()
            
        except Exception as e:
            logger.error(f"Failed to make predictions: {e}")
            return np.array([])
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """Evaluate model performance"""
        try:
            if self.model is None:
                logger.error("Model not trained")
                return {}
            
            # Prepare sequences
            X_seq, y_seq = self.prepare_sequences(X_test, y_test)
            
            if len(X_seq) == 0:
                return {}
            
            # Make predictions
            y_pred = self.model.predict(X_seq, verbose=0).flatten()
            
            metrics = {
                'mse': float(mean_squared_error(y_seq, y_pred)),
                'rmse': float(np.sqrt(mean_squared_error(y_seq, y_pred))),
                'mae': float(mean_absolute_error(y_seq, y_pred)),
                'r2_score': float(r2_score(y_seq, y_pred))
            }
            
            # Add training history
            if self.history:
                metrics['training_history'] = {
                    'loss': [float(x) for x in self.history.history['loss']],
                    'val_loss': [float(x) for x in self.history.history['val_loss']],
                    'mae': [float(x) for x in self.history.history['mae']],
                    'val_mae': [float(x) for x in self.history.history['val_mae']]
                }
            
            logger.info(f"✓ Model evaluation: R²={metrics['r2_score']:.4f}, RMSE={metrics['rmse']:.4f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to evaluate model: {e}")
            return {}
    
    def save_model(self, filepath: str = 'models/lstm_model.h5'):
        """Save model to file"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Save Keras model
            self.model.save(filepath)
            
            # Save configuration
            config = {
                'sequence_length': self.sequence_length,
                'n_features': self.n_features,
                'lstm_units': self.lstm_units,
                'dense_units': self.dense_units,
                'random_state': self.random_state
            }
            
            config_filepath = filepath.replace('.h5', '_config.pkl')
            joblib.dump(config, config_filepath)
            
            logger.info(f"✓ Saved LSTM model to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def load_model(self, filepath: str = 'models/lstm_model.h5'):
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
                self.sequence_length = config.get('sequence_length', 10)
                self.n_features = config.get('n_features', 1)
                self.lstm_units = config.get('lstm_units', 64)
                self.dense_units = config.get('dense_units', 32)
                self.random_state = config.get('random_state', 42)
            
            logger.info(f"✓ Loaded LSTM model from {filepath}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False


def train_lstm(X_train: np.ndarray, y_train: np.ndarray,
               sequence_length: int = 10, lstm_units: int = 64,
               epochs: int = 50) -> LSTMModel:
    """Convenience function to train LSTM"""
    n_features = X_train.shape[1] if len(X_train.shape) > 1 else 1
    
    model = LSTMModel(
        sequence_length=sequence_length,
        n_features=n_features,
        lstm_units=lstm_units
    )
    model.build_model()
    model.train(X_train, y_train, epochs=epochs)
    return model


if __name__ == "__main__":
    from analytics.load_data import load_sample_data
    from models.preprocessing import preprocess_data
    from sklearn.model_selection import train_test_split
    
    print("Loading data...")
    df = load_sample_data()
    
    X = df.drop(['sensor_type', 'sensor_id', 'timestamp'], axis=1, errors='ignore')
    y = df['value'].values
    
    # Scale data for LSTM
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)
    y_scaled = scaler.fit_transform(y.reshape(-1, 1)).flatten()
    
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_scaled, test_size=0.2, random_state=42)
    
    print("\nTraining LSTM...")
    lstm_model = LSTMModel(sequence_length=10, n_features=X_train.shape[1], lstm_units=64)
    lstm_model.build_model()
    lstm_model.train(X_train, y_train, epochs=20, verbose=1)
    
    print("\nEvaluating...")
    metrics = lstm_model.evaluate(X_test, y_test)
    print(f"R² Score: {metrics['r2_score']:.4f}")
    print(f"RMSE: {metrics['rmse']:.4f}")