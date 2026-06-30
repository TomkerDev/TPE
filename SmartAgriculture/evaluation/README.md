# Model Evaluation Package

This package provides comprehensive tools for evaluating, comparing, and visualizing machine learning model performance in the Smart Agriculture system.

## 📦 Package Structure

```
evaluation/
├── __init__.py
├── metrics.py                      # Core metrics calculation
├── classification_metrics.py       # Classification metrics
├── regression_metrics.py           # Regression metrics
├── anomaly_metrics.py              # Anomaly detection metrics
├── confusion_matrix_plot.py        # Confusion matrix visualization
├── roc_curve_plot.py               # ROC curve visualization
├── precision_recall_plot.py        # Precision-Recall curve visualization
├── learning_curve_plot.py          # Learning curve visualization
├── compare_models.py               # Model comparison tools
├── statistical_test.py             # Statistical significance tests
├── report.py                       # Report generation
├── evaluation_pipeline.py          # End-to-end evaluation pipeline
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

### Installation

```bash
pip install -r evaluation/requirements.txt
```

### Basic Usage

```python
from evaluation import (
    evaluate_classification,
    plot_confusion_matrix,
    plot_roc_curve,
    compare_models,
    run_full_evaluation
)
import numpy as np

# Evaluate a classification model
y_true = np.array([0, 1, 2, 0, 1, 2])
y_pred = np.array([0, 1, 2, 0, 1, 1])
y_prob = np.array([[0.8, 0.1, 0.1], [0.1, 0.8, 0.1], ...])

metrics = evaluate_classification(y_true, y_pred, y_prob)
print(f"Accuracy: {metrics['accuracy']:.4f}")
```

## 📊 Metrics Modules

### 1. Core Metrics (`metrics.py`)

Unified interface for calculating metrics across all task types.

```python
from evaluation.metrics import calculate_all_metrics, format_metrics_report

# Calculate metrics for any task type
result = calculate_all_metrics(
    y_true=y_true,
    y_pred=y_pred,
    y_prob=y_prob,
    task_type='classification'  # or 'regression', 'anomaly'
)

# Format as report
report = format_metrics_report(result.metrics, "My Model")
print(report)
```

### 2. Classification Metrics (`classification_metrics.py`)

Comprehensive classification metrics including:
- Accuracy, Precision, Recall, F1-Score
- Specificity, Balanced Accuracy
- Cohen's Kappa, Matthews Correlation Coefficient
- ROC-AUC, Log Loss
- Confusion Matrix
- Per-class metrics

```python
from evaluation.classification_metrics import ClassificationMetrics, evaluate_classification

# Method 1: Using convenience function
metrics = evaluate_classification(
    y_true=y_test,
    y_pred=y_pred,
    y_prob=y_prob,
    class_names=['Class A', 'Class B', 'Class C']
)

# Method 2: Using class
evaluator = ClassificationMetrics(y_test, y_pred, y_prob)
metrics = evaluator.calculate_all()
per_class = evaluator.per_class_metrics()
```

### 3. Regression Metrics (`regression_metrics.py`)

Comprehensive regression metrics including:
- MAE, MSE, RMSE
- MAPE (Mean Absolute Percentage Error)
- R² Score, Adjusted R²
- Explained Variance
- Max Error, Median Absolute Error
- Residual analysis

```python
from evaluation.regression_metrics import RegressionMetrics, evaluate_regression

metrics = evaluate_regression(
    y_true=y_test,
    y_pred=y_pred,
    n_features=20  # for adjusted R²
)

# Get residual statistics
evaluator = RegressionMetrics(y_test, y_pred)
residual_stats = evaluator.get_residual_stats()
residuals_df = evaluator.residuals_dataframe()
```

### 4. Anomaly Detection Metrics (`anomaly_metrics.py`)

Specialized metrics for anomaly detection:
- Accuracy, Precision, Recall, F1-Score
- Specificity, False Positive Rate
- Detection Rate, False Alarm Rate
- ROC-AUC, Average Precision
- Threshold analysis

```python
from evaluation.anomaly_metrics import AnomalyMetrics, evaluate_anomaly_detection

