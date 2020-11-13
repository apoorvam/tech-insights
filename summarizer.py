import json
import math
import re
from collections import Counter
from os import listdir
import nltk
from nltk.corpus import reuters, stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
import uuid
import main

SUMMARY_LENGTH = 3
ideal_sent_length = 20.0
dataset_path = "clean_dataset/"

class Summarizer:

    def __init__(self):
        nltk.download('punkt')
        nltk.download('reuters')
        nltk.download('stopwords')
        self.stemmer = nltk.SnowballStemmer("english")
        self.stop_words = stopwords.words('english')

    def generate_summaries(self):
        self.__build_TFIDF_model()

        docs_list = listdir(dataset_path)
        count = 0
        for doc_json in docs_list:
            with open(dataset_path + doc_json, 'r', encoding="latin-1") as file:
                print(doc_json)
                if ".json" in doc_json:
                    doc = json.load(file)
                    article_id = str(uuid.uuid4())
                    title = doc['title'].strip()
                    url = doc['url']
                    doc = doc['text'].strip()
                    if doc.startswith(title):
                        doc = doc[len(title):].strip()

                    scores = Counter()
                    self.__score_sentences(scores, doc, title)
                    highest_scores = scores.most_common(SUMMARY_LENGTH)
                    summary = ''
                    for sentence in highest_scores:
                        summary += ' ' + self.__getSentence(summary, sentence[0])
                    count += 1
                    print(count)
                    main.store_article(article_id, title, summary.strip(), url)
        return

    def __getSentence(self, summary, str):
        if len((summary+' '+str).encode('utf-8')) > 1500:
            return ''
        else:
            return str


    def __build_TFIDF_model(self):
        """ Build term-document matrix containing TF-IDF score for each word in each document
                    in the Reuters corpus news (via NLTK).
                """
        token_dict = {}
        for article in reuters.fileids():
            token_dict[article] = reuters.raw(article)

        # Use TF-IDF to determine frequency of each word in our article, relative to the
        # word frequency distributions in corpus of 11k Reuters news articles.
        self._tfidf = TfidfVectorizer(tokenizer=self.__tokenize_and_stem, stop_words='english', decode_error='ignore')
        tdm = self._tfidf.fit_transform(token_dict.values())  # Term-document matrix

    def __tokenize_and_stem(self, text):
        tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
        filtered = []

        # filter out numeric tokens, raw punctuation, etc.
        for token in tokens:
            if re.search('[a-zA-Z]', token):
                filtered.append(token)
        stems = [self.stemmer.stem(t) for t in filtered]
        return stems

    def __score_sentences(self, scores, doc, title):
        sentences = self.__split_into_sentences(doc)
        frequency_scores = self.__frequency_scores(doc)

        if frequency_scores is not None:
            for i, s in enumerate(sentences):
                headline_score = self.__headline_score(title, s) * 1.5
                length_score = self.__length_score(self.__split_into_words(s)) * 1.0
                position_score = self.__position_score(float(i + 1), len(sentences)) * 1.0
                frequency_score = frequency_scores[i] * 4
                score = (headline_score + frequency_score + length_score + position_score) / 4.0
                scores[s] = score

    def __split_into_sentences(self, text):
        tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        sentences = tokenizer.tokenize(text)
        return sentences

    def __split_into_words(self, text):
        """ Split a sentence string into an array of words """
        try:
            text = re.sub(r'[^\w ]', '', text)  # remove non-words
            return [w.strip('.').lower() for w in text.split()]
        except TypeError:
            return None

    def __frequency_scores(self, doc):
        # Add our document into the model so we can retrieve scores
        response = self._tfidf.transform([doc])
        feature_names = self._tfidf.get_feature_names()  # these are just stemmed words

        word_prob = {}  # TF-IDF individual word probabilities
        for col in response.nonzero()[1]:
            word_prob[feature_names[col]] = response[0, col]

        sent_scores = []
        for sentence in self.__split_into_sentences(doc):
            score = 0
            sent_tokens = self.__tokenize_and_stem(sentence)
            for token in (t for t in sent_tokens if t in word_prob):
                score += word_prob[token]

            # Normalize score by length of sentence, since we later factor in sentence length as a feature
            if len(sent_tokens) == 0:
                return sent_scores.append(0)
            sent_scores.append(score / len(sent_tokens))

        return sent_scores

    def __headline_score(self, title, sentence):
        title_stems = [self.stemmer.stem(w) for w in title if w not in self.stop_words]
        sentence_stems = [self.stemmer.stem(w) for w in sentence if w not in self.stop_words]
        count = 0.0
        for word in sentence_stems:
            if word in title_stems:
                count += 1.0
        if len(title_stems) == 0:
            return 0
        score = count / len(title_stems)
        return score

    def __length_score(self, words):
        len_diff = math.fabs(ideal_sent_length - len(words))
        return len_diff / ideal_sent_length

    def __position_score(self, position, sentence_length):
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
