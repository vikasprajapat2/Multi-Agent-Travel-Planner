class RecommendationAgent:

    def __init__(self, vector_store):
        self.vector_store = vector_store

    def recommend_next_trip(self, query):
        similar = self.vector_store.search(query)

        return {
            "suggestion": "Based on your past trips",
            "similar_trips": similar
        }