# For Isolation Forest (predictions: 1=normal, -1=anomaly)
metrics = evaluate_anomaly_detection(
    y_true=y_test,
    y_pred=y_pred,
    anomaly_scores=anomaly_scores
)

# Get threshold analysis
evaluator = AnomalyMetrics(y_test, y_pred, anomaly_scores)
threshold_df = evaluator.get_threshold_metrics(np.linspace(-0.5, 0.5, 20))
```

## 📈 Visualization Modules

### 1. Confusion Matrix (`confusion_matrix_plot.py`)

```python
from evaluation.confusion_matrix_plot import (
    plot_confusion_matrix,
    plot_normalized_confusion_matrix,
    plot_confusion_matrix_comparison
)

# Basic confusion matrix
plot_confusion_matrix(
    y_test, y_pred,
    class_names=['A', 'B', 'C'],
    title="Model Confusion Matrix",
    save_path="cm.png"
)

# Comparison of multiple models
plot_confusion_matrix_comparison(
    y_test,
    predictions={'RF': rf_pred, 'DT': dt_pred, 'SVM': svm_pred},
    class_names=['A', 'B', 'C'],
    save_path="cm_comparison.png"
)
```

### 2. ROC Curve (`roc_curve_plot.py`)

```python
from evaluation.roc_curve_plot import (
    plot_roc_curve,
    plot_roc_comparison,
    calculate_auc_score
)

# Single ROC curve
plot_roc_curve(
    y_test, y_prob,
    title="ROC Curve",
    class_names=['A', 'B', 'C'],
    save_path="roc.png"
)

# Compare multiple models
plot_roc_comparison(
    y_test,
    probabilities={'RF': rf_prob, 'XGB': xgb_prob},
    title="Model Comparison",
    save_path="roc_comparison.png"
)

# Calculate AUC
auc = calculate_auc_score(y_test, y_prob)
```

### 3. Precision-Recall Curve (`precision_recall_plot.py`)

```python
from evaluation.precision_recall_plot import (
    plot_precision_recall_curve,
    plot_pr_comparison,
    calculate_average_precision
)

# Plot PR curve
plot_precision_recall_curve(
    y_test, y_prob,
    title="Precision-Recall Curve",
    class_names=['A', 'B', 'C'],
    save_path="pr_curve.png"
)

# Calculate Average Precision
ap = calculate_average_precision(y_test, y_prob)
```

### 4. Learning Curves (`learning_curve_plot.py`)

```python
from evaluation.learning_curve_plot import (
    plot_learning_curve,
    plot_validation_curve,
    plot_learning_curve_comparison
)

# Learning curve
plot_learning_curve(
    model, X_train, y_train,
    title="Learning Curve",
    cv=5,
    task_type='classification',
    save_path="learning_curve.png"
)

# Validation curve for hyperparameter tuning
plot_validation_curve(
    model, X_train, y_train,
    param_name='max_depth',
    param_range=np.arange(1, 21),
    title="Validation Curve",
    save_path="validation_curve.png"
)

# Compare multiple models
plot_learning_curve_comparison(
    models={'RF': rf_model, 'XGB': xgb_model},
    X=X_train, y=y_train,
    cv=5,
    save_path="lc_comparison.png"
)
```

## 🔍 Model Comparison

### Compare Models (`compare_models.py`)

```python
from evaluation.compare_models import (
    ModelComparator,
    ModelResult,
    compare_models,
    create_comparison_table
)

# Method 1: Using ModelComparator class
comparator = ModelComparator()

# Add results
for model_name, metrics in results.items():
    result = ModelResult(
        model_name=model_name,
        model_type=model_name,
        task_type='classification',
        metrics=metrics,
        training_time=training_time
    )
    comparator.add_result(result)

# Compare
comparison_df = comparator.compare('accuracy')
best_model = comparator.get_best_model('accuracy')
ranking = comparator.get_ranking('f1_score', top_n=3)

# Save results
comparator.save_results('results/comparison.json')
table = comparator.generate_comparison_table(
    metrics=['accuracy', 'precision', 'recall', 'f1_score'],
    output_file='results/table.csv'
)

