# tech-insights

TechInsights is a simplified news site for busy technologists with links and summaries of latest
 updates in the tech industry. It provides a collection of articles,
simplified AI generated short summary, link to original article and a audio version of the news that one can listen to as they start day. 

## Project Tech Stack

* Languages: Python, JS, HTML
* Hosting: Google Cloud App engine, Firebase
* Frameworks/Libraries: Google text to speech API, nltk, sklearn
 
**Dataset source**: [TLDR newsletter](https://www.tldrnewsletter.com)

## Project setup and usage

* Run `python -r requirements.txt` to install dependencies.
* Set Firebase API_KEY and GOOGLE_APPLICATION_CREDENTIALS in the environment to access Firebase
 storage and for hosting. 
 
## Summarizer model

Summarizer developed is an Extractive text summarizer. Extractive text summarization involves the selection of phrases and sentences from the source document to make up the new summary. Techniques involve ranking the relevance of phrases in order to choose only those most relevant to the meaning of the source.
The algorithm uses a number of features to score the relevance of a sentence:

* TF IDF: is a numerical statistic that reflects how important a word is to a document in a
 collection or corpus. The tf–idf value increases proportionally to the number of times a word appears in the document and is offset by the number of documents in the corpus that contain the word.
* Similarity to headline
* Position of the sentence in the article: This assumes that sentences in the starting and in the
 ending are more important
* Length of the sentence

All of these are weighted to produce a single score for each sentence in the article and the most important sentences are picked to form the summary.
