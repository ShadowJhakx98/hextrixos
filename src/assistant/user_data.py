from collections import Counter, defaultdict
import datetime

class UserData:
    def __init__(self):
        self.queries = []
        self.weather_requests = defaultdict(Counter)
        self.time_requests = defaultdict(Counter)
        self.info_requests = defaultdict(Counter)

    def update_user_data(self, query, category):
        current_time = datetime.datetime.now()
        day_of_week = current_time.strftime('%A')
        hour = current_time.hour
        self.queries.append(query)
        getattr(self, f"{category}_requests")[day_of_week][hour] += 1