# Method 2: Using convenience function
comparison = compare_models(results_dict, metric='accuracy')
```

## 📊 Statistical Testing

### Statistical Tests (`statistical_test.py`)

```python
from evaluation.statistical_test import (
    StatisticalTester,
    statistical_comparison,
    wilcoxon_test,
    paired_t_test,
    mcnemar_test
)

# Method 1: Using StatisticalTester class
tester = StatisticalTester(alpha=0.05)

# Wilcoxon test (non-parametric, paired)
result = tester.wilcoxon_test(scores1, scores2)

# Paired t-test (parametric)
result = tester.paired_t_test(scores1, scores2)

# McNemar's test (for classifier comparison)
result = tester.mcnemar_test(pred1, pred2, y_true)

# Friedman test (multiple models)
result = tester.friedman_test(scores_matrix)

# Effect size
cohens_d = tester.effect_size_cohens_d(scores1, scores2)
interpretation = tester.interpret_effect_size(cohens_d)

# Method 2: Statistical comparison
comparison_df = statistical_comparison(
    predictions={'RF': rf_pred, 'XGB': xgb_pred},
    y_true=y_test,
    test_type='wilcoxon',  # or 't_test', 'mcnemar'
    alpha=0.05
)
```

## 📄 Report Generation

### Generate Reports (`report.py`)

```python
from evaluation.report import (
    generate_evaluation_report,
    generate_markdown_report,
    generate_latex_table
)

# Generate comprehensive report
report_path = generate_evaluation_report(
    model_results=results_dict,
    task_type='classification',
    best_metric='accuracy',
    statistical_tests=statistical_results,
    visualizations=['plots/cm.png', 'plots/roc.png'],
    output_dir='results',
    format='json'  # or 'markdown', 'latex'
)

# Generate simple Markdown report
md_report = generate_markdown_report(
    model_results=results_dict,
    task_type='classification',
    output_file='results/report.md'
)

# Generate LaTeX table
latex_table = generate_latex_table(
    df=comparison_df,
    caption="Model Comparison",
    label="table:comparison"
)
```

## 🔄 End-to-End Pipeline

### Evaluation Pipeline (`evaluation_pipeline.py`)

```python
from evaluation.evaluation_pipeline import (
    EvaluationPipeline,
    EvaluationConfig,
    run_full_evaluation
)

# Method 1: Using EvaluationPipeline class
config = EvaluationConfig(
    task_type='classification',
    generate_plots=True,
    perform_statistical_tests=True,
    generate_report=True,
    report_format='markdown',
    output_dir='results/evaluation'
)

pipeline = EvaluationPipeline(config)

# Run full evaluation
report_path = pipeline.run_full_evaluation(
    models={'RF': rf_model, 'XGB': xgb_model},
    X_test=X_test,
    y_test=y_test,
    training_times={'RF': 10.5, 'XGB': 15.2},
    metadata={'RF': {'n_estimators': 100}}
)

# Get summary
summary = pipeline.get_summary()
print(summary)

# Method 2: Using convenience function
report_path = run_full_evaluation(
    models=models_dict,
    X_test=X_test,
    y_test=y_test,
    task_type='classification',
    training_times=training_times,
    output_dir='results',
    generate_plots=True,
    generate_report=True
)
```

## 📋 Complete Workflow Example

```python
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from evaluation import evaluate_classification, plot_confusion_matrix
from evaluation.evaluation_pipeline import run_full_evaluation
import time

