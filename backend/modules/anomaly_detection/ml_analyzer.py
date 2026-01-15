"""
ML-based Anomaly Analyzer - On-demand or scheduled deep analysis
Supports multiple algorithms for user selection.
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class MLAnalyzer:
    """
    Provides ML-based anomaly detection with multiple algorithm options.
    Designed for batch/scheduled analysis, not real-time continuous use.
    """
    
    ALGORITHMS = {
        'isolation_forest': 'Isolation Forest',
        'one_class_svm': 'One-Class SVM',
        'dbscan': 'DBSCAN Clustering'
    }
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.current_algorithm = 'isolation_forest'
        self.last_analysis = None
        
    def analyze(
        self, 
        data_points: List[Dict],
        algorithm: str = 'isolation_forest',
        params: Optional[Dict] = None
    ) -> Dict:
        """
        Perform ML-based anomaly analysis on a batch of data points.
        
        Args:
            data_points: List of data dicts with 'temperature', 'vibration', 'power', 'timestamp'
            algorithm: One of 'isolation_forest', 'one_class_svm', 'dbscan'
            params: Optional algorithm-specific parameters
            
        Returns:
            Analysis result with anomalies, statistics, and recommendations
        """
        if not data_points or len(data_points) < 20:
            return {
                'success': False,
                'error': 'Insufficient data for ML analysis (minimum 20 points required)',
                'data_points_count': len(data_points) if data_points else 0
            }
        
        try:
            # Extract features
            features = self._extract_features(data_points)
            
            # Select and run algorithm
            if algorithm == 'isolation_forest':
                result = self._run_isolation_forest(features, data_points, params)
            elif algorithm == 'one_class_svm':
                result = self._run_one_class_svm(features, data_points, params)
            elif algorithm == 'dbscan':
                result = self._run_dbscan(features, data_points, params)
            else:
                return {
                    'success': False,
                    'error': f'Unknown algorithm: {algorithm}. Available: {list(self.ALGORITHMS.keys())}'
                }
            
            # Add metadata
            result['algorithm'] = algorithm
            result['algorithm_name'] = self.ALGORITHMS[algorithm]
            result['analyzed_at'] = datetime.now().isoformat()
            result['data_points_count'] = len(data_points)
            result['success'] = True
            
            self.last_analysis = result
            return result
            
        except Exception as e:
            logger.error(f"ML analysis failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'algorithm': algorithm
            }
    
    def _extract_features(self, data_points: List[Dict]) -> np.ndarray:
        """Extract and normalize features from data points"""
        features = []
        for point in data_points:
            features.append([
                point.get('temperature', 0),
                point.get('vibration', 0),
                point.get('power', 0)
            ])
        
        features_array = np.array(features)
        
        # Normalize features
        features_scaled = self.scaler.fit_transform(features_array)
        
        return features_scaled
    
    def _run_isolation_forest(
        self, 
        features: np.ndarray, 
        data_points: List[Dict],
        params: Optional[Dict]
    ) -> Dict:
        """
        Run Isolation Forest algorithm.
        Fast and effective for general outlier detection.
        """
        # Default parameters
        contamination = params.get('contamination', 0.05) if params else 0.05
        n_estimators = params.get('n_estimators', 100) if params else 100
        
        # Train model
        model = IsolationForest(
            n_estimators=n_estimators,
            contamination=contamination,
            random_state=42
        )
        
        predictions = model.fit_predict(features)
        scores = model.decision_function(features)
        
        # Find anomalies (prediction = -1)
        anomaly_indices = np.where(predictions == -1)[0]
        
        anomalies = []
        for idx in anomaly_indices:
            anomalies.append({
                'index': int(idx),
                'timestamp': data_points[idx].get('timestamp'),
                'score': float(scores[idx]),
                'values': {
                    'temperature': data_points[idx].get('temperature'),
                    'vibration': data_points[idx].get('vibration'),
                    'power': data_points[idx].get('power')
                }
            })
        
        return {
            'anomalies': anomalies,
            'anomaly_count': len(anomalies),
            'anomaly_rate': len(anomalies) / len(data_points),
            'parameters': {
                'contamination': contamination,
                'n_estimators': n_estimators
            },
            'scores': scores.tolist(),
            'summary': f'Found {len(anomalies)} anomalies ({len(anomalies)/len(data_points)*100:.1f}%) using Isolation Forest'
        }
    
    def _run_one_class_svm(
        self, 
        features: np.ndarray, 
        data_points: List[Dict],
        params: Optional[Dict]
    ) -> Dict:
        """
        Run One-Class SVM algorithm.
        Good for finding subtle non-linear patterns, but slower.
        """
        # Default parameters
        nu = params.get('nu', 0.05) if params else 0.05  # Fraction of outliers
        kernel = params.get('kernel', 'rbf') if params else 'rbf'
        gamma = params.get('gamma', 'scale') if params else 'scale'
        
        # Train model
        model = OneClassSVM(
            nu=nu,
            kernel=kernel,
            gamma=gamma
        )
        
        predictions = model.fit_predict(features)
        scores = model.decision_function(features)
        
        # Find anomalies (prediction = -1)
        anomaly_indices = np.where(predictions == -1)[0]
        
        anomalies = []
        for idx in anomaly_indices:
            anomalies.append({
                'index': int(idx),
                'timestamp': data_points[idx].get('timestamp'),
                'score': float(scores[idx]),
                'values': {
                    'temperature': data_points[idx].get('temperature'),
                    'vibration': data_points[idx].get('vibration'),
                    'power': data_points[idx].get('power')
                }
            })
        
        return {
            'anomalies': anomalies,
            'anomaly_count': len(anomalies),
            'anomaly_rate': len(anomalies) / len(data_points),
            'parameters': {
                'nu': nu,
                'kernel': kernel,
                'gamma': gamma
            },
            'scores': scores.tolist(),
            'summary': f'Found {len(anomalies)} anomalies ({len(anomalies)/len(data_points)*100:.1f}%) using One-Class SVM'
        }
    
    def _run_dbscan(
        self, 
        features: np.ndarray, 
        data_points: List[Dict],
        params: Optional[Dict]
    ) -> Dict:
        """
        Run DBSCAN clustering algorithm.
        Identifies outliers as points that don't belong to any cluster.
        """
        # Default parameters
        eps = params.get('eps', 0.5) if params else 0.5
        min_samples = params.get('min_samples', 5) if params else 5
        
        # Train model
        model = DBSCAN(
            eps=eps,
            min_samples=min_samples
        )
        
        labels = model.fit_predict(features)
        
        # Anomalies are points with label -1 (noise)
        anomaly_indices = np.where(labels == -1)[0]
        
        # Count clusters
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        
        anomalies = []
        for idx in anomaly_indices:
            anomalies.append({
                'index': int(idx),
                'timestamp': data_points[idx].get('timestamp'),
                'cluster': -1,
                'values': {
                    'temperature': data_points[idx].get('temperature'),
                    'vibration': data_points[idx].get('vibration'),
                    'power': data_points[idx].get('power')
                }
            })
        
        return {
            'anomalies': anomalies,
            'anomaly_count': len(anomalies),
            'anomaly_rate': len(anomalies) / len(data_points),
            'n_clusters': n_clusters,
            'parameters': {
                'eps': eps,
                'min_samples': min_samples
            },
            'cluster_labels': labels.tolist(),
            'summary': f'Found {len(anomalies)} outlier points ({len(anomalies)/len(data_points)*100:.1f}%) and {n_clusters} clusters using DBSCAN'
        }
    
    def get_available_algorithms(self) -> Dict:
        """Get list of available algorithms with descriptions"""
        return {
            'algorithms': [
                {
                    'id': 'isolation_forest',
                    'name': 'Isolation Forest',
                    'description': 'Fast and effective for general outlier detection. Best for most use cases.',
                    'speed': 'fast',
                    'parameters': {
                        'contamination': {'type': 'float', 'default': 0.05, 'range': [0.01, 0.5]},
                        'n_estimators': {'type': 'int', 'default': 100, 'range': [50, 300]}
                    }
                },
                {
                    'id': 'one_class_svm',
                    'name': 'One-Class SVM',
                    'description': 'Finds subtle non-linear patterns. Good for complex anomalies, but slower.',
                    'speed': 'medium',
                    'parameters': {
                        'nu': {'type': 'float', 'default': 0.05, 'range': [0.01, 0.5]},
                        'kernel': {'type': 'enum', 'default': 'rbf', 'options': ['rbf', 'linear', 'poly']},
                        'gamma': {'type': 'enum', 'default': 'scale', 'options': ['scale', 'auto']}
                    }
                },
                {
                    'id': 'dbscan',
                    'name': 'DBSCAN Clustering',
                    'description': 'Identifies group anomalies and outliers through density-based clustering.',
                    'speed': 'fast',
                    'parameters': {
                        'eps': {'type': 'float', 'default': 0.5, 'range': [0.1, 2.0]},
                        'min_samples': {'type': 'int', 'default': 5, 'range': [2, 20]}
                    }
                }
            ]
        }
    
    def get_last_analysis(self) -> Optional[Dict]:
        """Get the most recent analysis result"""
        return self.last_analysis


# Global instance
ml_analyzer = MLAnalyzer()
