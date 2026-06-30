"""
Statistical Testing Module

This module provides statistical tests for comparing model performance.
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional, Tuple, List
from scipy import stats
from scipy.stats import wilcoxon, ttest_rel, ttest_ind, friedmanchisquare
from sklearn.metrics import accuracy_score, mean_squared_error

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StatisticalTester:
    """Perform statistical tests on model results"""
    
    def __init__(self, alpha: float = 0.05):
        """
        Initialize StatisticalTester
        
        Args:
            alpha: Significance level (default: 0.05)
        """
        self.alpha = alpha
        
    def wilcoxon_test(self, scores1: np.ndarray, scores2: np.ndarray,
                      alternative: str = 'two-sided') -> Dict[str, Any]:
        """
        Perform Wilcoxon signed-rank test (paired, non-parametric)
        
        Args:
            scores1: Scores from first model
            scores2: Scores from second model
            alternative: 'two-sided', 'less', or 'greater'
            
        Returns:
            Dictionary with test results
        """
        try:
            # Ensure arrays are 1D
            scores1 = np.array(scores1).flatten()
            scores2 = np.array(scores2).flatten()
            
            # Remove NaN values
            mask = ~(np.isnan(scores1) | np.isnan(scores2))
            scores1 = scores1[mask]
            scores2 = scores2[mask]
            
            if len(scores1) < 3:
                logger.warning("Not enough samples for Wilcoxon test")
                return {'error': 'Not enough samples'}
            
            # Perform test
            statistic, p_value = wilcoxon(scores1, scores2, alternative=alternative)
            
            result = {
                'test': 'Wilcoxon signed-rank test',
                'statistic': float(statistic),
                'p_value': float(p_value),
                'significant': p_value < self.alpha,
                'alpha': self.alpha,
                'alternative': alternative,
                'n_samples': len(scores1)
            }
            
            logger.info(f"✓ Wilcoxon test: statistic={statistic:.4f}, p-value={p_value:.4f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to perform Wilcoxon test: {e}")
            return {'error': str(e)}
    
    def paired_t_test(self, scores1: np.ndarray, scores2: np.ndarray,
                     alternative: str = 'two-sided') -> Dict[str, Any]:
        """
        Perform paired t-test (parametric)
        
        Args:
            scores1: Scores from first model
            scores2: Scores from second model
            alternative: 'two-sided', 'less', or 'greater'
            
        Returns:
            Dictionary with test results
        """
        try:
            # Ensure arrays are 1D
            scores1 = np.array(scores1).flatten()
            scores2 = np.array(scores2).flatten()
            
            # Remove NaN values
            mask = ~(np.isnan(scores1) | np.isnan(scores2))
            scores1 = scores1[mask]
            scores2 = scores2[mask]
            
            if len(scores1) < 2:
                logger.warning("Not enough samples for t-test")
                return {'error': 'Not enough samples'}
            
            # Perform test
            statistic, p_value = ttest_rel(scores1, scores2, alternative=alternative)
            
            result = {
                'test': 'Paired t-test',
                'statistic': float(statistic),
                'p_value': float(p_value),
                'significant': p_value < self.alpha,
                'alpha': self.alpha,
                'alternative': alternative,
                'n_samples': len(scores1),
                'mean_diff': float(np.mean(scores1 - scores2)),
                'std_diff': float(np.std(scores1 - scores2))
            }
            
            logger.info(f"✓ Paired t-test: statistic={statistic:.4f}, p-value={p_value:.4f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to perform paired t-test: {e}")
            return {'error': str(e)}
    
    def independent_t_test(self, scores1: np.ndarray, scores2: np.ndarray,
                          equal_var: bool = True,
                          alternative: str = 'two-sided') -> Dict[str, Any]:
        """
        Perform independent t-test (parametric)
        
        Args:
            scores1: Scores from first model
            scores2: Scores from second model
            equal_var: Whether to assume equal variances
            alternative: 'two-sided', 'less', or 'greater'
            
        Returns:
            Dictionary with test results
        """
        try:
            # Ensure arrays are 1D
            scores1 = np.array(scores1).flatten()
            scores2 = np.array(scores2).flatten()
            
            # Remove NaN values
            scores1 = scores1[~np.isnan(scores1)]
            scores2 = scores2[~np.isnan(scores2)]
            
            if len(scores1) < 2 or len(scores2) < 2:
                logger.warning("Not enough samples for independent t-test")
                return {'error': 'Not enough samples'}
            
            # Perform test
            statistic, p_value = ttest_ind(scores1, scores2, equal_var=equal_var, alternative=alternative)
            
            result = {
                'test': 'Independent t-test',
                'statistic': float(statistic),
                'p_value': float(p_value),
                'significant': p_value < self.alpha,
                'alpha': self.alpha,
                'alternative': alternative,
                'equal_var': equal_var,
                'n_samples_1': len(scores1),
                'n_samples_2': len(scores2),
                'mean_1': float(np.mean(scores1)),
                'mean_2': float(np.mean(scores2)),
                'std_1': float(np.std(scores1)),
                'std_2': float(np.std(scores2))
            }
            
            logger.info(f"✓ Independent t-test: statistic={statistic:.4f}, p-value={p_value:.4f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to perform independent t-test: {e}")
            return {'error': str(e)}
    
    def mcnemar_test(self, predictions1: np.ndarray, predictions2: np.ndarray,
                    y_true: np.ndarray) -> Dict[str, Any]:
        """
        Perform McNemar's test for comparing two classifiers
        
        Args:
            predictions1: Predictions from first model
            predictions2: Predictions from second model
            y_true: True labels
            
        Returns:
            Dictionary with test results
        """
        try:
            from statsmodels.stats.contingency_tables import mcnemar
            
            # Ensure arrays are 1D
            predictions1 = np.array(predictions1).flatten()
            predictions2 = np.array(predictions2).flatten()
            y_true = np.array(y_true).flatten()
            
            # Calculate contingency table
            correct1 = predictions1 == y_true
            correct2 = predictions2 == y_true
            
            # Both correct
            b = np.sum(correct1 & correct2)
            # Model 1 correct, Model 2 wrong
            c = np.sum(correct1 & ~correct2)
            # Model 1 wrong, Model 2 correct
            d = np.sum(~correct1 & correct2)
            # Both wrong
            a = np.sum(~correct1 & ~correct2)
            
            # Create contingency table
            table = [[b, c], [d, a]]
            
            # Perform McNemar's test
            result = mcnemar(table, exact=False, correction=True)
            
            test_result = {
                'test': "McNemar's test",
                'statistic': float(result.statistic),
                'p_value': float(result.pvalue),
                'significant': result.pvalue < self.alpha,
                'alpha': self.alpha,
                'contingency_table': {
                    'both_correct': int(b),
                    'model1_correct_model2_wrong': int(c),
                    'model1_wrong_model2_correct': int(d),
                    'both_wrong': int(a)
                }
            }
            
            logger.info(f"✓ McNemar's test: statistic={result.statistic:.4f}, p-value={result.pvalue:.4f}")
            
            return test_result
            
        except Exception as e:
            logger.error(f"Failed to perform McNemar's test: {e}")
            return {'error': str(e)}
    
    def friedman_test(self, scores_matrix: np.ndarray) -> Dict[str, Any]:
        """
        Perform Friedman test (non-parametric ANOVA for multiple models)
        
        Args:
            scores_matrix: Matrix of shape (n_datasets, n_models)
            
        Returns:
            Dictionary with test results
        """
        try:
            # Ensure 2D array
            scores_matrix = np.array(scores_matrix)
            
            if scores_matrix.shape[0] < 3:
                logger.warning("Not enough datasets for Friedman test")
                return {'error': 'Not enough datasets (need at least 3)'}
            
            # Perform Friedman test
            statistic, p_value = friedmanchisquare(*scores_matrix.T)
            
            result = {
                'test': 'Friedman test',
                'statistic': float(statistic),
                'p_value': float(p_value),
                'significant': p_value < self.alpha,
                'alpha': self.alpha,
                'n_datasets': scores_matrix.shape[0],
                'n_models': scores_matrix.shape[1]
            }
            
            logger.info(f"✓ Friedman test: statistic={statistic:.4f}, p-value={p_value:.4f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to perform Friedman test: {e}")
            return {'error': str(e)}
    
    def nemenyi_test(self, scores_matrix: np.ndarray) -> pd.DataFrame:
        """
        Perform Nemenyi post-hoc test (after Friedman test)
        
        Args:
            scores_matrix: Matrix of shape (n_datasets, n_models)
            
        Returns:
            DataFrame with pairwise comparisons
        """
        try:
            from scipy.stats import rankdata
            
            scores_matrix = np.array(scores_matrix)
            n_datasets, n_models = scores_matrix.shape
            
            # Rank models for each dataset
            ranks = np.array([rankdata(scores_matrix[i]) for i in range(n_datasets)])
            
            # Calculate average ranks
            avg_ranks = np.mean(ranks, axis=0)
            
            # Calculate critical difference
            q_alpha = 2.344  # For alpha=0.05 and k models (approximate)
            cd = q_alpha * np.sqrt(n_models * (n_models + 1) / (6 * n_datasets))
            
            # Perform pairwise comparisons
            comparisons = []
            for i in range(n_models):
                for j in range(i + 1, n_models):
                    diff = abs(avg_ranks[i] - avg_ranks[j])
                    significant = diff > cd
                    
                    comparisons.append({
                        'Model 1': f'Model {i+1}',
                        'Model 2': f'Model {j+1}',
                        'Rank Diff': diff,
                        'Critical Diff': cd,
                        'Significant': significant
                    })
            
            df = pd.DataFrame(comparisons)
            
            logger.info(f"✓ Nemenyi test completed with {len(comparisons)} comparisons")
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to perform Nemenyi test: {e}")
            return pd.DataFrame()
    
    def effect_size_cohens_d(self, scores1: np.ndarray, scores2: np.ndarray) -> float:
        """
        Calculate Cohen's d effect size
        
        Args:
            scores1: Scores from first model
            scores2: Scores from second model
            
        Returns:
            Cohen's d effect size
        """
        try:
            scores1 = np.array(scores1).flatten()
            scores2 = np.array(scores2).flatten()
            
            # Remove NaN values
            scores1 = scores1[~np.isnan(scores1)]
            scores2 = scores2[~np.isnan(scores2)]
            
            # Calculate pooled standard deviation
            n1, n2 = len(scores1), len(scores2)
            var1, var2 = np.var(scores1, ddof=1), np.var(scores2, ddof=1)
            pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
            
            if pooled_std == 0:
                return 0.0
            
            # Calculate Cohen's d
            cohens_d = (np.mean(scores1) - np.mean(scores2)) / pooled_std
            
            return float(cohens_d)
            
        except Exception as e:
            logger.error(f"Failed to calculate Cohen's d: {e}")
            return 0.0
    
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
            return "Negligible"
        elif abs_d < 0.5:
            return "Small"
        elif abs_d < 0.8:
            return "Medium"
        else:
            return "Large"


def statistical_comparison(predictions: Dict[str, np.ndarray],
                          y_true: np.ndarray,
                          test_type: str = 'wilcoxon',
                          alpha: float = 0.05) -> pd.DataFrame:
    """
    Perform statistical comparison of multiple models
    
    Args:
        predictions: Dictionary of model names to predictions
        y_true: True labels
        test_type: Type of test ('wilcoxon', 't_test', 'mcnemar')
        alpha: Significance level
        
    Returns:
        DataFrame with pairwise comparison results
    """
    try:
        tester = StatisticalTester(alpha=alpha)
        model_names = list(predictions.keys())
        n_models = len(model_names)
        
        comparisons = []
        
        for i in range(n_models):
            for j in range(i + 1, n_models):
                model1 = model_names[i]
                model2 = model_names[j]
                pred1 = predictions[model1]
                pred2 = predictions[model2]
                
                # Calculate accuracy for each sample (1 if correct, 0 if wrong)
                acc1 = (pred1 == y_true).astype(int)
                acc2 = (pred2 == y_true).astype(int)
                
                # Perform test
                if test_type == 'wilcoxon':
                    result = tester.wilcoxon_test(acc1, acc2)
                elif test_type == 't_test':
                    result = tester.paired_t_test(acc1, acc2)
                elif test_type == 'mcnemar':
                    result = tester.mcnemar_test(pred1, pred2, y_true)
                else:
                    result = {'error': f'Unknown test type: {test_type}'}
                
                if 'error' not in result:
                    comparisons.append({
                        'Model 1': model1,
                        'Model 2': model2,
                        'Test': result.get('test', test_type),
                        'Statistic': result.get('statistic', 0.0),
                        'p-value': result.get('p_value', 1.0),
                        'Significant': result.get('significant', False),
                        'Effect Size (Cohen d)': tester.effect_size_cohens_d(acc1, acc2)
                    })
        
        df = pd.DataFrame(comparisons)
        
        logger.info(f"✓ Completed statistical comparison with {len(comparisons)} tests")
        
        return df
        
    except Exception as e:
        logger.error(f"Failed to perform statistical comparison: {e}")
        return pd.DataFrame()


def wilcoxon_test(scores1: np.ndarray, scores2: np.ndarray,
                 alpha: float = 0.05) -> Dict[str, Any]:
    """
    Convenience function for Wilcoxon test
    
    Args:
        scores1: Scores from first model
        scores2: Scores from second model
        alpha: Significance level
        
    Returns:
        Dictionary with test results
    """
    tester = StatisticalTester(alpha=alpha)
    return tester.wilcoxon_test(scores1, scores2)


def paired_t_test(scores1: np.ndarray, scores2: np.ndarray,
                 alpha: float = 0.05) -> Dict[str, Any]:
    """
    Convenience function for paired t-test
    
    Args:
        scores1: Scores from first model
        scores2: Scores from second model
        alpha: Significance level
        
    Returns:
        Dictionary with test results
    """
    tester = StatisticalTester(alpha=alpha)
    return tester.paired_t_test(scores1, scores2)


def mcnemar_test(predictions1: np.ndarray, predictions2: np.ndarray,
                y_true: np.ndarray, alpha: float = 0.05) -> Dict[str, Any]:
    """
    Convenience function for McNemar's test
    
    Args:
        predictions1: Predictions from first model
        predictions2: Predictions from second model
        y_true: True labels
        alpha: Significance level
        
    Returns:
        Dictionary with test results
    """
    tester = StatisticalTester(alpha=alpha)
    return tester.mcnemar_test(predictions1, predictions2, y_true)


if __name__ == "__main__":
    # Test statistical tests
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    
    print("Testing statistical tests...")
    
    # Generate sample data
    X, y = make_classification(n_samples=500, n_features=20, n_classes=2,
                               n_informative=15, random_state=42)
    
    # Use multiple train-test splits for repeated measures
    n_splits = 10
    rf_scores = []
    gb_scores = []
    lr_scores = []
    
    for i in range(n_splits):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=i)
        
        # Random Forest
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X_train, y_train)
        rf_scores.append(accuracy_score(y_test, rf.predict(X_test)))
        
        # Gradient Boosting
        gb = GradientBoostingClassifier(n_estimators=100, random_state=42)
        gb.fit(X_train, y_train)
        gb_scores.append(accuracy_score(y_test, gb.predict(X_test)))
        
        # Logistic Regression
        lr = LogisticRegression(max_iter=1000, random_state=42)
        lr.fit(X_train, y_train)
        lr_scores.append(accuracy_score(y_test, lr.predict(X_test)))
    
    rf_scores = np.array(rf_scores)
    gb_scores = np.array(gb_scores)
    lr_scores = np.array(lr_scores)
    
    print(f"\nRandom Forest: {rf_scores.mean():.4f} ± {rf_scores.std():.4f}")
    print(f"Gradient Boosting: {gb_scores.mean():.4f} ± {gb_scores.std():.4f}")
    print(f"Logistic Regression: {lr_scores.mean():.4f} ± {lr_scores.std():.4f}")
    
    # Wilcoxon test
    print("\n" + "="*80)
    print("1. Wilcoxon Test (RF vs GB):")
    tester = StatisticalTester(alpha=0.05)
    result = tester.wilcoxon_test(rf_scores, gb_scores)
    print(f"Statistic: {result.get('statistic', 0):.4f}")
    print(f"P-value: {result.get('p_value', 1.0):.4f}")
    print(f"Significant: {result.get('significant', False)}")
    
    # Paired t-test
    print("\n2. Paired t-test (RF vs LR):")
    result = tester.paired_t_test(rf_scores, lr_scores)
    print(f"Statistic: {result.get('statistic', 0):.4f}")
    print(f"P-value: {result.get('p_value', 1.0):.4f}")
    print(f"Significant: {result.get('significant', False)}")
    
    # Effect size
    print("\n3. Effect Size (Cohen's d):")
    cohens_d = tester.effect_size_cohens_d(rf_scores, gb_scores)
    interpretation = tester.interpret_effect_size(cohens_d)
    print(f"Cohen's d (RF vs GB): {cohens_d:.4f} ({interpretation})")
    
    # McNemar's test
    print("\n4. McNemar's Test:")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)
    
    gb = GradientBoostingClassifier(n_estimators=100, random_state=42)
    gb.fit(X_train, y_train)
    gb_pred = gb.predict(X_test)
    
    result = tester.mcnemar_test(rf_pred, gb_pred, y_test)
    print(f"Statistic: {result.get('statistic', 0):.4f}")
    print(f"P-value: {result.get('p_value', 1.0):.4f}")
    print(f"Significant: {result.get('significant', False)}")
    
    # Friedman test
    print("\n5. Friedman Test:")
    scores_matrix = np.array([rf_scores, gb_scores, lr_scores]).T
    result = tester.friedman_test(scores_matrix)
    print(f"Statistic: {result.get('statistic', 0):.4f}")
    print(f"P-value: {result.get('p_value', 1.0):.4f}")
    print(f"Significant: {result.get('significant', False)}")
    
    # Nemenyi test
    print("\n6. Nemenyi Post-hoc Test:")
    nemenyi_results = tester.nemenyi_test(scores_matrix)
    print(nemenyi_results.to_string(index=False))
    
    # Statistical comparison function
    print("\n7. Statistical Comparison Function:")
    predictions = {
        'Random Forest': rf_pred,
        'Gradient Boosting': gb_pred
    }
    comparison = statistical_comparison(predictions, y_test, test_type='mcnemar')
    print(comparison.to_string(index=False))