# 1. Prepare data
X, y = make_classification(n_samples=1000, n_features=20, n_classes=3, 
                           n_informative=15, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 2. Train models
models = {
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
    'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42)
}

training_times = {}
for name, model in models.items():
    start = time.time()
    model.fit(X_train, y_train)
    training_times[name] = time.time() - start

# 3. Run full evaluation pipeline
report = run_full_evaluation(
    models=models,
    X_test=X_test,
    y_test=y_test,
    task_type='classification',
    training_times=training_times,
    output_dir='results',
    generate_plots=True,
    generate_report=True
)

print(f"Evaluation complete! Report: {report}")
```

## 🎯 Supported Task Types

### Classification
- Multi-class and binary classification
- Metrics: Accuracy, Precision, Recall, F1-Score, ROC-AUC
- Visualizations: Confusion Matrix, ROC Curve, Precision-Recall Curve

### Regression
- Continuous value prediction
- Metrics: MAE, MSE, RMSE, R², MAPE
- Visualizations: Residual plots, Learning curves

### Anomaly Detection
- Unsupervised and supervised anomaly detection
- Metrics: Detection rate, False alarm rate, F1-Score
- Visualizations: Threshold analysis, ROC curves

## 📊 Output Formats

### Reports
- **JSON**: Structured data for programmatic access
- **Markdown**: Human-readable documentation
- **LaTeX**: Academic paper integration

### Visualizations
- High-resolution PNG (300 DPI)
- Publication-ready figures
- Comparison plots

## 🔧 Configuration

### EvaluationConfig Options

```python
@dataclass
class EvaluationConfig:
    task_type: str = 'classification'  # 'classification', 'regression', 'anomaly'
    metrics: List[str] = None  # Auto-detected if None
    generate_plots: bool = True
    perform_statistical_tests: bool = True
    statistical_test_type: str = 'wilcoxon'  # 'wilcoxon', 't_test', 'mcnemar'
    alpha: float = 0.05  # Significance level
    output_dir: str = 'results'
    save_plots: bool = True
    plots_dir: str = 'plots'
    generate_report: bool = True
    report_format: str = 'markdown'  # 'json', 'markdown', 'latex'
```

## 📚 API Reference

### Key Functions

| Function | Description |
|----------|-------------|
| `evaluate_classification()` | Evaluate classification model |
| `evaluate_regression()` | Evaluate regression model |
| `evaluate_anomaly_detection()` | Evaluate anomaly detection |
| `plot_confusion_matrix()` | Plot confusion matrix |
| `plot_roc_curve()` | Plot ROC curve |
| `plot_precision_recall_curve()` | Plot PR curve |
| `plot_learning_curve()` | Plot learning curve |
| `compare_models()` | Compare multiple models |
| `statistical_comparison()` | Statistical significance tests |
| `generate_evaluation_report()` | Generate comprehensive report |
| `run_full_evaluation()` | Run complete evaluation pipeline |

## 🐛 Troubleshooting

### Common Issues

1. **Import errors**: Ensure all dependencies are installed
   ```bash
   pip install -r evaluation/requirements.txt
   ```

2. **Plot not displaying**: Set `show=False` and use `save_path`
   ```python
   plot_confusion_matrix(..., show=False, save_path="cm.png")
   ```

3. **Statistical test fails**: Ensure you have enough samples (minimum 3 for Wilcoxon)

4. **Memory issues**: Reduce number of models or use simpler visualizations

## 📖 Examples

See the `__main__` blocks in each module for complete examples:
- `metrics.py`: Basic metrics calculation
- `classification_metrics.py`: Classification evaluation
- `regression_metrics.py`: Regression evaluation
- `anomaly_metrics.py`: Anomaly detection
- `confusion_matrix_plot.py`: Confusion matrix plots
- `roc_curve_plot.py`: ROC curves
- `precision_recall_plot.py`: PR curves
- `learning_curve_plot.py`: Learning curves
- `compare_models.py`: Model comparison
- `statistical_test.py`: Statistical tests
- `report.py`: Report generation
- `evaluation_pipeline.py`: Full pipeline

## 🤝 Integration with Models Package

```python
from models import RandomForestModel, XGBoostModel
from evaluation import run_full_evaluation

# Train models
rf = RandomForestModel(n_estimators=100)
rf.build_model()
rf.train(X_train, y_train)

xgb = XGBoostModel(n_estimators=100)
xgb.build_model()
xgb.train(X_train, y_train)

# Evaluate
models = {'Random Forest': rf, 'XGBoost': xgb}
report = run_full_evaluation(
    models=models,
    X_test=X_test,
    y_test=y_test,
    task_type='classification'
)
```

## 📄 License

Part of the Smart Agriculture IoT System.