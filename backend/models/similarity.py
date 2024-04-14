import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse.linalg import svds
from sklearn.preprocessing import normalize


class Similarity:
    def __init__(self, reviews, businesses):
        self.reviews = reviews
        self.businesses = businesses

        self.cuisinereviews = []
        self.cuisinetfidf_vectorizer = TfidfVectorizer()
        self.cuisinetfidf_reviews = None

        self.tfidf_vectorizer = TfidfVectorizer()
        self.tfidf_reviews = self.tfidf_vectorizer.fit_transform(
            [x.text for x in self.reviews])

        docs_compressed, s, words_compressed = svds(self.tfidf_reviews, k=40)
        self.words_compressed = words_compressed.transpose()

        word_to_index = self.tfidf_vectorizer.vocabulary_
        index_to_word = {i: t for t, i in word_to_index.items()}

        # normalize the rows
        self.docs_compressed_normed = normalize(docs_compressed)

    # def set_cuisine_reviews(self, cuisine):
    #     self.

    def text_mining(self, query):
        query_tfidf = self.tfidf_vectorizer.transform([query]).toarray()
        query_vec = normalize(
            np.dot(query_tfidf, self.words_compressed)).squeeze()
        sims = self.docs_compressed_normed.dot(query_vec)
        asort = np.argsort(-sims)
        business_map = {}
        for i in asort:
            business_map[self.reviews[i].business_id] = business_map.get(
                self.reviews[i].business_id, 0) + sims[i]
        # averaging scores over review count
        for k, v in business_map.items():
            business_map[k] = v / self.businesses[k].review_count
        # order by similarity
        business_map = {k: v for k, v in sorted(
            business_map.items(), key=lambda item: item[1], reverse=True)}
        return business_map
