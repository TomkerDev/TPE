# Machine Learning Models Package

This package provides a comprehensive collection of machine learning models for classification, regression, and anomaly detection tasks in the Smart Agriculture system.

## 📦 Available Models

### Classification Models

1. **Random Forest** (`random_forest.py`)
   - Ensemble method using multiple decision trees
   - Default: 300 trees, max_depth=20
   - Supports feature importance analysis

2. **Decision Tree** (`decision_tree.py`)
   - Single decision tree classifier
   - Default: max_depth=15
   - Highly interpretable

3. **Support Vector Machine (SVM)** (`svm.py`)
   - Kernel-based classifier
   - Supports multiple kernels (rbf, linear, poly, sigmoid)
   - Probability estimates available

4. **K-Nearest Neighbors (KNN)** (`knn.py`)
   - Instance-based learning
   - Default: k=5 neighbors
   - Supports multiple distance metrics

5. **XGBoost** (`xgboost_model.py`)
   - Gradient boosting framework
   - Default: 400 estimators, learning_rate=0.05
   - High performance and speed

### Regression Models

1. **Linear Regression** (`linear_regression.py`)
   - Simple linear model
   - Provides coefficient analysis
   - Fast training and prediction

2. **Random Forest Regressor** (`random_forest_regressor.py`)
   - Ensemble regression method
   - Default: 300 trees, max_depth=20
   - Feature importance available

3. **LSTM** (`lstm_model.py`)
   - Long Short-Term Memory network
   - For time series forecasting
   - Requires TensorFlow
   - Sequence-based predictions

### Anomaly Detection Models

1. **Isolation Forest** (`isolation_forest.py`)
   - Unsupervised anomaly detection
   - Default: 200 trees, contamination=0.1
   - No labels required for training

2. **Autoencoder** (`autoencoder.py`)
   - Neural network-based anomaly detection
   - Learns to reconstruct normal data
   - Requires TensorFlow
   - Automatic threshold calculation

## 🚀 Quick Start

### Installation

```bash
# Install all dependencies
pip install -r requirements.txt

# Or install individually
pip install scikit-learn xgboost tensorflow pandas numpy joblib
```

### Basic Usage

```python
from models import RandomForestModel, train_and_evaluate
from models.training_pipeline import TrainingPipeline
import numpy as np

# Prepare your data
X_train = np.array([[...], [...], ...])
y_train = np.array([...])
X_test = np.array([[...], [...], ...])
y_test = np.array([...])

# Method 1: Use individual model
model = RandomForestModel(n_estimators=100)
model.build_model()
model.train(X_train, y_train)
metrics = model.evaluate(X_test, y_test)
print(f"Accuracy: {metrics['accuracy']:.4f}")

# Method 2: Use convenience function
model = train_random_forest(X_train, y_train, n_estimators=100)
metrics = model.evaluate(X_test, y_test)

# Method 3: Use training pipeline for multiple models
pipeline = TrainingPipeline()
pipeline.train_and_evaluate(
    model=RandomForestModel(n_estimators=100),
    model_name='rf_model',
    model_type='Random Forest',
    X_train=X_train,
    y_train=y_train,
    X_test=X_test,
    y_test=y_test,
    task_type='classification'
)

# Compare models
comparison = pipeline.compare_models()
print(comparison)

# Get best model
best = pipeline.get_best_model()
print(f"Best model: {best.model_name}")
```

### Training Multiple Models

```python
from models import (
    RandomForestModel, DecisionTreeModel, XGBoostModel
)

# Define models configuration
models_config = [
    {
        'class': RandomForestModel,
        'name': 'random_forest',
        'type': 'Random Forest',
        'params': {'n_estimators': 100, 'max_depth': 20}
    },
    {
        'class': DecisionTreeModel,
        'name': 'decision_tree',
        'type': 'Decision Tree',
        'params': {'max_depth': 10}
    },
    {
        'class': XGBoostModel,
        'name': 'xgboost',
        'type': 'XGBoost',
        'params': {'n_estimators': 100, 'learning_rate': 0.05}
    }
]

# Train all models
from models.training_pipeline import train_multiple_models

pipeline = train_multiple_models(
    X_train=X_train,
    y_train=y_train,
    X_test=X_test,
    y_test=y_test,
    models_config=models_config,
    task_type='classification'
)

# Generate report
report = pipeline.generate_report()
print(report)

# Save results
pipeline.save_results('experiment_results.json')
```

### Model Persistence

```python
from models import save_model, load_model, save_metrics, load_metrics

# Save model
model_path = save_model(
    model=my_model,
    model_name='my_best_model',
    metadata={'accuracy': 0.95, 'training_date': '2024-01-01'}
)

# Load model
loaded_data = load_model('models/my_best_model.pkl')
my_model = loaded_data['model']
metadata = loaded_data['metadata']

# Save metrics
save_metrics(
    metrics={'accuracy': 0.95, 'f1_score': 0.94},
    model_name='my_best_model'
)

# Load metrics
metrics = load_metrics('my_best_model')
```

### Anomaly Detection

```python
from models import IsolationForestModel, AutoencoderModel

# Method 1: Isolation Forest
iso_model = IsolationForestModel(n_estimators=200, contamination=0.1)
iso_model.build_model()
iso_model.train(X_train)  # No labels needed

# Predict anomalies
predictions = iso_model.predict(X_test)  # 1=normal, -1=anomaly
anomaly_scores = iso_model.get_anomaly_scores(X_test)

# Method 2: Autoencoder
ae_model = AutoencoderModel(
    input_dim=X_train.shape[1],
    encoding_dim=16,
    hidden_layers=[64, 32]
)
ae_model.build_model()
ae_model.train(X_train, epochs=50)

# Detect anomalies
predictions = ae_model.predict(X_test)
scores = ae_model.get_anomaly_scores(X_test)
```

