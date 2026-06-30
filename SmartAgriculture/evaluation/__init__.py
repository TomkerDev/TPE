"""
Model Evaluation and Comparison Package

This package provides comprehensive tools for evaluating, comparing, and
visualizing machine learning model performance.
"""
from .metrics import (
    calculate_all_metrics,
    format_metrics_report
)

from .classification_metrics import (
    ClassificationMetrics,
    evaluate_classification
)

from .regression_metrics import (
    RegressionMetrics,
    evaluate_regression,
    calculate_mape
)

from .anomaly_metrics import (
    AnomalyMetrics,
    evaluate_anomaly_detection
)

from .confusion_matrix_plot import (
    plot_confusion_matrix,
    plot_normalized_confusion_matrix
)

from .roc_curve_plot import (
    plot_roc_curve,
    plot_multiclass_roc
)

from .precision_recall_plot import (
    plot_precision_recall_curve,
    plot_precision_recall_multiclass
)

from .learning_curve_plot import (
    plot_learning_curve,
    plot_validation_curves
)

from .compare_models import (
    compare_models,
    ModelComparator,
    create_comparison_table
)

from .statistical_test import (
    statistical_comparison,
    wilcoxon_test,
    paired_t_test,
    mcnemar_test
)

from .report import (
    generate_evaluation_report,
    generate_latex_table,
    generate_markdown_report
)

from .evaluation_pipeline import (
    EvaluationPipeline,
    run_full_evaluation
)

__all__ = [
    # Core metrics
    'calculate_all_metrics',
    'format_metrics_report',
    
    # Classification
    'ClassificationMetrics',
    'evaluate_classification',
    
    # Regression
    'RegressionMetrics',
    'evaluate_regression',
    'calculate_mape',
    
    # Anomaly detection
    'AnomalyMetrics',
    'evaluate_anomaly_detection',
    
    # Visualizations
    'plot_confusion_matrix',
    'plot_normalized_confusion_matrix',
    'plot_roc_curve',
    'plot_multiclass_roc',
    'plot_precision_recall_curve',
    'plot_precision_recall_multiclass',
    'plot_learning_curve',
    'plot_validation_curves',
    
    # Comparison
    'compare_models',
    'ModelComparator',
    'create_comparison_table',
    
    # Statistical tests
    'statistical_comparison',
    'wilcoxon_test',
    'paired_t_test',
    'mcnemar_test',
    
    # Reports
    'generate_evaluation_report',
    'generate_latex_table',
    'generate_markdown_report',
    
    # Pipeline
    'EvaluationPipeline',
    'run_full_evaluation'
]

__version__ = '1.0.0'