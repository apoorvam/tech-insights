import math
import re
from collections import Counter

import nltk
from nltk.corpus import reuters, stopwords
from sklearn.feature_extraction.text import TfidfVectorizer

SUMMARY_LENGTH = 10
ideal_sent_length = 20.0
stemmer = nltk.SnowballStemmer("english")
stop_words = stopwords.words('english')

class Summarizer:
    def __init__(self, doc, url, title):
        self.url = url
        self.doc = doc
        self.title = title

    def generate_summaries(self):
        self.build_TFIDF_model()

        self._scores = Counter()
        self.score_sentences()

        highest_scores = self._scores.most_common(SUMMARY_LENGTH)

        self.summary = ' '.join([sentence[0] for sentence in highest_scores])

        return self.summary


    def build_TFIDF_model(self):
        """ Build term-document matrix containing TF-IDF score for each word in each document
                    in the Reuters corpus news (via NLTK).
                """
        token_dict = {}
        for article in reuters.fileids():
            token_dict[article] = reuters.raw(article)

        # Use TF-IDF to determine frequency of each word in our article, relative to the
        # word frequency distributions in corpus of 11k Reuters news articles.
        self._tfidf = TfidfVectorizer(tokenizer=self.tokenize_and_stem, stop_words='english', decode_error='ignore')
        tdm = self._tfidf.fit_transform(token_dict.values())  # Term-document matrix

    def tokenize_and_stem(self, text):
        tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
        filtered = []

        # filter out numeric tokens, raw punctuation, etc.
        for token in tokens:
            if re.search('[a-zA-Z]', token):
                filtered.append(token)
        stems = [stemmer.stem(t) for t in filtered]
        return stems

    def score_sentences(self):
        sentences = self.split_into_sentences(self.doc)
        frequency_scores = self.frequency_scores(self.doc)

        for i, s in enumerate(sentences):
            headline_score = self.headline_score(self.title, s) * 1.5
            length_score = self.length_score(self.split_into_words(s)) * 1.0
            position_score = self.position_score(float(i + 1), len(sentences)) * 1.0
            frequency_score = frequency_scores[i] * 4
            score = (headline_score + frequency_score + length_score + position_score) / 4.0
            self._scores[s] = score

    def split_into_sentences(self, text):
        tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        sentences = tokenizer.tokenize(text)
        return sentences

    def split_into_words(self, text):
        """ Split a sentence string into an array of words """
        try:
            text = re.sub(r'[^\w ]', '', text)  # remove non-words
            return [w.strip('.').lower() for w in text.split()]
        except TypeError:
            return None

    def frequency_scores(self, doc):
        # Add our document into the model so we can retrieve scores
        response = self._tfidf.transform([doc])
        feature_names = self._tfidf.get_feature_names()  # these are just stemmed words

        word_prob = {}  # TF-IDF individual word probabilities
        for col in response.nonzero()[1]:
            word_prob[feature_names[col]] = response[0, col]

        sent_scores = []
        for sentence in self.split_into_sentences(doc):
            score = 0
            sent_tokens = self.tokenize_and_stem(sentence)
            for token in (t for t in sent_tokens if t in word_prob):
                score += word_prob[token]

            # Normalize score by length of sentence, since we later factor in sentence length as a feature
            sent_scores.append(score / len(sent_tokens))

        return sent_scores

    def headline_score(self, title, sentence):
        title_stems = [stemmer.stem(w) for w in title if w not in stop_words]
        sentence_stems = [stemmer.stem(w) for w in sentence if w not in stop_words]
        count = 0.0
        for word in sentence_stems:
            if word in title_stems:
                count += 1.0
        score = count / len(title_stems)
        return score

    def length_score(self, words):
        len_diff = math.fabs(ideal_sent_length - len(words))
        return len_diff / ideal_sent_length

    def position_score(self, position, sentence_length):
        relative_position = position / sentence_length
        if 0 < relative_position <= 0.1:
            return 0.17
        elif 0.1 < relative_position <= 0.2:
            return 0.23
        elif 0.2 < relative_position <= 0.3:
            return 0.14
        elif 0.3 < relative_position <= 0.4:
            return 0.08
        elif 0.4 < relative_position <= 0.5:
            return 0.05
        elif 0.5 < relative_position <= 0.6:
            return 0.04
        elif 0.6 < relative_position <= 0.7:
            return 0.06
        elif 0.7 < relative_position <= 0.8:
            return 0.04
        elif 0.8 < relative_position <= 0.9:
            return 0.04
        elif 0.9 < relative_position <= 1.0:
            return 0.15
        else:
            return 0

