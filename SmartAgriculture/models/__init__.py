"""
Machine Learning Models Package

This package contains various machine learning models for classification,
regression, and anomaly detection tasks.
"""
from .random_forest import RandomForestModel, train_random_forest
from .decision_tree import DecisionTreeModel, train_decision_tree
from .svm import SVMModel, train_svm
from .knn import KNNModel, train_knn
from .xgboost_model import XGBoostModel, train_xgboost
from .linear_regression import LinearRegressionModel, train_linear_regression
from .random_forest_regressor import RandomForestRegressorModel, train_random_forest_regressor
from .lstm_model import LSTMModel, train_lstm
from .isolation_forest import IsolationForestModel, train_isolation_forest
from .autoencoder import AutoencoderModel, train_autoencoder
from .save_model import ModelSaver, save_model, load_model, save_metrics, load_metrics, model_saver
from .training_pipeline import TrainingPipeline, TrainingResult, train_multiple_models

__all__ = [
    # Classification models
    'RandomForestModel',
    'train_random_forest',
    'DecisionTreeModel',
    'train_decision_tree',
    'SVMModel',
    'train_svm',
    'KNNModel',
    'train_knn',
    'XGBoostModel',
    'train_xgboost',
    
    # Regression models
    'LinearRegressionModel',
    'train_linear_regression',
    'RandomForestRegressorModel',
    'train_random_forest_regressor',
    'LSTMModel',
    'train_lstm',
    
    # Anomaly detection models
    'IsolationForestModel',
    'train_isolation_forest',
    'AutoencoderModel',
    'train_autoencoder',
    
    # Utilities
    'ModelSaver',
    'save_model',
    'load_model',
    'save_metrics',
    'load_metrics',
    'model_saver',
    'TrainingPipeline',
    'TrainingResult',
    'train_multiple_models'
]

__version__ = '1.0.0'