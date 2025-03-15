"""
activity_tracking.py

Implementation of sexual activity tracking with Google Fit sync
for tracking fitness metrics related to intimate activities
"""

import os
import json
import time
import logging
import datetime
import numpy as np
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Setup logging
logger = logging.getLogger("ActivityTracking")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class ActivityTracker:
    def __init__(self, safety_manager=None):
        """
        Initialize Activity Tracker with Google Fit integration
        
        Args:
            safety_manager: Optional safety manager that handles consent
        """
        self.safety_manager = safety_manager
        self.credentials = None
        self.fitness_service = None
        self.data_source_id = None
        self.scopes = [
            'https://www.googleapis.com/auth/fitness.activity.write',
            'https://www.googleapis.com/auth/fitness.heart_rate.write',
            'https://www.googleapis.com/auth/fitness.body.read',
            'https://www.googleapis.com/auth/fitness.activity.read'
        ]
        self.activity_history = {}
        
        # Try to load stored credentials
        self._load_credentials()
    
    def _load_credentials(self):
        """Load Google API credentials"""
        token_file = 'tokens/fitness_token.json'
        
        try:
            if os.path.exists(token_file):
                self.credentials = Credentials.from_authorized_user_file(token_file, self.scopes)
            
            # If credentials don't exist or are invalid
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    # Need to get new credentials
                    return False
                
                # Save the refreshed credentials
                os.makedirs(os.path.dirname(token_file), exist_ok=True)
                with open(token_file, 'w') as token:
                    token.write(self.credentials.to_json())
            
            return True
        except Exception as e:
            logger.error(f"Error loading credentials: {str(e)}")
            return False
    
    def authenticate(self, client_secrets_file='client_secrets.json'):
        """
        Authenticate with Google Fit API using OAuth
        
        Args:
            client_secrets_file: Path to client secrets JSON file
            
        Returns:
            Boolean indicating success
        """
        try:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, self.scopes)
            self.credentials = flow.run_local_server(port=0)
            
            # Save the credentials for next run
            token_file = 'tokens/fitness_token.json'
            os.makedirs(os.path.dirname(token_file), exist_ok=True)
            with open(token_file, 'w') as token:
                token.write(self.credentials.to_json())
            
            logger.info("Successfully authenticated with Google Fit")
            return True
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def initialize_service(self):
        """Initialize the Google Fitness service"""
        if not self.credentials:
            if not self._load_credentials():
                logger.error("No valid credentials available")
                return False
        
        try:
            self.fitness_service = build('fitness', 'v1', credentials=self.credentials)
            
            # Set up data source if needed
            if not self.data_source_id:
                self._create_or_get_data_source()
            
            logger.info("Google Fit service initialized")
            return True
        except Exception as e:
            logger.error(f"Error initializing fitness service: {str(e)}")
            return False
    
    def _create_or_get_data_source(self):
        """Create or get the data source for sex/masturbation activities"""
        try:
            # Define data source
            data_source = {
                'dataStreamName': 'hextrix_sexual_activity',
                'type': 'derived',
                'application': {
                    'name': 'Hextrix AI'
                },
                'dataType': {
                    'name': 'com.google.activity.segment',
                    'field': [
                        {
                            'name': 'activity',
                            'format': 'integer'
                        }
                    ]
                },
                'device': {
                    'type': 'phone',
                    'manufacturer': 'Hextrix',
                    'model': 'AI',
                    'uid': '1000001',
                    'version': '1.0'
                }
            }
            
            # Check if data source already exists
            list_sources = self.fitness_service.users().dataSources().list(
                userId='me'
            ).execute()
            
            for source in list_sources.get('dataSource', []):
                if source.get('dataStreamName') == 'hextrix_sexual_activity':
                    self.data_source_id = source['dataStreamId']
                    logger.info(f"Using existing data source: {self.data_source_id}")
                    return
            
            # Create new data source
            data_source_result = self.fitness_service.users().dataSources().create(
                userId='me',
                body=data_source
            ).execute()
            
            self.data_source_id = data_source_result['dataStreamId']
            logger.info(f"Created new data source: {self.data_source_id}")
            
        except Exception as e:
            logger.error(f"Error creating data source: {str(e)}")
            self.data_source_id = "derived:com.google.activity.segment:Hextrix:AI:hextrix_sexual_activity"
    
    def log_activity(self, user_id, activity_type, duration_minutes, heart_rate=None, calories=None, require_consent=True):
        """
        Log sexual activity to Google Fit
        
        Args:
            user_id: User identifier
            activity_type: Type of activity ("sex" or "masturbation")
            duration_minutes: Duration in minutes
            heart_rate: Optional average heart rate
            calories: Optional calories burned
            require_consent: Whether to require consent
            
        Returns:
            Dict with status information
        """
        # Safety check
        if require_consent and self.safety_manager:
            if not self.safety_manager.check_consent(user_id, "activity_tracking"):
                return {
                    "status": "error",
                    "message": "Consent required for activity tracking",
                    "requires_consent": True
                }
            
            if not self.safety_manager.verify_age(user_id):
                return {
                    "status": "error", 
                    "message": "Age verification required",
                    "requires_verification": True
                }
        
        if not self.fitness_service:
            if not self.initialize_service():
                return {
                    "status": "error",
                    "message": "Could not initialize Google Fit service"
                }
        
        try:
            # Validate activity type
            if activity_type not in ["sex", "masturbation"]:
                return {
                    "status": "error",
                    "message": "Invalid activity type. Must be 'sex' or 'masturbation'"
                }
            
            # Calculate timestamps
            end_time = datetime.datetime.utcnow()
            start_time = end_time - datetime.timedelta(minutes=duration_minutes)
            
            # Convert to nanoseconds for Google Fit API
            end_nanos = int(end_time.timestamp() * 1000000000)
            start_nanos = int(start_time.timestamp() * 1000000000)
            
            # Map activity type to Google Fit activity value
            # We'll use custom values since Google Fit doesn't have specific codes for these activities
            # 3000001 = sex, 3000002 = masturbation (using high numbers to avoid conflicts)
            activity_value = 3000001 if activity_type == "sex" else 3000002
            
            # Build dataset
            data_set = {
                "dataSourceId": self.data_source_id,
                "minStartTimeNs": start_nanos,
                "maxEndTimeNs": end_nanos,
                "point": [
                    {
                        "startTimeNanos": start_nanos,
                        "endTimeNanos": end_nanos,
                        "dataTypeName": "com.google.activity.segment",
                        "value": [
                            {
                                "intVal": activity_value
                            }
                        ]
                    }
                ]
            }
            
            # Log activity data to Google Fit
            self.fitness_service.users().dataSources().datasets().patch(
                userId='me',
                dataSourceId=self.data_source_id,
                datasetId=f"{start_nanos}-{end_nanos}",
                body=data_set
            ).execute()
            
            # If heart rate data is provided, log that too
            if heart_rate:
                self._log_heart_rate(start_nanos, end_nanos, heart_rate)
            
            # If calorie data is provided, log that too
            if calories:
                self._log_calories(start_nanos, end_nanos, calories)
            
            # Store activity in local history
            if user_id not in self.activity_history:
                self.activity_history[user_id] = []
            
            self.activity_history[user_id].append({
                "activity_type": activity_type,
                "duration_minutes": duration_minutes,
                "heart_rate": heart_rate,
                "calories": calories,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            })
            
            logger.info(f"Activity logged for user {user_id}: {activity_type} for {duration_minutes} minutes")
            
            return {
                "status": "success",
                "message": f"{activity_type.capitalize()} activity logged successfully",
                "duration_minutes": duration_minutes,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error logging activity: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to log activity: {str(e)}"
            }
    
    def _log_heart_rate(self, start_nanos, end_nanos, heart_rate):
        """Log heart rate data to Google Fit"""
        try:
            # Create or get heart rate data source
            heart_rate_source_id = "derived:com.google.heart_rate.bpm:Hextrix:AI:hextrix_heart_rate"
            
            # Build heart rate dataset
            heart_rate_data = {
                "dataSourceId": heart_rate_source_id,
                "minStartTimeNs": start_nanos,
                "maxEndTimeNs": end_nanos,
                "point": [
                    {
                        "startTimeNanos": start_nanos,
                        "endTimeNanos": end_nanos,
                        "dataTypeName": "com.google.heart_rate.bpm",
                        "value": [
                            {
                                "fpVal": float(heart_rate)
                            }
                        ]
                    }
                ]
            }
            
            # Log heart rate data to Google Fit
            self.fitness_service.users().dataSources().datasets().patch(
                userId='me',
                dataSourceId=heart_rate_source_id,
                datasetId=f"{start_nanos}-{end_nanos}",
                body=heart_rate_data
            ).execute()
            
            logger.info(f"Heart rate data logged: {heart_rate} bpm")
            return True
        except Exception as e:
            logger.error(f"Error logging heart rate: {str(e)}")
            return False
    
    def _log_calories(self, start_nanos, end_nanos, calories):
        """Log calorie data to Google Fit"""
        try:
            # Create or get calories data source
            calories_source_id = "derived:com.google.calories.expended:Hextrix:AI:hextrix_calories"
            
            # Build calories dataset
            calories_data = {
                "dataSourceId": calories_source_id,
                "minStartTimeNs": start_nanos,
                "maxEndTimeNs": end_nanos,
                "point": [
                    {
                        "startTimeNanos": start_nanos,
                        "endTimeNanos": end_nanos,
                        "dataTypeName": "com.google.calories.expended",
                        "value": [
                            {
                                "fpVal": float(calories)
                            }
                        ]
                    }
                ]
            }
            
            # Log calories data to Google Fit
            self.fitness_service.users().dataSources().datasets().patch(
                userId='me',
                dataSourceId=calories_source_id,
                datasetId=f"{start_nanos}-{end_nanos}",
                body=calories_data
            ).execute()
            
            logger.info(f"Calories data logged: {calories} kcal")
            return True
        except Exception as e:
            logger.error(f"Error logging calories: {str(e)}")
            return False
    
    def get_activity_stats(self, user_id, days=30, require_consent=True):
        """
        Get statistics about sexual activities
        
        Args:
            user_id: User identifier
            days: Number of days to analyze
            require_consent: Whether to require consent
            
        Returns:
            Dict with activity statistics
        """
        # Safety check
        if require_consent and self.safety_manager:
            if not self.safety_manager.check_consent(user_id, "activity_tracking"):
                return {
                    "status": "error",
                    "message": "Consent required for activity tracking",
                    "requires_consent": True
                }
            
            if not self.safety_manager.verify_age(user_id):
                return {
                    "status": "error", 
                    "message": "Age verification required",
                    "requires_verification": True
                }
        
        if not self.fitness_service:
            if not self.initialize_service():
                return {
                    "status": "error",
                    "message": "Could not initialize Google Fit service"
                }
        
        try:
            # Calculate date range
            end_time = datetime.datetime.utcnow()
            start_time = end_time - datetime.timedelta(days=days)
            
            # Convert to milliseconds for Google Fit API
            end_millis = int(end_time.timestamp() * 1000)
            start_millis = int(start_time.timestamp() * 1000)
            
            # Get activity data from Google Fit
            result = self.fitness_service.users().dataset().aggregate(
                userId='me',
                body={
                    "aggregateBy": [{
                        "dataSourceId": self.data_source_id
                    }],
                    "bucketByTime": {"durationMillis": 86400000},  # Daily buckets
                    "startTimeMillis": start_millis,
                    "endTimeMillis": end_millis
                }
            ).execute()
            
            # Process the results
            sex_count = 0
            masturbation_count = 0
            sex_duration = 0
            masturbation_duration = 0
            
            for bucket in result.get('bucket', []):
                for dataset in bucket.get('dataset', []):
                    for point in dataset.get('point', []):
                        for value in point.get('value', []):
                            activity_type = value.get('intVal')
                            
                            # Calculate duration in minutes
                            start_ns = int(point.get('startTimeNanos', 0))
                            end_ns = int(point.get('endTimeNanos', 0))
                            duration_minutes = (end_ns - start_ns) / (60 * 1000000000)
                            
                            if activity_type == 3000001:  # Sex
                                sex_count += 1
                                sex_duration += duration_minutes
                            elif activity_type == 3000002:  # Masturbation
                                masturbation_count += 1
                                masturbation_duration += duration_minutes
            
            # Calculate averages and other statistics
            total_count = sex_count + masturbation_count
            total_duration = sex_duration + masturbation_duration
            
            avg_sex_duration = sex_duration / max(1, sex_count)
            avg_masturbation_duration = masturbation_duration / max(1, masturbation_count)
            
            # Calculate estimated calories based on average MET values
            # MET values: ~3.0 for masturbation, ~5.8 for sex (approximate values)
            # Calories = MET * weight(kg) * duration(hours)
            # Assuming 70kg weight for this example
            weight_kg = 70  # This should ideally be user-specific
            
            est_sex_calories = (5.8 * weight_kg * (sex_duration / 60)) 
            est_masturbation_calories = (3.0 * weight_kg * (masturbation_duration / 60))
            total_calories = est_sex_calories + est_masturbation_calories
            
            return {
                "status": "success",
                "period_days": days,
                "total_activities": total_count,
                "sex_count": sex_count,
                "masturbation_count": masturbation_count,
                "sex_duration_minutes": round(sex_duration, 1),
                "masturbation_duration_minutes": round(masturbation_duration, 1),
                "total_duration_minutes": round(total_duration, 1),
                "avg_sex_duration_minutes": round(avg_sex_duration, 1),
                "avg_masturbation_duration_minutes": round(avg_masturbation_duration, 1),
                "estimated_calories": round(total_calories, 1),
                "estimated_sex_calories": round(est_sex_calories, 1),
                "estimated_masturbation_calories": round(est_masturbation_calories, 1),
                "activities_per_week": round(total_count * 7 / days, 1)
            }
            
        except Exception as e:
            logger.error(f"Error getting activity stats: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get activity statistics: {str(e)}"
            }
    
    def estimate_activity_metrics(self, activity_type, duration_minutes, user_weight_kg=None, user_age=None, user_gender=None):
        """
        Estimate metrics for sexual activity without logging
        
        Args:
            activity_type: Type of activity ("sex" or "masturbation")
            duration_minutes: Duration in minutes
            user_weight_kg: User's weight in kg
            user_age: User's age
            user_gender: User's gender
            
        Returns:
            Dict with estimated metrics
        """
        try:
            # Default values if not provided
            weight_kg = user_weight_kg or 70
            age = user_age or 30
            gender = user_gender or "male"
            
            # Base MET values
            base_met_sex = 5.8
            base_met_masturbation = 3.0
            
            # Adjust MET based on gender
            gender_factor = 0.9 if gender.lower() == "female" else 1.0
            
            # Adjust MET based on age (simplified)
            age_factor = 1.0
            if age > 50:
                age_factor = 0.85
            elif age < 25:
                age_factor = 1.1
            
            # Calculate final MET values
            met_sex = base_met_sex * gender_factor * age_factor
            met_masturbation = base_met_masturbation * gender_factor * age_factor
            
            # Select MET based on activity type
            met = met_sex if activity_type == "sex" else met_masturbation
            
            # Calculate calories burned
            # Calories = MET * weight(kg) * duration(hours)
            calories = met * weight_kg * (duration_minutes / 60)
            
            # Estimate average heart rate
            # This is a simple estimation and would need to be refined
            # with actual data, as heart rate varies greatly by individual fitness level
            resting_hr = 70  # Assumed resting heart rate
            max_hr = 220 - age  # Estimated max heart rate
            
            # For sex, assume HR is about 50-70% of max HR
            # For masturbation, assume HR is about 40-60% of max HR
            if activity_type == "sex":
                avg_hr_percent = 0.6  # 60% of max HR
            else:
                avg_hr_percent = 0.5  # 50% of max HR
            
            estimated_hr = resting_hr + (max_hr - resting_hr) * avg_hr_percent
            
            return {
                "activity_type": activity_type,
                "duration_minutes": duration_minutes,
                "estimated_calories": round(calories, 1),
                "estimated_heart_rate": round(estimated_hr, 1),
                "metabolic_equivalent": round(met, 1),
                "intensity": "moderate" if met < 6 else "vigorous"
            }
            
        except Exception as e:
            logger.error(f"Error estimating metrics: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to estimate metrics: {str(e)}"
            }
    
    def get_user_activity_history(self, user_id, limit=10, require_consent=True):
        """
        Get recent activity history for a user
        
        Args:
            user_id: User identifier 
            limit: Maximum number of activities to return
            require_consent: Whether to require consent
            
        Returns:
            List of activity entries
        """
        # Safety check
        if require_consent and self.safety_manager:
            if not self.safety_manager.check_consent(user_id, "activity_tracking"):
                return {
                    "status": "error",
                    "message": "Consent required for activity tracking",
                    "requires_consent": True
                }
        
        # Check if we have local history for this user
        if user_id in self.activity_history:
            # Return most recent activities first
            history = sorted(self.activity_history[user_id], 
                            key=lambda x: x["end_time"], 
                            reverse=True)
            
            return {
                "status": "success",
                "history": history[:limit]
            }
        else:
            return {
                "status": "success",
                "history": []
            }
