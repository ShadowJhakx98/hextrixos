"""
fitness_integration.py

Display fitness data in HUD panel using Google Fitness API
"""

import logging
import datetime
from datetime import timedelta

logger = logging.getLogger("FitnessIntegration")
logger.setLevel(logging.INFO)

class FitnessIntegration:
    def __init__(self, api_manager):
        """
        Initialize Google Fitness integration
        
        Args:
            api_manager: GoogleAPIManager instance
        """
        self.api_manager = api_manager
        self.fitness_service = None
        self.cached_data = {}
        self.cache_times = {}
    
    def initialize(self):
        """Initialize the Fitness service"""
        try:
            self.fitness_service = self.api_manager.get_fitness_service()
            return self.fitness_service is not None
        except Exception as e:
            logger.error(f"Error initializing Fitness service: {str(e)}")
            return False
    
    def get_step_count(self, days=7, force_refresh=False):
        """Get step count data for the specified number of days"""
        return self._get_fitness_data('steps', days, force_refresh)
    
    def get_heart_rate(self, days=1, force_refresh=False):
        """Get heart rate data for the specified number of days"""
        return self._get_fitness_data('heart_rate', days, force_refresh)
    
    def get_calories(self, days=7, force_refresh=False):
        """Get calorie data for the specified number of days"""
        return self._get_fitness_data('calories', days, force_refresh)
    
    def get_weight(self, days=30, force_refresh=False):
        """Get weight data for the specified number of days"""
        return self._get_fitness_data('weight', days, force_refresh)
    
    def get_sleep(self, days=7, force_refresh=False):
        """Get sleep data for the specified number of days"""
        return self._get_fitness_data('sleep', days, force_refresh)
    
    def _get_fitness_data(self, data_type, days, force_refresh=False):
        """Core method to retrieve fitness data of various types"""
        # Define cache_key at the beginning to avoid UnboundLocalError
        cache_key = f"{data_type}_{days}"
        
        try:
            if not self.fitness_service:
                if not self.initialize():
                    return {'data_type': data_type, 'points': []}
            
            # Return cached data if available and not expired
            if (not force_refresh and cache_key in self.cached_data and cache_key in self.cache_times and
                (datetime.datetime.now() - self.cache_times[cache_key]).total_seconds() < 1800):  # 30 minutes cache
                return self.cached_data[cache_key]
            
            # Set up time range
            end_time = datetime.datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            # Map data types to Google Fitness data sources
            data_sources = {
                'steps': 'derived:com.google.step_count.delta:com.google.android.gms:estimated_steps',
                'heart_rate': 'derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm',
                'calories': 'derived:com.google.calories.expended:com.google.android.gms:merge_calories_expended',
                'weight': 'derived:com.google.weight:com.google.android.gms:merge_weight',
                'sleep': 'derived:com.google.sleep.segment:com.google.android.gms:merged'
            }
            
            data_source = data_sources.get(data_type)
            if not data_source:
                raise ValueError(f"Unsupported data type: {data_type}")
            
            # Request fitness data
            body = {
                "aggregateBy": [{
                    "dataTypeName": data_source
                }],
                "bucketByTime": {"durationMillis": 86400000},  # Daily buckets
                "startTimeMillis": int(start_time.timestamp() * 1000),
                "endTimeMillis": int(end_time.timestamp() * 1000)
            }
            
            response = self.fitness_service.users().dataset().aggregate(userId="me", body=body).execute()
            
            # Process the fitness data
            fitness_data = {
                'data_type': data_type,
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                },
                'points': []
            }
            
            for bucket in response.get('bucket', []):
                date_str = datetime.datetime.fromtimestamp(int(bucket['startTimeMillis']) / 1000).strftime('%Y-%m-%d')
                
                data_set = bucket.get('dataset', [])[0]
                data_points = data_set.get('point', [])
                
                if data_points:
                    point = data_points[0]
                    value = point.get('value', [{}])[0].get('intVal', 0) or point.get('value', [{}])[0].get('fpVal', 0)
                    
                    fitness_data['points'].append({
                        'date': date_str,
                        'start_time': bucket.get('startTimeMillis', 0),
                        'end_time': bucket.get('endTimeMillis', 0),
                        'value': value
                    })
            
            # Cache the fitness data
            self.cached_data[cache_key] = fitness_data
            self.cache_times[cache_key] = datetime.datetime.now()
            
            return fitness_data
            
        except Exception as e:
            logger.error(f"Error retrieving fitness data: {str(e)}")
            if cache_key in self.cached_data:
                logger.info(f"Using expired cached {data_type} fitness data due to error")
                return self.cached_data[cache_key]
            
            return {'data_type': data_type, 'points': []}
    
    def get_activity_summary(self, days=7):
        """Get a summary of all activity data for the specified number of days"""
        try:
            steps = self.get_step_count(days)
            calories = self.get_calories(days)
            
            # Combine data
            summary = {
                'days': days,
                'total_steps': sum(point['value'] for point in steps['points']),
                'avg_steps': sum(point['value'] for point in steps['points']) / max(1, len(steps['points'])),
                'total_calories': sum(point['value'] for point in calories['points']),
                'avg_calories': sum(point['value'] for point in calories['points']) / max(1, len(calories['points'])),
                'daily_data': []
            }
            
            # Map data by date
            date_map = {}
            for point in steps['points']:
                date_map[point['date']] = {'date': point['date'], 'steps': point['value']}
            
            for point in calories['points']:
                if point['date'] in date_map:
                    date_map[point['date']]['calories'] = point['value']
                else:
                    date_map[point['date']] = {'date': point['date'], 'calories': point['value']}
            
            # Sort by date and add to summary
            summary['daily_data'] = sorted(date_map.values(), key=lambda x: x['date'])
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting activity summary: {str(e)}")
            return {'days': days, 'total_steps': 0, 'avg_steps': 0, 'daily_data': []}