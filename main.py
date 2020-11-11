# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime

from flask import Flask, render_template, request
from google.auth.transport import requests
from google.cloud import datastore
import google.oauth2.id_token

firebase_request_adapter = requests.Request()

# [START gae_python38_datastore_store_and_fetch_user_times]
datastore_client = datastore.Client()

# [END gae_python38_datastore_store_and_fetch_user_times]
app = Flask(__name__)


# [START gae_python38_datastore_store_and_fetch_user_times]
def store_article():
    entity = datastore.Entity(key=datastore_client.key('Article',
                                                       '0a10f9d3e931d1f3ef201f05ff0e3b6b42ce6b16'))
    entity.update({
        'title': 'Brightcove Introduces Jump Start for Apple TV® to Accelerate New Video Apps on Fourth-Generation Apple TV®',
        'summary': 'Brightcove Inc. (NASDAQ: BCOV), the leading provider of cloud services for video, today announced Brightcove Jump Start for Apple TV® , a new service offering to enable publishers to quickly launch video apps on the fourth-generation Apple TV®. For a limited time, starting at $10,000 USD, the new Jump Start offering builds on Brightcove’s existing expertise and history of delivering and monetizing a range of beautiful video experiences on the Apple TV® platform and across the Apple® ecosystem.',
        'article_url': 'https://www.brightcove.com/en/company/press/brightcove-introduces-jump-start-apple-tv-accelerate-new-video-apps-fourth-generation-apple-tv'
    })

    datastore_client.put(entity)


def fetch_articles(limit):
    query = datastore_client.query(kind='Article')
    articles = query.fetch(limit=limit)
    return articles


# [START gae_python38_datastore_render_user_times]
@app.route('/')
def root():
    # Verify Firebase auth.
    id_token = request.cookies.get("token")
    error_message = None
    articles = fetch_articles(1)

    return render_template(
        'index.html',
        article_data=articles, error_message=error_message)
# [END gae_python38_datastore_render_user_times]


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.

    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
