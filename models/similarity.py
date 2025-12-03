import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from scipy.sparse.linalg import svds
from sklearn.preprocessing import normalize

class Similarity:
    def __init__(self, reviews, businesses):
        self.reviews = reviews
        self.businesses = businesses
        # Combine English stop words with specific stop words
        specific_stop_words = ["food", "good", "place", "tucson", "one"]
        custom_stop_words = set(ENGLISH_STOP_WORDS) | set(specific_stop_words)
        self.tfidf_vectorizer = TfidfVectorizer(stop_words=custom_stop_words, max_df=0.7, min_df=75)
        self.tfidf_reviews = self.tfidf_vectorizer.fit_transform([x.text for x in self.reviews])

        docs_compressed, s, words_compressed = svds(self.tfidf_reviews, k=40)
        self.words_compressed = words_compressed.transpose()

        self.word_to_index = self.tfidf_vectorizer.vocabulary_
        self.index_to_word = {i: t for t, i in self.word_to_index.items()}

        # normalize the rows
        self.docs_compressed_normed = normalize(docs_compressed)

        # This Code was run to find the words in each dimension and name them    

        # for i in range(40):
        #     print("Top words in dimension", i)
        #     dimension_col = self.words_compressed[:,i].squeeze()
        #     asort = np.argsort(-dimension_col)
        #     print([self.index_to_word[i] for i in asort[:10]])
        #     print()

        # These are the names we produced for each dimension   
  
        self.dimension_names = ["General Quality", "Outstanding Experience", "Personal Favorites", "Quality & Value", "Pleasurable Visits", "Menu Variety", "Happy Hour", "Lunch Worth", "Casual Dining", "Relaxed Atmosphere", "Happy Hour Variety", "Meal Times", "Service & Waiting", "Service Recommendation", "Friendly Atmosphere", "Diverse Menu", "Local Flavors", "Quality Meals", "Casual Socializing", "Trendy Choices", "Sandwich Specialties", "Recommendation Quality", "Meal Experience", "Efficient Service", "Culinary Excellence", "Community Feel", "Evening Enjoyment", "Friendly Service", "Social Dining", "Cherished Moments", "Sushi Bar Experience", "Morning Delights", "Taco Bar Fun", "General Appreciation", "Casual Favorites", "Casual Comfort", "Local Favorites", "Authentic Cuisine", "Exceptional Service", "Satisfactory Dining"]


    def jaccard(self, business1, business2):
        # intersect over union
        cat1 = self.businesses[business1].categories
        cat2 = self.businesses[business2].categories
        cat1_tok = set(cat1.split(","))
        cat2_tok = set(cat2.split(","))
        return len(cat1_tok.intersection(cat2_tok)) / len(cat1_tok.union(cat2_tok))
    
    def dimension_scores(self, query):
        query_tfidf = self.tfidf_vectorizer.transform([query]).toarray()
        query_vec = normalize(np.dot(query_tfidf, self.words_compressed)).squeeze()
        adjusted_query_vec = query_vec - min(query_vec)
        dimension_scores = {self.dimension_names[i]: (adjusted_query_vec[i] + 1) / (max(adjusted_query_vec) + 1) for i in range(40)}
        return dimension_scores

    def text_mining(self, query, valid_businesses, favrestaurant_id):
        query_tfidf = self.tfidf_vectorizer.transform([query]).toarray()
        query_vec = normalize(np.dot(query_tfidf, self.words_compressed)).squeeze()

        # find the use SVD to rank the businesses
        sims = self.docs_compressed_normed.dot(query_vec)
        asort = np.argsort(-sims)
        business_map = {}
        for i in asort:
            business_map[self.reviews[i].business_id] = business_map.get(self.reviews[i].business_id, 0) + sims[i]

        # averaging scores over review count
        for k, v in business_map.items():
            business_map[k] = v / self.businesses[k].review_count

        # order by similarity
        business_map = {k: v for k, v in sorted(
            business_map.items(), key=lambda item: item[1], reverse=True)}
        if valid_businesses is not None:
            cuisine_businesses_map = {
                k: v for k, v in business_map.items() if k in valid_businesses}
            business_map = cuisine_businesses_map
        
        # check if user selected a fav restaurant
        if favrestaurant_id == None or len(favrestaurant_id) == 0:
            return business_map
        
        # calculate jaccard similarity with fav restaurant, and add to the score
        jacc_sim_businesses = {}
        for k, v in business_map.items():
            jacc_sim_businesses[k] = self.jaccard(
                k, favrestaurant_id) + business_map[k]
        return {k: v for k, v in sorted(jacc_sim_businesses.items(), key=lambda item: item[1], reverse=True) if k != favrestaurant_id}
