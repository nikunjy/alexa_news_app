from flask import Flask
from flask_ask import Ask, question, statement
import requests
import json
import os
import unidecode
app = Flask(__name__)
ask = Ask(app, "/")


def _get_headlines():
    """
    Gets the headlines from new york times
    :return:
    """
    url = "http://api.nytimes.com/svc/topstories/v2/world.json?api-key=66fa8330903e437783df1965800be3d7"
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
    headline_string = _get_headlines()
    return statement(headline_string)


@app.route('/')
def homepage():
    return _get_headlines()


@ask.launch
def start_skill():
  return question("Would you like the top news ?")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port = port)