import numpy as np
from collections import Counter

class Introspection:
    def __init__(self, user_data):
        self.user_data = user_data
        self.introspection_log = []

    def introspect(self):
        report = f"Total queries: {len(self.user_data.queries)}\n"
        strengths = [label for label, count in Counter(self.user_data.queries).items() if count > 2]
        report += f"Strengths: {', '.join(strengths)}\n"
        self.introspection_log.append(report)
        return report
