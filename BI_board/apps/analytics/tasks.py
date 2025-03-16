from celery import shared_task
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.cluster import KMeans
from .models import AnalysisResults, ProcessedData
import json
from fuzzywuzzy import process

@shared_task
def run_analytics(processed_data_id, column_mappings=None):
    try:
        # Fetch processed data
        processed_data = ProcessedData.objects.get(id=processed_data_id)
        data_content = processed_data.processed_json
        df = pd.read_json(data_content)
        df = df.dropna()
        columns = df.columns.tolist()

        # Define expected variables with possible aliases
        credit_risk_vars = {
            'age': ['age', 'customer_age', 'birth_year'],
            'employment_status': ['employment_status', 'job_status', 'work_status'],
            'annual_income': ['annual_income', 'income', 'yearly_income', 'salary'],
            'debt_to_income_ratio': ['debt_to_income_ratio', 'dti', 'debt_income_ratio'],
            'credit_score': ['credit_score', 'fico_score', 'credit_rating'],
            'previous_loan_defaults': ['previous_loan_defaults', 'defaults', 'past_defaults'],
            'number_of_late_payments': ['number_of_late_payments', 'late_payments', 'delinquencies'],
            'default': ['default', 'loan_default', 'defaulted', 'is_default']
        }
        segmentation_vars = {
            'age': ['age', 'customer_age', 'birth_year'],
            'annual_income': ['annual_income', 'income', 'yearly_income', 'salary'],
            'purchase_frequency': ['purchase_frequency', 'frequency', 'purchases_per_month'],
            'average_transaction_value': ['average_transaction_value', 'avg_purchase', 'avg_spend']
        }
        sales_forecast_vars = {
            'date': ['date', 'timestamp', 'sale_date', 'time'],
            'sales': ['sales', 'revenue', 'total_sales', 'amount']
        }

        # Suggest mappings if not provided
        if not column_mappings:
            def suggest_mapping(expected_vars, available_cols):
                mappings = {}
                for key, aliases in expected_vars.items():
                    best_match, score = process.extractOne(key, available_cols, scorer=process.fuzz.token_sort_ratio)
                    if score > 70 or best_match in aliases:
                        mappings[key] = best_match
                    if key in ['age', 'annual_income', 'credit_score', 'purchase_frequency', 'sales', 'average_transaction_value']:
                        if best_match in available_cols and not pd.api.types.is_numeric_dtype(df[best_match]):
                            mappings.pop(key, None)
                    elif key == 'date' and best_match in available_cols:
                        try:
                            pd.to_datetime(df[best_match])
                        except:
                            mappings.pop(key, None)
                return mappings

            recommendations = {
                'credit_risk': {'possible': False, 'suggested_mappings': suggest_mapping(credit_risk_vars, columns)},
                'segmentation': {'possible': False, 'suggested_mappings': suggest_mapping(segmentation_vars, columns)},
                'sales_forecast': {'possible': False, 'suggested_mappings': suggest_mapping(sales_forecast_vars, columns)}
            }
            recommendations['credit_risk']['possible'] = len(recommendations['credit_risk']['suggested_mappings']) >= 4
            recommendations['segmentation']['possible'] = len(recommendations['segmentation']['suggested_mappings']) >= 2
            recommendations['sales_forecast']['possible'] = len(recommendations['sales_forecast']['suggested_mappings']) == 2

            AnalysisResults.objects.create(
                processed_data=processed_data,
                recommendations=json.dumps(recommendations),
                factors=json.dumps({})  # Empty analysis results for now
            )
            return {'status': 'mapping_needed', 'result_id': AnalysisResults.objects.last().id}

        # Use provided mappings to rename columns
        df_mapped = df.rename(columns=column_mappings)

        # Run analyses with mapped data
        results = {}
        if 'credit_risk' in column_mappings:
            X = df_mapped[['age', 'annual_income', 'credit_score']].values
            y = df_mapped['default'].values if 'default' in df_mapped else np.random.randint(0, 2, len(df_mapped))
            model = LogisticRegression()
            model.fit(X, y)
            risk_scores = model.predict_proba(X)[:, 1]
            results['credit_risk'] = {
                'risk_scores': risk_scores.tolist(),
                'key_factors': ['age', 'annual_income', 'credit_score'],
                'recommendation': 'Monitor high-risk borrowers (score > 0.7)'
            }

        if 'segmentation' in column_mappings:
            numeric_cols = df_mapped.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) >= 2:
                X = df_mapped[numeric_cols].values
                kmeans = KMeans(n_clusters=3, random_state=42)
                clusters = kmeans.fit_predict(X)
                results['segmentation'] = {
                    'labels': clusters.tolist(),
                    'centroids': kmeans.cluster_centers_.tolist(),
                    'recommendation': 'Target Cluster 0 for upselling'
                }

        if 'sales_forecast' in column_mappings:
            df_mapped['date'] = pd.to_datetime(df_mapped['date'])
            df_mapped['days_since_start'] = (df_mapped['date'] - df_mapped['date'].min()).dt.days
            X = df_mapped[['days_since_start']].values
            y = df_mapped['sales'].values
            model = LinearRegression()
            model.fit(X, y)
            future_days = np.array([[i] for i in range(max(X.flatten()) + 1, max(X.flatten()) + 31)])
            forecast = model.predict(future_days)
            results['sales_forecast'] = {
                'dates': [(df_mapped['date'].max() + pd.Timedelta(days=i)).isoformat() for i in range(1, 31)],
                'predictions': forecast.tolist(),
                'recommendation': 'Prepare inventory for sales peak'
            }

        AnalysisResults.objects.create(
            processed_data=processed_data,
            recommendations=json.dumps([results.get(analysis, {}).get('recommendation') for analysis in results]),
            factors=json.dumps(results)  # Store full analysis results here
        )
        return {'status': 'success', 'result_id': AnalysisResults.objects.last().id}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}