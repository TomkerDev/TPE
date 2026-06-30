"""
Evaluation Report Generation Module

This module provides tools for generating comprehensive evaluation reports.
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import json
import os
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class EvaluationReport:
    """Container for evaluation report data"""
    report_id: str
    timestamp: str
    task_type: str
    models: List[str]
    best_model: str
    best_metric: str
    best_score: float
    comparison_table: pd.DataFrame
    detailed_metrics: Dict[str, Dict[str, Any]]
    statistical_tests: Optional[Dict[str, Any]] = None
    visualizations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


def generate_evaluation_report(model_results: Dict[str, Any],
                              task_type: str = 'classification',
                              best_metric: str = None,
                              statistical_tests: Dict[str, Any] = None,
                              visualizations: List[str] = None,
                              output_dir: str = 'results',
                              format: str = 'json') -> str:
    """
    Generate comprehensive evaluation report
    
    Args:
        model_results: Dictionary of model results
        task_type: Type of task ('classification', 'regression', 'anomaly')
        best_metric: Metric to determine best model
        statistical_tests: Statistical test results (optional)
        visualizations: List of visualization file paths (optional)
        output_dir: Directory to save report
        format: Output format ('json', 'markdown', 'latex')
        
    Returns:
        Path to generated report
    """
    try:
        from .compare_models import ModelComparator, ModelResult
        
        # Create comparator
        comparator = ModelComparator()
        
        # Convert results to ModelResult objects
        for model_name, result_data in model_results.items():
            result = ModelResult(
                model_name=model_name,
                model_type=result_data.get('model_type', model_name),
                task_type=task_type,
                metrics=result_data.get('metrics', {}),
                training_time=result_data.get('training_time', 0.0),
                metadata=result_data.get('metadata', {})
            )
            comparator.add_result(result)
        
        # Determine best metric if not provided
        if best_metric is None:
            if task_type == 'classification':
                best_metric = 'accuracy'
            elif task_type == 'regression':
                best_metric = 'r2_score'
            elif task_type == 'anomaly':
                best_metric = 'f1_score'
        
        # Get best model
        best_result = comparator.get_best_model(best_metric)
        best_model = best_result.model_name if best_result else 'N/A'
        best_score = best_result.metrics.get(best_metric, 0.0) if best_result else 0.0
        
        # Get comparison table
        comparison_table = comparator.compare_multiple_metrics()
        
        # Get detailed metrics
        detailed_metrics = {
            name: result.metrics 
            for name, result in comparator.results.items()
        }
        
        # Create report
        report = EvaluationReport(
            report_id=datetime.now().strftime('%Y%m%d_%H%M%S'),
            timestamp=datetime.now().isoformat(),
            task_type=task_type,
            models=list(model_results.keys()),
            best_model=best_model,
            best_metric=best_metric,
            best_score=best_score,
            comparison_table=comparison_table,
            detailed_metrics=detailed_metrics,
            statistical_tests=statistical_tests,
            visualizations=visualizations or []
        )
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate report file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'json':
            filepath = os.path.join(output_dir, f'evaluation_report_{timestamp}.json')
            _save_json_report(report, filepath)
        elif format == 'markdown':
            filepath = os.path.join(output_dir, f'evaluation_report_{timestamp}.md')
            _save_markdown_report(report, filepath)
        elif format == 'latex':
            filepath = os.path.join(output_dir, f'evaluation_report_{timestamp}.tex')
            _save_latex_report(report, filepath)
        else:
            raise ValueError(f"Unknown format: {format}")
        
        logger.info(f"✓ Generated evaluation report: {filepath}")
        
        return filepath
        
    except Exception as e:
        logger.error(f"Failed to generate evaluation report: {e}")
        return ""


def _save_json_report(report: EvaluationReport, filepath: str):
    """Save report in JSON format"""
    try:
        report_dict = {
            'report_id': report.report_id,
            'timestamp': report.timestamp,
            'task_type': report.task_type,
            'models': report.models,
            'best_model': report.best_model,
            'best_metric': report.best_metric,
            'best_score': report.best_score,
            'comparison_table': report.comparison_table.to_dict(orient='records'),
            'detailed_metrics': report.detailed_metrics,
            'statistical_tests': report.statistical_tests,
            'visualizations': report.visualizations,
            'metadata': report.metadata
        }
        
        with open(filepath, 'w') as f:
            json.dump(report_dict, f, indent=2)
            
    except Exception as e:
        logger.error(f"Failed to save JSON report: {e}")


def _save_markdown_report(report: EvaluationReport, filepath: str):
    """Save report in Markdown format"""
    try:
        lines = []
        
        # Header
        lines.append("# Model Evaluation Report")
        lines.append("")
        lines.append(f"**Report ID:** {report.report_id}")
        lines.append(f"**Generated:** {report.timestamp}")
        lines.append(f"**Task Type:** {report.task_type}")
        lines.append("")
        
        # Summary
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **Models Evaluated:** {len(report.models)}")
        lines.append(f"- **Best Model:** {report.best_model}")
        lines.append(f"- **Best Metric:** {report.best_metric} = {report.best_score:.4f}")
        lines.append("")
        
        # Model Comparison Table
        lines.append("## Model Comparison")
        lines.append("")
        lines.append(report.comparison_table.to_markdown(index=False))
        lines.append("")
        
        # Detailed Metrics
        lines.append("## Detailed Metrics")
        lines.append("")
        
        for model_name in report.models:
            lines.append(f"### {model_name}")
            lines.append("")
            
            if model_name in report.detailed_metrics:
                metrics = report.detailed_metrics[model_name]
                
                for metric_name, metric_value in metrics.items():
                    if isinstance(metric_value, (int, float)):
                        lines.append(f"- **{metric_name}:** {metric_value:.4f}")
                    elif isinstance(metric_value, str):
                        lines.append(f"- **{metric_name}:** {metric_value}")
                    elif isinstance(metric_value, list):
                        lines.append(f"- **{metric_name}:** [{len(metric_value)} values]")
                    else:
                        lines.append(f"- **{metric_name}:** {metric_value}")
                
                lines.append("")
        
        # Statistical Tests
        if report.statistical_tests:
            lines.append("## Statistical Tests")
            lines.append("")
            
            for test_name, test_result in report.statistical_tests.items():
                lines.append(f"### {test_name}")
                lines.append("")
                
                if isinstance(test_result, dict):
                    for key, value in test_result.items():
                        if isinstance(value, (int, float)):
                            lines.append(f"- **{key}:** {value:.4f}")
                        else:
                            lines.append(f"- **{key}:** {value}")
                elif isinstance(test_result, pd.DataFrame):
                    lines.append(test_result.to_markdown(index=False))
                
                lines.append("")
        
        # Visualizations
        if report.visualizations:
            lines.append("## Visualizations")
            lines.append("")
            
            for viz_path in report.visualizations:
                viz_name = os.path.basename(viz_path)
                lines.append(f"- {viz_name}")
            
            lines.append("")
        
        # Write to file
        with open(filepath, 'w') as f:
            f.write('\n'.join(lines))
            
    except Exception as e:
        logger.error(f"Failed to save Markdown report: {e}")


def _save_latex_report(report: EvaluationReport, filepath: str):
    """Save report in LaTeX format"""
    try:
        lines = []
        
        # Document header
        lines.append(r"\documentclass{article}")
        lines.append(r"\usepackage{booktabs}")
        lines.append(r"\usepackage{graphicx}")
        lines.append(r"\usepackage{hyperref}")
        lines.append(r"\title{Model Evaluation Report}")
        lines.append(r"\author{Smart Agriculture System}")
        lines.append(r"\date{" + report.timestamp + r"}")
        lines.append(r"\begin{document}")
        lines.append(r"\maketitle")
        lines.append("")
        
        # Summary
        lines.append(r"\section{Summary}")
        lines.append("")
        lines.append(f"Task Type: {report.task_type}")
        lines.append(f"Models Evaluated: {len(report.models)}")
        lines.append(f"Best Model: \\textbf{{{report.best_model}}}")
        lines.append(f"Best {report.best_metric}: {report.best_score:.4f}")
        lines.append("")
        
        # Model Comparison Table
        lines.append(r"\section{Model Comparison}")
        lines.append("")
        lines.append(report.comparison_table.to_latex(index=False, escape=True))
        lines.append("")
        
        # Detailed Metrics
        lines.append(r"\section{Detailed Metrics}")
        lines.append("")
        
        for model_name in report.models:
            lines.append(rf"\subsection{{{model_name}}}")
            lines.append("")
            
            if model_name in report.detailed_metrics:
                metrics = report.detailed_metrics[model_name]
                
                for metric_name, metric_value in metrics.items():
                    if isinstance(metric_value, (int, float)):
                        lines.append(f"{metric_name}: {metric_value:.4f}\\\\")
                    else:
                        lines.append(f"{metric_name}: {metric_value}\\\\")
                
                lines.append("")
        
        # Document footer
        lines.append(r"\end{document}")
        
        # Write to file
        with open(filepath, 'w') as f:
            f.write('\n'.join(lines))
            
    except Exception as e:
        logger.error(f"Failed to save LaTeX report: {e}")


def generate_latex_table(df: pd.DataFrame, 
                        caption: str = "Model Comparison",
                        label: str = "table:comparison") -> str:
    """
    Generate LaTeX table from DataFrame
    
    Args:
        df: DataFrame to convert
        caption: Table caption
        label: Table label for referencing
        
    Returns:
        LaTeX table string
    """
    try:
        latex = df.to_latex(index=False, escape=True, caption=caption, label=label)
        return latex
    except Exception as e:
        logger.error(f"Failed to generate LaTeX table: {e}")
        return ""


def generate_markdown_report(model_results: Dict[str, Any],
                            task_type: str = 'classification',
                            output_file: str = None) -> str:
    """
    Generate Markdown report (convenience function)
    
    Args:
        model_results: Dictionary of model results
        task_type: Type of task
        output_file: Output file path (optional)
        
    Returns:
        Report as string
    """
    try:
        from .compare_models import ModelComparator, ModelResult
        
        # Create comparator
        comparator = ModelComparator()
        
        # Convert results
        for model_name, result_data in model_results.items():
            result = ModelResult(
                model_name=model_name,
                model_type=result_data.get('model_type', model_name),
                task_type=task_type,
                metrics=result_data.get('metrics', {}),
                training_time=result_data.get('training_time', 0.0)
            )
            comparator.add_result(result)
        
        # Generate report
        lines = []
        lines.append("# Model Evaluation Report")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Task Type:** {task_type}")
        lines.append("")
        
        # Summary
        lines.append("## Summary")
        lines.append("")
        lines.append(f"Total models evaluated: {len(model_results)}")
        
        best = comparator.get_best_model()
        if best:
            lines.append(f"Best model: **{best.model_name}**")
        lines.append("")
        
        # Comparison table
        lines.append("## Model Comparison")
        lines.append("")
        comparison = comparator.compare_multiple_metrics()
        lines.append(comparison.to_markdown(index=False))
        lines.append("")
        
        # Detailed results
        lines.append("## Detailed Results")
        lines.append("")
        
        for model_name, result in comparator.results.items():
            lines.append(f"### {model_name}")
            lines.append("")
            
            for metric, value in result.metrics.items():
                if isinstance(value, (int, float)):
                    lines.append(f"- {metric}: {value:.4f}")
                else:
                    lines.append(f"- {metric}: {value}")
            
            lines.append("")
        
        report = '\n'.join(lines)
        
        # Save if file provided
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w') as f:
                f.write(report)
            logger.info(f"✓ Saved Markdown report to {output_file}")
        
        return report
        
    except Exception as e:
        logger.error(f"Failed to generate Markdown report: {e}")
        return ""


if __name__ == "__main__":
    # Test report generation
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    from evaluation.classification_metrics import evaluate_classification
    import time
    
    print("Testing report generation...")
    
    # Generate sample data
    X, y = make_classification(n_samples=1000, n_features=20, n_classes=3,
                               n_informative=15, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train models
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42)
    }
    
    model_results = {}
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        start_time = time.time()
        
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)
        
        training_time = time.time() - start_time
        
        # Calculate metrics
        metrics = evaluate_classification(y_test, y_pred, y_prob)
        
        model_results[name] = {
            'model_type': name,
            'metrics': metrics,
            'training_time': training_time
        }
    
    # Generate JSON report
    print("\n1. Generating JSON report...")
    json_report = generate_evaluation_report(
        model_results,
        task_type='classification',
        best_metric='accuracy',
        output_dir='results',
        format='json'
    )
    print(f"JSON report: {json_report}")
    
    # Generate Markdown report
    print("\n2. Generating Markdown report...")
    md_report = generate_evaluation_report(
        model_results,
        task_type='classification',
        best_metric='accuracy',
        output_dir='results',
        format='markdown'
    )
    print(f"Markdown report: {md_report}")
    
    # Generate LaTeX report
    print("\n3. Generating LaTeX report...")
    latex_report = generate_evaluation_report(
        model_results,
        task_type='classification',
        best_metric='accuracy',
        output_dir='results',
        format='latex'
    )
    print(f"LaTeX report: {latex_report}")
    
    # Generate simple Markdown report
    print("\n4. Generating simple Markdown report...")
    simple_md = generate_markdown_report(
        model_results,
        task_type='classification',
        output_file='results/simple_report.md'
    )
    print(f"Simple Markdown report generated")
    print("\n" + "="*80)
    print(simple_md[:500] + "...")