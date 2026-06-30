"""
Statistical Validation Module

This module provides tools for statistical validation of experimental results.
"""
import numpy as np
import pandas as pd
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
from scipy import stats

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class StatisticalTestResult:
    """Container for statistical test results"""
    test_name: str
    test_type: str
    statistic: float
    p_value: float
    is_significant: bool
    alpha: float
    interpretation: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ComparisonResult:
    """Container for comparison results"""
    model_a: str
    model_b: str
    test_type: str
    statistic: float
    p_value: float
    is_significant: bool
    effect_size: float
    winner: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class StatisticalValidator:
    """Perform statistical validation on experimental results"""
    
    def __init__(self, alpha: float = 0.05):
        """
        Initialize statistical validator
        
        Args:
            alpha: Significance level (default: 0.05)
        """
        self.alpha = alpha
        self.results: List[StatisticalTestResult] = []
        self.comparisons: List[ComparisonResult] = []
        
    def wilcoxon_test(self, sample1: np.ndarray, sample2: np.ndarray,
                     alternative: str = 'two-sided') -> StatisticalTestResult:
        """
        Perform Wilcoxon signed-rank test (non-parametric paired test)
        
        Args:
            sample1: First sample
            sample2: Second sample
            alternative: Alternative hypothesis ('two-sided', 'less', 'greater')
            
        Returns:
            Test result
        """
        try:
            logger.info("Performing Wilcoxon signed-rank test")
            
            statistic, p_value = stats.wilcoxon(sample1, sample2, alternative=alternative)
            
            is_significant = p_value < self.alpha
            interpretation = self._interpret_result(is_significant, p_value, "Wilcoxon")
            
            result = StatisticalTestResult(
                test_name="Wilcoxon signed-rank test",
                test_type="non_parametric",
                statistic=float(statistic),
                p_value=float(p_value),
                is_significant=is_significant,
                alpha=self.alpha,
                interpretation=interpretation
            )
            
            self.results.append(result)
            
            logger.info(f"✓ Wilcoxon test complete:")
            logger.info(f"  Statistic: {statistic:.4f}")
            logger.info(f"  P-value: {p_value:.4f}")
            logger.info(f"  Significant: {is_significant}")
            
            return result
            
        except Exception as e:
            logger.error(f"Wilcoxon test failed: {e}")
            raise
    
    def paired_t_test(self, sample1: np.ndarray, sample2: np.ndarray,
                     alternative: str = 'two-sided') -> StatisticalTestResult:
        """
        Perform paired t-test (parametric paired test)
        
        Args:
            sample1: First sample
            sample2: Second sample
            alternative: Alternative hypothesis
            
        Returns:
            Test result
        """
        try:
            logger.info("Performing paired t-test")
            
            statistic, p_value = stats.ttest_rel(sample1, sample2, alternative=alternative)
            
            is_significant = p_value < self.alpha
            interpretation = self._interpret_result(is_significant, p_value, "Paired t-test")
            
            result = StatisticalTestResult(
                test_name="Paired t-test",
                test_type="parametric",
                statistic=float(statistic),
                p_value=float(p_value),
                is_significant=is_significant,
                alpha=self.alpha,
                interpretation=interpretation
            )
            
            self.results.append(result)
            
            logger.info(f"✓ Paired t-test complete:")
            logger.info(f"  Statistic: {statistic:.4f}")
            logger.info(f"  P-value: {p_value:.4f}")
            logger.info(f"  Significant: {is_significant}")
            
            return result
            
        except Exception as e:
            logger.error(f"Paired t-test failed: {e}")
            raise
    
    def mcnemar_test(self, predictions1: np.ndarray, predictions2: np.ndarray,
                    y_true: np.ndarray) -> StatisticalTestResult:
        """
        Perform McNemar's test (for comparing two classifiers)
        
        Args:
            predictions1: Predictions from first classifier
            predictions2: Predictions from second classifier
            y_true: True labels
            
        Returns:
            Test result
        """
        try:
            logger.info("Performing McNemar's test")
            
            # Create contingency table
            correct1 = predictions1 == y_true
            correct2 = predictions2 == y_true
            
            # Both correct
            both_correct = np.sum(correct1 & correct2)
            # Only first correct
            only_first = np.sum(correct1 & ~correct2)
            # Only second correct
            only_second = np.sum(~correct1 & correct2)
            # Both wrong
            both_wrong = np.sum(~correct1 & ~correct2)
            
            # McNemar's statistic
            if (only_first + only_second) == 0:
                statistic = 0
                p_value = 1.0
            else:
                statistic = (abs(only_first - only_second) - 1) ** 2 / (only_first + only_second)
                p_value = 1 - stats.chi2.cdf(statistic, df=1)
            
            is_significant = p_value < self.alpha
            interpretation = self._interpret_result(is_significant, p_value, "McNemar")
            
            result = StatisticalTestResult(
                test_name="McNemar's test",
                test_type="classifier_comparison",
                statistic=float(statistic),
                p_value=float(p_value),
                is_significant=is_significant,
                alpha=self.alpha,
                interpretation=interpretation
            )
            
            self.results.append(result)
            
            logger.info(f"✓ McNemar's test complete:")
            logger.info(f"  Statistic: {statistic:.4f}")
            logger.info(f"  P-value: {p_value:.4f}")
            logger.info(f"  Significant: {is_significant}")
            
            return result
            
        except Exception as e:
            logger.error(f"McNemar's test failed: {e}")
            raise
    
    def anova_test(self, *samples: np.ndarray) -> StatisticalTestResult:
        """
        Perform one-way ANOVA test
        
        Args:
            *samples: Samples to compare
            
        Returns:
            Test result
        """
        try:
            logger.info(f"Performing one-way ANOVA on {len(samples)} samples")
            
            f_statistic, p_value = stats.f_oneway(*samples)
            
            is_significant = p_value < self.alpha
            interpretation = self._interpret_result(is_significant, p_value, "ANOVA")
            
            result = StatisticalTestResult(
                test_name="One-way ANOVA",
                test_type="parametric",
                statistic=float(f_statistic),
                p_value=float(p_value),
                is_significant=is_significant,
                alpha=self.alpha,
                interpretation=interpretation
            )
            
            self.results.append(result)
            
            logger.info(f"✓ ANOVA test complete:")
            logger.info(f"  F-statistic: {f_statistic:.4f}")
            logger.info(f"  P-value: {p_value:.4f}")
            logger.info(f"  Significant: {is_significant}")
            
            return result
            
        except Exception as e:
            logger.error(f"ANOVA test failed: {e}")
            raise
    
    def friedman_test(self, scores_matrix: np.ndarray) -> StatisticalTestResult:
        """
        Perform Friedman test (non-parametric ANOVA for repeated measures)
        
        Args:
            scores_matrix: Matrix where rows are algorithms and columns are datasets
            
        Returns:
            Test result
        """
        try:
            logger.info("Performing Friedman test")
            
            statistic, p_value = stats.friedmanchisquare(*scores_matrix.T)
            
            is_significant = p_value < self.alpha
            interpretation = self._interpret_result(is_significant, p_value, "Friedman")
            
            result = StatisticalTestResult(
                test_name="Friedman test",
                test_type="non_parametric",
                statistic=float(statistic),
                p_value=float(p_value),
                is_significant=is_significant,
                alpha=self.alpha,
                interpretation=interpretation
            )
            
            self.results.append(result)
            
            logger.info(f"✓ Friedman test complete:")
            logger.info(f"  Statistic: {statistic:.4f}")
            logger.info(f"  P-value: {p_value:.4f}")
            logger.info(f"  Significant: {is_significant}")
            
            return result
            
        except Exception as e:
            logger.error(f"Friedman test failed: {e}")
            raise
    
    def compare_models(self, model_a_scores: np.ndarray, model_b_scores: np.ndarray,
                      model_a_name: str = "Model A", model_b_name: str = "Model B",
                      test_type: str = 'wilcoxon') -> ComparisonResult:
        """
        Compare two models statistically
        
        Args:
            model_a_scores: Performance scores for model A
            model_b_scores: Performance scores for model B
            model_a_name: Name of model A
            model_b_name: Name of model B
            test_type: Type of test ('wilcoxon', 't_test', 'mcnemar')
            
        Returns:
            Comparison result
        """
        try:
            logger.info(f"Comparing {model_a_name} vs {model_b_name}")
            
            # Perform appropriate test
            if test_type == 'wilcoxon':
                test_result = self.wilcoxon_test(model_a_scores, model_b_scores)
            elif test_type == 't_test':
                test_result = self.paired_t_test(model_a_scores, model_b_scores)
            else:
                raise ValueError(f"Unknown test type: {test_type}")
            
            # Calculate effect size (Cohen's d)
            effect_size = self._cohens_d(model_a_scores, model_b_scores)
            
            # Determine winner
            mean_a = np.mean(model_a_scores)
            mean_b = np.mean(model_b_scores)
            
            if test_result.is_significant:
                winner = model_a_name if mean_a > mean_b else model_b_name
            else:
                winner = "No significant difference"
            
            comparison = ComparisonResult(
                model_a=model_a_name,
                model_b=model_b_name,
                test_type=test_type,
                statistic=test_result.statistic,
                p_value=test_result.p_value,
                is_significant=test_result.is_significant,
                effect_size=effect_size,
                winner=winner
            )
            
            self.comparisons.append(comparison)
            
            logger.info(f"✓ Comparison complete:")
            logger.info(f"  Winner: {winner}")
            logger.info(f"  Effect size (Cohen's d): {effect_size:.4f}")
            
            return comparison
            
        except Exception as e:
            logger.error(f"Model comparison failed: {e}")
            raise
    
    def _cohens_d(self, sample1: np.ndarray, sample2: np.ndarray) -> float:
        """Calculate Cohen's d effect size"""
        try:
            mean1 = np.mean(sample1)
            mean2 = np.mean(sample2)
            
            # Pooled standard deviation
            n1 = len(sample1)
            n2 = len(sample2)
            var1 = np.var(sample1, ddof=1)
            var2 = np.var(sample2, ddof=1)
            
            pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
            
            if pooled_std == 0:
                return 0.0
            
            cohens_d = (mean1 - mean2) / pooled_std
            
            return float(cohens_d)
            
        except Exception as e:
            logger.error(f"Failed to calculate Cohen's d: {e}")
            return 0.0
    
    def _interpret_result(self, is_significant: bool, p_value: float, test_name: str) -> str:
        """Interpret statistical test result"""
        if is_significant:
            if p_value < 0.001:
                return f"{test_name}: Highly significant difference (p < 0.001)"
            elif p_value < 0.01:
                return f"{test_name}: Significant difference (p < 0.01)"
            else:
                return f"{test_name}: Significant difference (p < 0.05)"
        else:
            return f"{test_name}: No significant difference (p = {p_value:.4f})"
    
    def interpret_effect_size(self, cohens_d: float) -> str:
        """
        Interpret Cohen's d effect size
        
        Args:
            cohens_d: Cohen's d value
            
        Returns:
            Interpretation string
        """
        abs_d = abs(cohens_d)
        
        if abs_d < 0.2:
            return "Negligible effect"
        elif abs_d < 0.5:
            return "Small effect"
        elif abs_d < 0.8:
            return "Medium effect"
        else:
            return "Large effect"
    
    def multiple_comparisons_correction(self, p_values: List[float],
                                       method: str = 'bonferroni') -> List[float]:
        """
        Apply multiple comparisons correction
        
        Args:
            p_values: List of p-values
            method: Correction method ('bonferroni', 'holm', 'fdr_bh')
            
        Returns:
            Corrected p-values
        """
        try:
            from statsmodels.stats.multitest import multipletests
            
            reject, p_corrected, _, _ = multipletests(p_values, alpha=self.alpha, method=method)
            
            logger.info(f"✓ Applied {method} correction to {len(p_values)} p-values")
            
            return p_corrected.tolist()
            
        except Exception as e:
            logger.error(f"Multiple comparisons correction failed: {e}")
            return p_values
    
    def calculate_confidence_interval(self, sample: np.ndarray,
                                     confidence: float = 0.95) -> Tuple[float, float]:
        """
        Calculate confidence interval for a sample
        
        Args:
            sample: Sample data
            confidence: Confidence level (default: 0.95)
            
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        try:
            mean = np.mean(sample)
            sem = stats.sem(sample)
            ci = stats.t.interval(confidence, len(sample) - 1, loc=mean, scale=sem)
            
            return (float(ci[0]), float(ci[1]))
            
        except Exception as e:
            logger.error(f"Failed to calculate confidence interval: {e}")
            return (0.0, 0.0)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get validation summary"""
        try:
            summary = {
                'total_tests': len(self.results),
                'total_comparisons': len(self.comparisons),
                'significant_results': sum(1 for r in self.results if r.is_significant),
                'by_test_type': {},
                'by_comparison': {}
            }
            
            # Count by test type
            for result in self.results:
                test_type = result.test_type
                if test_type not in summary['by_test_type']:
                    summary['by_test_type'][test_type] = 0
                summary['by_test_type'][test_type] += 1
            
            # Count by comparison
            for comparison in self.comparisons:
                key = f"{comparison.model_a} vs {comparison.model_b}"
                summary['by_comparison'][key] = {
                    'significant': comparison.is_significant,
                    'winner': comparison.winner,
                    'effect_size': comparison.effect_size
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get summary: {e}")
            return {}
    
    def export_results(self, filepath: str):
        """Export results to JSON"""
        try:
            results_data = {
                'timestamp': datetime.now().isoformat(),
                'alpha': self.alpha,
                'summary': self.get_summary(),
                'statistical_tests': [
                    {
                        'test_name': r.test_name,
                        'test_type': r.test_type,
                        'statistic': r.statistic,
                        'p_value': r.p_value,
                        'is_significant': r.is_significant,
                        'alpha': r.alpha,
                        'interpretation': r.interpretation,
                        'timestamp': r.timestamp
                    }
                    for r in self.results
                ],
                'model_comparisons': [
                    {
                        'model_a': c.model_a,
                        'model_b': c.model_b,
                        'test_type': c.test_type,
                        'statistic': c.statistic,
                        'p_value': c.p_value,
                        'is_significant': c.is_significant,
                        'effect_size': c.effect_size,
                        'winner': c.winner,
                        'timestamp': c.timestamp
                    }
                    for c in self.comparisons
                ]
            }
            
            with open(filepath, 'w') as f:
                json.dump(results_data, f, indent=2)
            
            logger.info(f"✓ Exported results to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to export results: {e}")


def validate_results(scores_dict: Dict[str, np.ndarray],
                    alpha: float = 0.05) -> Dict[str, Any]:
    """
    Convenience function to validate results
    
    Args:
        scores_dict: Dictionary of model names to performance scores
        alpha: Significance level
        
    Returns:
        Validation results
    """
    validator = StatisticalValidator(alpha=alpha)
    
    model_names = list(scores_dict.keys())
    results = {
        'tests': [],
        'comparisons': []
    }
    
    # Perform pairwise comparisons
    for i in range(len(model_names)):
        for j in range(i + 1, len(model_names)):
            model_a = model_names[i]
            model_b = model_names[j]
            
            comparison = validator.compare_models(
                scores_dict[model_a],
                scores_dict[model_b],
                model_a_name=model_a,
                model_b_name=model_b,
                test_type='wilcoxon'
            )
            
            results['comparisons'].append({
                'model_a': comparison.model_a,
                'model_b': comparison.model_b,
                'p_value': comparison.p_value,
                'is_significant': comparison.is_significant,
                'effect_size': comparison.effect_size,
                'winner': comparison.winner
            })
    
    # Add summary
    results['summary'] = validator.get_summary()
    
    return results


if __name__ == "__main__":
    # Test statistical validation
    print("Testing Statistical Validation...")
    print("="*80)
    
    np.random.seed(42)
    
    # Create sample data
    rf_scores = np.random.normal(0.986, 0.01, 30)
    xgb_scores = np.random.normal(0.991, 0.008, 30)
    svm_scores = np.random.normal(0.975, 0.015, 30)
    knn_scores = np.random.normal(0.948, 0.02, 30)
    
    validator = StatisticalValidator(alpha=0.05)
    
    print("\n1. Wilcoxon Test (RF vs XGBoost):")
    wilcoxon_result = validator.wilcoxon_test(rf_scores, xgb_scores)
    print(f"  P-value: {wilcoxon_result.p_value:.4f}")
    print(f"  Significant: {wilcoxon_result.is_significant}")
    
    print("\n2. Paired t-test (RF vs SVM):")
    ttest_result = validator.paired_t_test(rf_scores, svm_scores)
    print(f"  P-value: {ttest_result.p_value:.4f}")
    print(f"  Significant: {ttest_result.is_significant}")
    
    print("\n3. ANOVA (all models):")
    anova_result = validator.anova_test(rf_scores, xgb_scores, svm_scores, knn_scores)
    print(f"  F-statistic: {anova_result.statistic:.4f}")
    print(f"  P-value: {anova_result.p_value:.4f}")
    
    print("\n4. Model Comparisons:")
    comparison1 = validator.compare_models(rf_scores, xgb_scores, "Random Forest", "XGBoost")
    print(f"  RF vs XGBoost: {comparison1.winner} (p={comparison1.p_value:.4f})")
    
    comparison2 = validator.compare_models(svm_scores, knn_scores, "SVM", "KNN")
    print(f"  SVM vs KNN: {comparison2.winner} (p={comparison2.p_value:.4f})")
    
    print("\n5. Effect Size Interpretation:")
    print(f"  RF vs XGBoost: {validator.interpret_effect_size(comparison1.effect_size)}")
    print(f"  SVM vs KNN: {validator.interpret_effect_size(comparison2.effect_size)}")
    
    print("\n6. Confidence Intervals:")
    ci_rf = validator.calculate_confidence_interval(rf_scores)
    print(f"  RF: {ci_rf[0]:.4f} - {ci_rf[1]:.4f}")
    
    ci_xgb = validator.calculate_confidence_interval(xgb_scores)
    print(f"  XGBoost: {ci_xgb[0]:.4f} - {ci_xgb[1]:.4f}")
    
    print("\n7. Summary:")
    summary = validator.get_summary()
    print(json.dumps(summary, indent=2))
    
    # Export results
    validator.export_results('results/statistical_validation.json')
    
    print("\n✓ Statistical validation test complete!")