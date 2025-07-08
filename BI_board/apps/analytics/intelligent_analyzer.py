import pandas as pd
import numpy as np
from datetime import datetime
import re
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from fuzzywuzzy import process, fuzz
import logging

logger = logging.getLogger(__name__)

@dataclass
class ColumnProfile:
    """Profile of a single column"""
    name: str
    dtype: str
    null_percentage: float
    unique_values: int
    sample_values: List[Any]
    is_numeric: bool
    is_categorical: bool
    is_datetime: bool
    is_id_like: bool
    semantic_type: str
    confidence: float

@dataclass
class DatasetProfile:
    """Complete profile of a dataset"""
    shape: Tuple[int, int]
    columns: List[ColumnProfile]
    data_quality_score: float
    potential_target_columns: List[str]
    potential_feature_columns: List[str]
    relationships: Dict[str, List[str]]
    business_domain: str
    confidence: float

@dataclass
class AnalysisRecommendation:
    """Recommendation for analysis"""
    analysis_type: str
    confidence: float
    required_columns: Dict[str, str]
    missing_columns: List[str]
    data_quality_issues: List[str]
    explanation: str
    alternative_approaches: List[str]

class IntelligentDatasetAnalyzer:
    """
    Intelligent system that understands datasets and recommends optimal analysis
    """
    
    def __init__(self):
        self.semantic_patterns = {
            'customer_id': [
                r'customer.*id', r'cust.*id', r'client.*id', r'user.*id',
                r'account.*id', r'member.*id'
            ],
            'transaction_id': [
                r'transaction.*id', r'trans.*id', r'order.*id', r'invoice.*id',
                r'receipt.*id', r'payment.*id'
            ],
            'date': [
                r'date', r'time', r'timestamp', r'created.*at', r'updated.*at',
                r'.*date.*', r'.*time.*'
            ],
            'amount': [
                r'amount', r'price', r'cost', r'value', r'total', r'sum',
                r'revenue', r'sales', r'income', r'salary', r'wage'
            ],
            'age': [
                r'^age$', r'customer.*age', r'user.*age', r'birth.*year',
                r'years.*old'
            ],
            'score': [
                r'score', r'rating', r'grade', r'rank', r'credit.*score',
                r'risk.*score', r'satisfaction'
            ],
            'category': [
                r'category', r'type', r'class', r'group', r'segment',
                r'status', r'state', r'level'
            ],
            'location': [
                r'city', r'state', r'country', r'region', r'zip', r'postal',
                r'address', r'location'
            ]
        }
        
        self.business_domains = {
            'finance': ['credit', 'loan', 'bank', 'payment', 'transaction', 'account', 'balance'],
            'retail': ['product', 'purchase', 'order', 'customer', 'sales', 'inventory'],
            'marketing': ['campaign', 'lead', 'conversion', 'click', 'impression', 'engagement'],
            'hr': ['employee', 'salary', 'department', 'performance', 'hire', 'promotion'],
            'healthcare': ['patient', 'diagnosis', 'treatment', 'medical', 'hospital', 'doctor']
        }

    def analyze_dataset(self, df: pd.DataFrame) -> DatasetProfile:
        """
        Comprehensive analysis of dataset structure and content
        """
        logger.info(f"Analyzing dataset with shape {df.shape}")
        
        # Profile each column
        column_profiles = []
        for col in df.columns:
            profile = self._profile_column(df, col)
            column_profiles.append(profile)
        
        # Identify relationships and patterns
        relationships = self._identify_relationships(df, column_profiles)
        
        # Determine business domain
        business_domain = self._identify_business_domain(column_profiles)
        
        # Calculate data quality
        data_quality_score = self._calculate_data_quality(df, column_profiles)
        
        # Identify potential targets and features
        target_columns = self._identify_potential_targets(column_profiles)
        feature_columns = self._identify_potential_features(column_profiles)
        
        return DatasetProfile(
            shape=df.shape,
            columns=column_profiles,
            data_quality_score=data_quality_score,
            potential_target_columns=target_columns,
            potential_feature_columns=feature_columns,
            relationships=relationships,
            business_domain=business_domain,
            confidence=self._calculate_overall_confidence(column_profiles, data_quality_score)
        )

    def _profile_column(self, df: pd.DataFrame, col: str) -> ColumnProfile:
        """Profile a single column"""
        series = df[col]
        
        # Basic statistics
        null_pct = series.isnull().sum() / len(series) * 100
        unique_vals = series.nunique()
        sample_vals = series.dropna().head(5).tolist()
        
        # Type detection
        is_numeric = pd.api.types.is_numeric_dtype(series)
        is_categorical = self._is_categorical(series)
        is_datetime = self._is_datetime(series)
        is_id_like = self._is_id_like(series)
        
        # Semantic type detection
        semantic_type, confidence = self._detect_semantic_type(col, series)
        
        return ColumnProfile(
            name=col,
            dtype=str(series.dtype),
            null_percentage=null_pct,
            unique_values=unique_vals,
            sample_values=sample_vals,
            is_numeric=is_numeric,
            is_categorical=is_categorical,
            is_datetime=is_datetime,
            is_id_like=is_id_like,
            semantic_type=semantic_type,
            confidence=confidence
        )

    def _detect_semantic_type(self, col_name: str, series: pd.Series) -> Tuple[str, float]:
        """Detect semantic meaning of column"""
        col_lower = col_name.lower()
        
        # Check against semantic patterns
        for semantic_type, patterns in self.semantic_patterns.items():
            for pattern in patterns:
                if re.search(pattern, col_lower):
                    confidence = 0.9 if re.match(pattern, col_lower) else 0.7
                    return semantic_type, confidence
        
        # Content-based detection
        if pd.api.types.is_numeric_dtype(series):
            if series.min() >= 0 and series.max() <= 150 and 'age' in col_lower:
                return 'age', 0.8
            elif series.min() >= 0 and series.nunique() / len(series) > 0.8:
                return 'amount', 0.6
        
        # Default classification
        if pd.api.types.is_numeric_dtype(series):
            return 'numeric', 0.5
        elif self._is_categorical(series):
            return 'category', 0.5
        else:
            return 'text', 0.3

    def _is_categorical(self, series: pd.Series) -> bool:
        """Check if column is categorical"""
        if pd.api.types.is_numeric_dtype(series):
            return series.nunique() <= 20 and series.nunique() / len(series) < 0.1
        else:
            return series.nunique() <= 50 and series.nunique() / len(series) < 0.5

    def _is_datetime(self, series: pd.Series) -> bool:
        """Check if column contains datetime data"""
        if pd.api.types.is_datetime64_any_dtype(series):
            return True
        
        # Try to parse as datetime
        try:
            pd.to_datetime(series.dropna().head(100))
            return True
        except:
            return False

    def _is_id_like(self, series: pd.Series) -> bool:
        """Check if column looks like an ID"""
        if series.nunique() / len(series) > 0.95:  # High uniqueness
            if pd.api.types.is_numeric_dtype(series) or \
               all(isinstance(x, str) and len(x) > 5 for x in series.dropna().head(10)):
                return True
        return False

    def _identify_relationships(self, df: pd.DataFrame, profiles: List[ColumnProfile]) -> Dict[str, List[str]]:
        """Identify relationships between columns"""
        relationships = {}
        
        # Find potential foreign keys
        id_columns = [p.name for p in profiles if p.is_id_like]
        
        # Find correlated numeric columns
        numeric_cols = [p.name for p in profiles if p.is_numeric and not p.is_id_like]
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            high_corr = []
            for i in range(len(numeric_cols)):
                for j in range(i+1, len(numeric_cols)):
                    if abs(corr_matrix.iloc[i, j]) > 0.7:
                        high_corr.append((numeric_cols[i], numeric_cols[j]))
            relationships['correlated'] = high_corr
        
        return relationships

    def _identify_business_domain(self, profiles: List[ColumnProfile]) -> str:
        """Identify the business domain of the dataset"""
        column_names = [p.name.lower() for p in profiles]
        all_text = ' '.join(column_names)
        
        domain_scores = {}
        for domain, keywords in self.business_domains.items():
            score = sum(1 for keyword in keywords if keyword in all_text)
            domain_scores[domain] = score
        
        if domain_scores:
            best_domain = max(domain_scores, key=domain_scores.get)
            if domain_scores[best_domain] > 0:
                return best_domain
        
        return 'general'

    def _calculate_data_quality(self, df: pd.DataFrame, profiles: List[ColumnProfile]) -> float:
        """Calculate overall data quality score"""
        scores = []
        
        # Completeness score
        avg_null_pct = np.mean([p.null_percentage for p in profiles])
        completeness = max(0, 100 - avg_null_pct) / 100
        scores.append(completeness)
        
        # Consistency score (based on data types)
        type_consistency = len([p for p in profiles if p.confidence > 0.7]) / len(profiles)
        scores.append(type_consistency)
        
        # Uniqueness score (avoid too many duplicates)
        uniqueness_scores = []
        for p in profiles:
            if not p.is_id_like:
                uniqueness = min(1.0, p.unique_values / len(df) * 2)
                uniqueness_scores.append(uniqueness)
        
        if uniqueness_scores:
            scores.append(np.mean(uniqueness_scores))
        
        return np.mean(scores)

    def _identify_potential_targets(self, profiles: List[ColumnProfile]) -> List[str]:
        """Identify columns that could be prediction targets"""
        targets = []
        
        for profile in profiles:
            # Binary classification targets
            if profile.is_categorical and profile.unique_values == 2:
                targets.append(profile.name)
            
            # Regression targets (amounts, scores)
            elif profile.semantic_type in ['amount', 'score'] and profile.is_numeric:
                targets.append(profile.name)
            
            # Risk/default indicators
            elif any(keyword in profile.name.lower() for keyword in ['default', 'risk', 'churn', 'fraud']):
                targets.append(profile.name)
        
        return targets

    def _identify_potential_features(self, profiles: List[ColumnProfile]) -> List[str]:
        """Identify columns that could be good features"""
        features = []
        
        for profile in profiles:
            # Skip ID columns
            if profile.is_id_like:
                continue
            
            # Good feature candidates
            if profile.is_numeric or profile.is_categorical:
                if profile.null_percentage < 50:  # Not too many missing values
                    features.append(profile.name)
        
        return features

    def _calculate_overall_confidence(self, profiles: List[ColumnProfile], data_quality: float) -> float:
        """Calculate overall confidence in dataset understanding"""
        avg_column_confidence = np.mean([p.confidence for p in profiles])
        return (avg_column_confidence + data_quality) / 2

    def recommend_analyses(self, dataset_profile: DatasetProfile) -> List[AnalysisRecommendation]:
        """
        Intelligent recommendation of analyses based on dataset profile
        """
        recommendations = []

        # Check for Sales Forecasting
        sales_rec = self._check_sales_forecasting(dataset_profile)
        if sales_rec:
            recommendations.append(sales_rec)

        # Check for Credit Risk Analysis
        credit_rec = self._check_credit_risk(dataset_profile)
        if credit_rec:
            recommendations.append(credit_rec)

        # Check for Customer Segmentation
        segment_rec = self._check_customer_segmentation(dataset_profile)
        if segment_rec:
            recommendations.append(segment_rec)

        # Additional intelligent recommendations
        other_recs = self._suggest_alternative_analyses(dataset_profile)
        recommendations.extend(other_recs)

        # Sort by confidence
        recommendations.sort(key=lambda x: x.confidence, reverse=True)

        return recommendations

    def _check_sales_forecasting(self, profile: DatasetProfile) -> AnalysisRecommendation:
        """Check if sales forecasting is possible"""
        required_cols = {'date': None, 'sales': None}
        missing_cols = []
        issues = []

        # Find date column
        date_candidates = [c for c in profile.columns if c.semantic_type == 'date' or c.is_datetime]
        if date_candidates:
            required_cols['date'] = date_candidates[0].name
        else:
            missing_cols.append('date/timestamp column')

        # Find sales/amount column
        sales_candidates = [c for c in profile.columns
                          if c.semantic_type == 'amount' and c.is_numeric]
        if sales_candidates:
            required_cols['sales'] = sales_candidates[0].name
        else:
            missing_cols.append('sales/revenue/amount column')

        # Calculate confidence
        confidence = 0.0
        if not missing_cols:
            confidence = 0.9
            if profile.shape[0] < 30:
                issues.append("Dataset might be too small for reliable forecasting (< 30 records)")
                confidence -= 0.2
        else:
            confidence = 0.1

        explanation = "Sales forecasting requires time-series data with dates and corresponding sales values."
        alternatives = []

        if missing_cols:
            if any(c.is_numeric for c in profile.columns):
                alternatives.append("Trend analysis of available numeric columns")
            alternatives.append("Descriptive statistics and data exploration")

        return AnalysisRecommendation(
            analysis_type="sales_forecasting",
            confidence=confidence,
            required_columns=required_cols,
            missing_columns=missing_cols,
            data_quality_issues=issues,
            explanation=explanation,
            alternative_approaches=alternatives
        )

    def _check_credit_risk(self, profile: DatasetProfile) -> AnalysisRecommendation:
        """Check if credit risk analysis is possible"""
        required_cols = {'age': None, 'income': None, 'credit_score': None, 'default': None}
        missing_cols = []
        issues = []

        # Find age column
        age_candidates = [c for c in profile.columns if c.semantic_type == 'age']
        if age_candidates:
            required_cols['age'] = age_candidates[0].name
        else:
            missing_cols.append('age column')

        # Find income column
        income_candidates = [c for c in profile.columns
                           if 'income' in c.name.lower() or 'salary' in c.name.lower()]
        if income_candidates:
            required_cols['income'] = income_candidates[0].name
        else:
            missing_cols.append('income/salary column')

        # Find credit score
        score_candidates = [c for c in profile.columns
                          if 'credit' in c.name.lower() and 'score' in c.name.lower()]
        if score_candidates:
            required_cols['credit_score'] = score_candidates[0].name
        else:
            missing_cols.append('credit score column')

        # Find default/risk indicator
        default_candidates = [c for c in profile.columns
                            if any(keyword in c.name.lower()
                                 for keyword in ['default', 'risk', 'bad', 'delinquent'])]
        if default_candidates:
            required_cols['default'] = default_candidates[0].name
        else:
            missing_cols.append('default/risk indicator column')

        # Calculate confidence
        confidence = max(0.0, 1.0 - len(missing_cols) * 0.25)

        if confidence > 0.5 and profile.shape[0] < 100:
            issues.append("Dataset might be too small for reliable risk modeling (< 100 records)")
            confidence -= 0.2

        explanation = "Credit risk analysis requires customer demographics, financial info, and default indicators."
        alternatives = []

        if len(missing_cols) > 2:
            alternatives.append("Customer profiling and descriptive analytics")
            alternatives.append("Correlation analysis of available financial metrics")

        return AnalysisRecommendation(
            analysis_type="credit_risk",
            confidence=confidence,
            required_columns=required_cols,
            missing_columns=missing_cols,
            data_quality_issues=issues,
            explanation=explanation,
            alternative_approaches=alternatives
        )

    def _check_customer_segmentation(self, profile: DatasetProfile) -> AnalysisRecommendation:
        """Check if customer segmentation is possible"""
        required_cols = {}
        missing_cols = []
        issues = []

        # Find numeric columns for segmentation
        numeric_cols = [c for c in profile.columns
                       if c.is_numeric and not c.is_id_like and c.null_percentage < 50]

        if len(numeric_cols) >= 2:
            required_cols['features'] = [c.name for c in numeric_cols[:5]]  # Top 5
            confidence = 0.8
        else:
            missing_cols.append("at least 2 numeric columns for clustering")
            confidence = 0.2

        # Check for customer-related data
        customer_indicators = [c for c in profile.columns
                             if any(keyword in c.name.lower()
                                  for keyword in ['customer', 'user', 'client', 'member'])]

        if customer_indicators:
            confidence += 0.1

        if confidence > 0.5 and profile.shape[0] < 50:
            issues.append("Dataset might be too small for meaningful clustering (< 50 records)")
            confidence -= 0.2

        explanation = "Customer segmentation requires multiple numeric features to identify customer groups."
        alternatives = []

        if len(numeric_cols) < 2:
            alternatives.append("Descriptive statistics by categorical variables")
            alternatives.append("Distribution analysis of individual metrics")

        return AnalysisRecommendation(
            analysis_type="customer_segmentation",
            confidence=confidence,
            required_columns=required_cols,
            missing_columns=missing_cols,
            data_quality_issues=issues,
            explanation=explanation,
            alternative_approaches=alternatives
        )

    def _suggest_alternative_analyses(self, profile: DatasetProfile) -> List[AnalysisRecommendation]:
        """Suggest alternative analyses based on data characteristics"""
        alternatives = []

        # Correlation Analysis
        numeric_cols = [c for c in profile.columns if c.is_numeric and not c.is_id_like]
        if len(numeric_cols) >= 3:
            alternatives.append(AnalysisRecommendation(
                analysis_type="correlation_analysis",
                confidence=0.7,
                required_columns={'numeric_features': [c.name for c in numeric_cols]},
                missing_columns=[],
                data_quality_issues=[],
                explanation="Analyze relationships between numeric variables to find patterns.",
                alternative_approaches=[]
            ))

        # Anomaly Detection
        if len(numeric_cols) >= 2 and profile.shape[0] > 100:
            alternatives.append(AnalysisRecommendation(
                analysis_type="anomaly_detection",
                confidence=0.6,
                required_columns={'features': [c.name for c in numeric_cols]},
                missing_columns=[],
                data_quality_issues=[],
                explanation="Identify unusual patterns or outliers in your data.",
                alternative_approaches=[]
            ))

        # Descriptive Analytics (always possible)
        alternatives.append(AnalysisRecommendation(
            analysis_type="descriptive_analytics",
            confidence=0.9,
            required_columns={'all_columns': [c.name for c in profile.columns]},
            missing_columns=[],
            data_quality_issues=[],
            explanation="Comprehensive statistical summary and data exploration.",
            alternative_approaches=[]
        ))

        return alternatives
