from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix

class ModelTrainer:
    def __init__(self, user_data):
        self.vectorizer = CountVectorizer()
        self.classifier = MultinomialNB()
        self.user_data = user_data
        self.trained = False
        self.labels = []

    def train_model(self):
        if len(self.user_data.queries) > 5:
            X = self.vectorizer.fit_transform(self.user_data.queries)
            y = self.labels
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
            self.classifier.fit(X_train, y_train)
            accuracy = accuracy_score(y_test, self.classifier.predict(X_test))
            self.trained = True
            return accuracy

    def predict_category(self, query):
        if self.trained:
            X = self.vectorizer.transform([query])
            return self.classifier.predict(X)[0]
        return "unknown"
