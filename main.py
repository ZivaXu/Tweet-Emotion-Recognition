### HCDE 310 - Final Project: Tweet Emotion Recognition
### authors: Linda Lai, Ziva Xu

import webapp2, os, urllib2, json, jinja2, logging, urllib
from ibm_watson import ToneAnalyzerV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import ApiException

import plotly
import plotly.graph_objs as go
import pandas as pd
import numpy as np

import keys as keys     # file for api keys
import twitter      # A Python wrapper around the Twitter API.


JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
                                       extensions=['jinja2.ext.autoescape'],
                                       autoescape=True)

# Utility functions you may want to use
def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

def safeGet(url):  # not currently being used
    try:
        return urllib2.urlopen(url)
    except urllib2.URLError as e:
        logging.error("The server couldn't fulfill the request.")
        logging.error("Error code: ", e.code)
    except urllib2.URLError as e:
        logging.error("We failed to reach a server")
        logging.error("Reason: ", e.reason)
    return None



# fetch tweet data from twitter api
# only retrieves Tweets that have been sent in the last 7 days
# Returns a list of dictionaries
def tweets_search(ACCESS_TOKEN = keys.ACCESS_TOKEN,
    ACCESS_SECRET = keys.ACCESS_SECRET,
    CONSUMER_KEY = keys.CONSUMER_KEY,
    CONSUMER_SECRET = keys.CONSUMER_SECRET,
    params = {},
    q = '#UW',
    lang = 'en',   # by default, only retrieve tweets in English
    result_type = 'recent',
    count = '100'):
    params['q'] = q
    params['result_type'] = result_type
    params['count'] = count
    params['lang'] = lang
    query = urllib.urlencode(params)
    api = twitter.Api(consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token_key=ACCESS_TOKEN,
        access_token_secret=ACCESS_SECRET)
    logging.info("query: ", query)
    results = api.GetSearch(raw_query=query)
    return results


# combine all the tweets text into one string
# Returns a string (that will be processed with function tone_analyzer)
def tweets_combine(tweets):
    combined_string = tweets
    for each_tweet in tweets:
        tweet_text = each_tweet.text
        combined_string = combined_string + tweet_text + ".\n"
    return combined_string



# analyze the tone of the given text
watson_api = keys.WATSON_API

def tone_analyzer(tone_input,
    url="https://gateway.watsonplatform.net/tone-analyzer/api",
    content_type="application/json",
    sentences=False
    ):
    authenticator = IAMAuthenticator(watson_api)
    tone_analyzer = ToneAnalyzerV3(version='2017-09-21', authenticator=authenticator)
    tone_analyzer.set_service_url(url)
    text = tone_input
    try:
        return tone_analyzer.tone({'text': text}, content_type=content_type, sentences=sentences).get_result()
    except ApiException as ex:
        if hasattr(ex, "code"):
            logging.error("The server couldn't fulfill the request.")
            logging.error("Error code: ", ex.code)
        elif hasattr(ex, 'reason'):
            logging.error("We failed to reach a server")
            logging.error("Reason: ", ex.message)
        return None


def create_plot_one(): # this isn't final, just a sample call of the bar graph
    N = 40
    x = np.linspace(0, 1, N)
    y = np.random.randn(N)
    df = pd.DataFrame({'x': x, 'y': y}) # creating a sample dataframe
    data = [
        go.Bar(
            x=df['x'], # assign x as the dataframe column 'x'
            y=df['y']
        )
    ]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


# def create_plot_two():


###############
class MainHandler(webapp2.RequestHandler):
    def genpage(self, tag="#UW"):
        if tag[0] != "#":
            tag = "#" + tag     # make sure its a valid tag
        tweets_data = tweets_search(q=tag)
        combined_tweets = tweets_combine(tweets_data)
        tone_analyzer(combined_tweets)
        # not sure what type of data the function tone_analyzer returns

        plot_one = create_plot_one()
        plot_two = create_plot_two()

        tvals = {'tag': tag, 'plot_one': plot_one, 'plot_two': plot_two}
        template = JINJA_ENVIRONMENT.get_template('template.html')
        self.response.write(template.render(tvals))

    def get(self):
        self.genpage()

    def post(self):
        tag = self.request.get('tag')
        self.genpage(tag)


application = webapp2.WSGIApplication([('/', MainHandler)], debug=True)
