from flask import Flask
from flask_ask import Ask, question, statement
import requests
import json
import os
import unidecode
import config
app = Flask(__name__)
ask = Ask(app, "/")
API_KEY = config.NYTIMES_API_KEY


def _get_headlines(headline_topic):
    """
    Gets the headlines from new york times
    :return:
    """
    url_format =  "http://api.nytimes.com/svc/topstories/v2/%s.json?api-key=%s"
    url = url_format % (headline_topic, API_KEY)
    print url
    data = json.loads(requests.get(url).text)
    headlines = []
    index = 1
    for result in data.get("results"):
        headline = unidecode.unidecode(result.get("title"))
        headline = "Headline {} : {}".format(index, headline)
        headlines.append(headline)
        index += 1
    headline_string = ""
    index = 1
    for headline_d in headlines:
        headline = unidecode.unidecode(headline_d)
        index += 1
        headline_string += headline + ". "
        if index == 5:
            break
    return headline_string


@ask.intent("GetNewsIntent")
def get_headlines():
    headline_string = _get_headlines("world")
    return statement(headline_string)


@app.route('/')
def homepage():
    return _get_headlines("world")


@ask.launch
def start_skill():
  return question("Would you like the top news ?")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)