### Time Series Forecasting with LSTM

```python
from models import LSTMModel
from sklearn.preprocessing import MinMaxScaler

# Prepare data
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)
y_scaled = scaler.fit_transform(y.reshape(-1, 1)).flatten()

# Create and train LSTM
lstm_model = LSTMModel(
    sequence_length=10,
    n_features=X_scaled.shape[1],
    lstm_units=64,
    dense_units=32
)
lstm_model.build_model()
lstm_model.train(X_train, y_train, epochs=50, batch_size=64)

# Make predictions
predictions = lstm_model.predict(X_test)
metrics = lstm_model.evaluate(X_test, y_test)

# Save model (uses H5 format)
lstm_model.save_model('models/lstm_model.h5')
```

## 📊 Model Comparison

The `TrainingPipeline` class automatically compares all trained models:

```python
pipeline = TrainingPipeline()

# Train multiple models
for config in models_config:
    pipeline.train_and_evaluate(...)

# Compare by different metrics
comparison = pipeline.compare_models(metric='accuracy')
comparison = pipeline.compare_models(metric='f1_score')
comparison = pipeline.compare_models(metric='training_time')

# Generate comprehensive report
report = pipeline.generate_report('training_report.txt')
```

## 🔧 Model Features

All models include:
- ✅ Consistent API (build_model, train, predict, evaluate)
- ✅ Model persistence (save/load)
- ✅ Comprehensive logging
- ✅ Error handling
- ✅ Type hints
- ✅ Documentation

### Common Methods

```python
# Build model
model.build_model()

# Train model
model.train(X_train, y_train)

# Make predictions
predictions = model.predict(X_test)

# Evaluate model
metrics = model.evaluate(X_test, y_test)

# Get feature importance (if available)
importance = model.get_feature_importance(feature_names)

# Save model
model.save_model('path/to/model.pkl')

# Load model
model.load_model('path/to/model.pkl')
```

## 📈 Evaluation Metrics

### Classification
- Accuracy
- Precision
- Recall
- F1-Score
- Confusion Matrix
- Classification Report

### Regression
- MSE (Mean Squared Error)
- RMSE (Root Mean Squared Error)
- MAE (Mean Absolute Error)
- R² Score

### Anomaly Detection
- Accuracy
- Anomalies Detected
- Normal Detected
- Reconstruction Error (Autoencoder)
- Anomaly Scores

## 🎯 Best Practices

1. **Data Preprocessing**: Always preprocess your data before training
   ```python
   from models.preprocessing import preprocess_data
   X_train_processed, X_test_processed = preprocess_data(X_train, X_test)
   ```

2. **Train-Test Split**: Use proper splitting
   ```python
   from models.train_test_split import split_data
   X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2)
   ```

3. **Model Selection**: Compare multiple models
   ```python
   pipeline = train_multiple_models(...)
   best_model = pipeline.get_best_model()
   ```

4. **Save Best Model**: Always save your best performing model
   ```python
   save_model(best_model.model, 'production_model')
   ```

5. **Monitor Performance**: Track metrics over time
   ```python
   save_metrics(metrics, 'model_v1')
   ```

## 📝 Example Workflows

### Complete Training Workflow

```python
from analytics.load_data import load_sample_data
from models.preprocessing import preprocess_data
from models.training_pipeline import train_multiple_models

# 1. Load data
df = load_sample_data()
X = df.drop(['target'], axis=1)
y = df['target']

# 2. Split data
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# 3. Preprocess
X_train_processed, X_test_processed = preprocess_data(X_train, X_test)

# 4. Define models
models_config = [
    {'class': RandomForestModel, 'name': 'rf', 'params': {'n_estimators': 100}},
    {'class': XGBoostModel, 'name': 'xgb', 'params': {'n_estimators': 100}},
]

# 5. Train and compare
pipeline = train_multiple_models(
    X_train_processed, y_train,
    X_test_processed, y_test,
    models_config,
    task_type='classification'
)

# 6. Get best model
best = pipeline.get_best_model()
print(f"Best model: {best.model_name}")

# 7. Save results
pipeline.save_results()
best.model.save_model('models/best_model.pkl')
```

## 🐛 Troubleshooting

### Common Issues

1. **TensorFlow not found**: Install TensorFlow for LSTM and Autoencoder
   ```bash
   pip install tensorflow>=2.15.0
   ```

2. **XGBoost errors**: Ensure compatible version
   ```bash
   pip install xgboost>=2.0.0
   ```

3. **Memory issues**: Reduce model complexity
   ```python
   model = RandomForestModel(n_estimators=50, max_depth=10)
   ```

4. **Slow training**: Use smaller datasets or simpler models
   ```python
   model = DecisionTreeModel(max_depth=5)
   ```

## 📚 Additional Resources

- [Scikit-learn Documentation](https://scikit-learn.org/)
- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [TensorFlow Documentation](https://www.tensorflow.org/)
- [Project Documentation](../README.md)

## 🤝 Contributing

When adding new models:
1. Follow the existing API pattern
2. Include all standard methods (build, train, predict, evaluate, save, load)
3. Add comprehensive error handling
4. Include logging
5. Update this README
6. Add to `__init__.py`

## 📄 License

Part of the Smart Agriculture IoT System.