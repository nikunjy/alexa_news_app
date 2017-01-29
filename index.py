from flask import Flask
from flask_ask import Ask, question, statement, convert_errors
import requests
import random
import json
import os
import unidecode
import config
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
ask = Ask(app, "/")

API_KEY = config.NYTIMES_API_KEY
TOPIC_FILE = "NYT_TOPICS"
REPROMPT_MSG = "You can say topics like world, technology, science, arts"
MAX_NUM_HEADLINES = 5


def _get_topic_mapping():
    data = {}
    with open("topic_mapping") as f:
        data = json.load(f)
    reverse_index = {}
    for topic in data:
        for mapping in data.get(topic):
            reverse_index[mapping.lower()] = topic.lower()
    return reverse_index


def _get_list_of_topics():
    with open(TOPIC_FILE) as f:
        content = f.readlines()
    content = [x.strip().lower() for x in content]
    return content

GLOBAL_LIST_TOPICS = _get_list_of_topics()
REVERSE_INDEX = _get_topic_mapping()


def _get_from_topics_or_index(topic):
    if topic in GLOBAL_LIST_TOPICS:
        return topic
    if REVERSE_INDEX.get(topic, None):
        return REVERSE_INDEX[topic]
    return None


def _get_valid_topic(topic):
    valid_topic = _get_from_topics_or_index(topic)
    if valid_topic is not None:
        return valid_topic

    tokens = topic.split()
    for token in tokens:
        valid_topic = _get_from_topics_or_index(token)
        if valid_topic is not None:
            return valid_topic
    return None


def _get_headlines(headline_topic):
    """
    Gets the headlines from new york times
    :return:
    """
    url_format = "http://api.nytimes.com/svc/topstories/v2/%s.json?api-key=%s"
    url = url_format % (headline_topic, API_KEY)
    logger.info(url)
    data = json.loads(requests.get(url).text)
    headlines = []
    for result in data.get("results"):
        headline = unidecode.unidecode(result.get("title"))
        abstract = unidecode.unidecode(result.get("abstract"))
        headline = "{}, {}".format(headline, abstract)
        headlines.append(headline)
    headline_string = "Top {} headlines for the topic {} are : ".format(MAX_NUM_HEADLINES, headline_topic)
    random.shuffle(headlines)
    index = 1
    for headline_d in headlines:
        headline = unidecode.unidecode(headline_d)
        headline_text = "Headline {} : {}".format(index, headline)
        index += 1
        headline_string += headline_text + ". "
        if index == MAX_NUM_HEADLINES:
            break
    logger.info(headline_string)
    return headline_string


@ask.intent("GetNewsIntent", mapping={'topic': 'Topic'}, convert={'topic': str})
def get_headlines(topic):
    if topic is None or 'Topic' in convert_errors or 'topic' in convert_errors:
        return question("Can you say your topic again").reprompt(REPROMPT_MSG)
    topic = topic.lower()
    logger.info(topic)
    topic = _get_valid_topic(topic)
    if topic is None:
        return question("I don't understand that topic").reprompt(REPROMPT_MSG)
    headline_string = _get_headlines(topic)
    return statement(headline_string)


@ask.intent("AllTopicsIntent")
def get_all_topics():
    logger.info("Getting list of all topics")
    topics = _get_list_of_topics()
    msg = "Topics are "
    for topic in topics:
        msg += topic + ", "
    return question(msg + ", so now, what would you like the news for ?")


@app.route('/')
def homepage():
    return _get_headlines("world")


@ask.intent('AMAZON.HelpIntent')
def help():
  return statement(REPROMPT_MSG)


@ask.intent('AMAZON.StopIntent')
def stop():
    return statement("Goodbye")


@ask.intent('AMAZON.CancelIntent')
def cancel():
    return statement("Goodbye")


@ask.launch
def start_skill():
    reprompt_msg = REPROMPT_MSG
    return question("What topic would you like the top news for ?").reprompt(reprompt_msg)

if __name__ == '__main__':
    logger.info(GLOBAL_LIST_TOPICS)
    logger.info(REVERSE_INDEX)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)