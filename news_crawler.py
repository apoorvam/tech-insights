import base64
import re
import sys

import time
import math
import urllib.request
import urllib.robotparser
import logging
from w3lib.url import url_query_cleaner
from urllib.parse import urlparse
from url_normalize import url_normalize
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from urllib.error import HTTPError
from queue import PriorityQueue
from bs4.element import Comment
import os
import sys
import json
from lxml import etree
import lxml.builder    

from urllib.error import URLError
from urllib.request import Request, urlopen
import nltk, string
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk import RegexpTokenizer
from simhash import Simhash, SimhashIndex


SEED_URL = 'https://www.tldrnewsletter.com/archives'


WRITE_MODE = "w+"
CRAWL_BATCH_SIZE = 10
SAVE_BATCH_SIZE = 10
CRAWL_MAXSIZE = 1000

known_domains = ['tldrnewsletter.com']

# list(map(canonical_url,urls))
# canonical_url("http://www.ccs.neu.edu/home/vip/teach/IRcourse/3_crawling_snippets/HW3/hw3.html" +"/../" +"../matt_es_client.zip")
# http://www.ccs.neu.edu/home/vip/teach/IRcourse/3_crawling_snippets/matt_es_client.zip


tokenizer = RegexpTokenizer(r"[\W.]+", gaps=True)

def tokenize(text):
    return tokenizer.tokenize(text.lower())


def cosine_sim(n_text1, n_text2):
    t1 = set(n_text1)
    count = 1
    for w in n_text2:
        if w in t1:
            count += 1
    return count


robots_allower = {}

def get_domain(url):
    parsed_uri = urlparse(url)
    return '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)


def get_hostname(url):
    return urlparse(url).hostname

def is_absolute(url):
    return bool(urlparse(url).netloc)


class Page:
    def __init__(self, url, raw_content, clean_content, a_tags):
        self.id = url
        self.url = url
        self.raw_content = raw_content
        self.clean_content = clean_content
        self.clean_out_links(a_tags)
        self.in_links = []
        self.wave_no = 0
        self.score = 0
        
    def clean_out_links(self, a_tags):
        links = {}
        for a in a_tags:
            if not a.has_attr('href'):
                continue
            link_url = a['href']
            links[link_url] =  a.get_text().strip()
            
        self.out_links = links
        
    
    def set_wave_no(self, wave_num):
        self.wave_no = wave_num
        
        
    def add_inlink(self, link):
        self.in_links.append(link)

        
    def set_score(self, score):
        self.score = score


        
def get_encoding(info):
    default = 'ISO-8859-1'
    return default    


def make_http_call(url):
    print(url)
    fp = urllib.request.urlopen(url)
    return fp

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if element.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def get_page_contents(url):
    url = urljoin(url, urlparse(url).path)
    req = Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36')
    raw_html = urlopen(req).read()
    soup = BeautifulSoup(raw_html, 'html.parser')
    for f in soup.find_all(id="footer"):
        f.decompose()
    for f in soup.find_all(class_="noprint"):
        f.decompose()
    for f in soup.find_all(id=re.compile("personal")):
        f.decompose()
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    a_tags = soup.find_all('a')
    contents = u" ".join(t.strip() for t in visible_texts)
    p = Page(url, raw_html, contents, a_tags)
    if sys.getsizeof(p.id) > 512:
        print("error: URL too long %s" % url)
        return -1
    soup.decompose()
    return p

# page = get_page_contents(SEED_DOCUMENTS[0], canonical_url(SEED_DOCUMENTS[0]))
# if page == -1:
#     print("Invalid url")



def valid_xml_char_ordinal(c):
    codepoint = ord(c)
    return (
        0x20 <= codepoint <= 0xD7FF or
        codepoint in (0x9, 0xA, 0xD) or
        0xE000 <= codepoint <= 0xFFFD or
        0x10000 <= codepoint <= 0x10FFFF)

def write_docs_to_file(p, filename):
    text = ''.join(c for c in p.clean_content if valid_xml_char_ordinal(c)) + " "
    text = ' '.join(text.split())
    content = p.url + "\n" + text
    fp = open(filename, "w+")
    fp.write(content)
    fp.close()


def crawl(seed):
    page = get_page_contents(seed)
    if page == -1:
        print("skipping url %s" % seed)
        return -1
    return page

blacklist = ["https://www.tldrnewsletter.com/?utm_source=fwd&utm_campaign={{ID}}", "https://www.tldrnewsletter.com/sponsor",
 "https://twitter.com/tldrdan", "{{UnsubscribeURL}}"]

archivesPage = crawl(SEED_URL)
archiveOutlinks = archivesPage.out_links
for path in archiveOutlinks:
    if path.startswith('/archives'):
        newsPage = crawl("https://www.tldrnewsletter.com"+path)
        articleLinks = newsPage.out_links
        for key, value in articleLinks.items():
            if key not in blacklist:
                articlePage = crawl(key)
                filename = "/Users/apoorvam/Projects/data/data_%s.txt" % (int(round(time.time() * 1000)))
                print(articlePage.url + " " + filename)
                write_docs_to_file(articlePage, filename)
                # sys.exit("Error message")



