import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse.linalg import svds
from sklearn.preprocessing import normalize

class Similarity:
    def __init__(self, reviews, businesses):
        self.reviews = reviews
        self.businesses = businesses
        self.tfidf_vectorizer = TfidfVectorizer(stop_words = 'english', max_df = 0.7, min_df = 75)
        self.tfidf_reviews = self.tfidf_vectorizer.fit_transform([x.text for x in self.reviews])
        # for each of the words in the vocabulary, check if its english
        # if not, remove it from the vocabulary
        self.tfidf_vectorizer.vocabulary_ = self.tfidf_vectorizer.vocabulary_


        docs_compressed, s, words_compressed = svds(self.tfidf_reviews, k=40)
        self.words_compressed = words_compressed.transpose()

        self.word_to_index = self.tfidf_vectorizer.vocabulary_
        self.index_to_word = {i: t for t, i in self.word_to_index.items()}

        # normalize the rows
        self.docs_compressed_normed = normalize(docs_compressed)

    def jaccard(self, business1, business2):
        # intersect over union
        cat1 = self.businesses[business1].categories
        cat2 = self.businesses[business2].categories
        cat1_tok = set(cat1.split(","))
        cat2_tok = set(cat2.split(","))
        return len(cat1_tok.intersection(cat2_tok)) / len(cat1_tok.union(cat2_tok))

    def text_mining(self, query, valid_businesses, favrestaurant_id):
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
        if valid_businesses is not None:
            cuisine_businesses_map = {
                k: v for k, v in business_map.items() if k in valid_businesses}
            business_map = cuisine_businesses_map
        if favrestaurant_id == None:
            return business_map
        jacc_sim_businesses = {}
        for k, v in business_map.items():
            jacc_sim_businesses[k] = self.jaccard(
                k, favrestaurant_id) + business_map[k]
        return {k: v for k, v in sorted(jacc_sim_businesses.items(), key=lambda item: item[1], reverse=True) if k != favrestaurant_id}
