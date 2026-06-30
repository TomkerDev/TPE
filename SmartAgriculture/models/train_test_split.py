"""
Train/Test Split Module
Handles data splitting for machine learning
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Optional, Tuple
from sklearn.model_selection import train_test_split, cross_val_score, learning_curve
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TrainTestSplit:
    """Handles train/test splitting and validation"""
    
    def __init__(self, test_size: float = 0.2, random_state: int = 42, shuffle: bool = True):
        """
        Initialize train/test splitter
        
        Args:
            test_size: Proportion of data for testing
            random_state: Random seed
            shuffle: Whether to shuffle data
        """
        self.test_size = test_size
        self.random_state = random_state
        self.shuffle = shuffle
        
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        
    def split(self, X: pd.DataFrame, y: pd.Series) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Split data into train and test sets
        
        Args:
            X: Features
            y: Target
            
        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        try:
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                X, y,
                test_size=self.test_size,
                random_state=self.random_state,
                shuffle=self.shuffle
            )
            
            logger.info(f"✓ Split data: Train={len(self.X_train)}, Test={len(self.X_test)}")
            logger.info(f"  Train shape: {self.X_train.shape}, Test shape: {self.X_test.shape}")
            
            return self.X_train, self.X_test, self.y_train, self.y_test
            
        except Exception as e:
            logger.error(f"Failed to split data: {e}")
            return None, None, None, None
    
    def get_split_data(self) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[np.ndarray], Optional[np.ndarray]]:
        """Get split data"""
        return self.X_train, self.X_test, self.y_train, self.y_test
    
    def cross_validate(self, model, X: np.ndarray, y: np.ndarray, 
                      cv: int = 5, scoring: str = 'accuracy') -> Dict[str, Any]:
        """
        Perform cross-validation
        
        Args:
            model: Model to validate
            X: Features
            y: Target
            cv: Number of folds
            scoring: Scoring metric
            
        Returns:
            Dictionary with cross-validation results
        """
        try:
            scores = cross_val_score(model, X, y, cv=cv, scoring=scoring)
            
            results = {
                'scores': scores.tolist(),
                'mean_score': float(scores.mean()),
                'std_score': float(scores.std()),
                'cv_folds': cv,
                'scoring': scoring
            }
            
            logger.info(f"✓ Cross-validation: {scoring}={scores.mean():.4f} (+/- {scores.std():.4f})")
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to cross-validate: {e}")
            return {}
    
    def grid_search(self, model, param_grid: Dict[str, List], 
                   X: np.ndarray, y: np.ndarray,
                   cv: int = 5, scoring: str = 'accuracy') -> Dict[str, Any]:
        """
        Perform grid search for hyperparameter tuning
        
        Args:
            model: Model to tune
            param_grid: Parameter grid
            X: Features
            y: Target
            cv: Number of folds
            scoring: Scoring metric
            
        Returns:
            Dictionary with grid search results
        """
        try:
            grid_search = GridSearchCV(
                model, param_grid, cv=cv, scoring=scoring,
                verbose=1, n_jobs=-1
            )
            
            grid_search.fit(X, y)
            
            results = {
                'best_params': grid_search.best_params_,
                'best_score': float(grid_search.best_score_),
                'best_estimator': grid_search.best_estimator_,
                'cv_results': {
                    'mean_test_scores': grid_search.cv_results_['mean_test_score'].tolist(),
                    'std_test_scores': grid_search.cv_results_['std_test_score'].tolist()
                }
            }
            
            logger.info(f"✓ Grid search best score: {grid_search.best_score_:.4f}")
            logger.info(f"  Best params: {grid_search.best_params_}")
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to perform grid search: {e}")
            return {}
    
    def randomized_search(self, model, param_distributions: Dict[str, List],
                         X: np.ndarray, y: np.ndarray,
                         n_iter: int = 100, cv: int = 5,
                         scoring: str = 'accuracy') -> Dict[str, Any]:
        """
        Perform randomized search for hyperparameter tuning
        
        Args:
            model: Model to tune
            param_distributions: Parameter distributions
            X: Features
            y: Target
            n_iter: Number of iterations
            cv: Number of folds
            scoring: Scoring metric
            
        Returns:
            Dictionary with search results
        """
        try:
            random_search = RandomizedSearchCV(
                model, param_distributions, n_iter=n_iter, cv=cv,
                scoring=scoring, verbose=1, n_jobs=-1, random_state=42
            )
            
            random_search.fit(X, y)
            
            results = {
                'best_params': random_search.best_params_,
                'best_score': float(random_search.best_score_),
                'best_estimator': random_search.best_estimator_
            }
            
            logger.info(f"✓ Randomized search best score: {random_search.best_score_:.4f}")
            logger.info(f"  Best params: {random_search.best_params_}")
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to perform randomized search: {e}")
            return {}
    
    def get_learning_curve(self, model, X: np.ndarray, y: np.ndarray,
                          cv: int = 5, train_sizes: List[float] = None) -> Dict[str, Any]:
        """
        Generate learning curve data
        
        Args:
            model: Model to evaluate
            X: Features
            y: Target
            cv: Number of folds
            train_sizes: Training set sizes (if None, auto-generated)
            
        Returns:
            Dictionary with learning curve data
        """
        try:
            if train_sizes is None:
                train_sizes = np.linspace(0.1, 1.0, 10)
            
            train_sizes_abs, train_scores, test_scores = learning_curve(
                model, X, y, cv=cv, train_sizes=train_sizes,
                n_jobs=-1, verbose=0
            )
            
            results = {
                'train_sizes': train_sizes_abs.tolist(),
                'train_scores_mean': train_scores.mean(axis=1).tolist(),
                'train_scores_std': train_scores.std(axis=1).tolist(),
                'test_scores_mean': test_scores.mean(axis=1).tolist(),
                'test_scores_std': test_scores.std(axis=1).tolist()
            }
            
            logger.info("✓ Generated learning curve data")
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to generate learning curve: {e}")
            return {}


def split_data(X: pd.DataFrame, y: pd.Series, 
               test_size: float = 0.2, 
               random_state: int = 42,
               shuffle: bool = True) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Convenience function to split data
    
    Args:
        X: Features
        y: Target
        test_size: Test set size
        random_state: Random seed
        shuffle: Whether to shuffle
        
    Returns:
        Tuple of (X_train, X_test, y_train, y_test)
    """
    splitter = TrainTestSplit(test_size, random_state, shuffle)
    return splitter.split(X, y)


if __name__ == "__main__":
    # Test train/test split
    from analytics.load_data import load_sample_data
    from models.dataset import Dataset
    
    print("Loading sample data...")
    df = load_sample_data()
    
    # Prepare features
    X = df.drop(['sensor_type', 'sensor_id', 'timestamp'], axis=1, errors='ignore')
    y = df['sensor_type']
    
    print(f"\nDataset shape: X={X.shape}, y={y.shape}")
    
    # Split data
    print("\nSplitting data...")
    splitter = TrainTestSplit(test_size=0.2, random_state=42)
    X_train, X_test, y_train, y_test = splitter.split(X, y)
    
    print(f"\nTrain: X={X_train.shape}, y={y_train.shape}")
    print(f"Test: X={X_test.shape}, y={y_test.shape}")
    
    # Test cross-validation
    print("\nTesting cross-validation...")
    from sklearn.ensemble import RandomForestClassifier
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    
    cv_results = splitter.cross_validate(model, X_train, y_train, cv=3)
    print(f"CV Results: {cv_results['mean_score']:.4f} (+/- {cv_results['std_score']:.4f})")