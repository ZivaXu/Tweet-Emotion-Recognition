### HCDE 310 - Final Project: Tweet Emotion Recognition
### authors: Linda Lai, Ziva Xu

import webapp2, os, urllib2, json, jinja2, logging, urllib
# from django.utils.encoding import smart_str, smart_unicode

import requests
api_key = "e1pNeA7xCEAKhZoFF7w7RvArWVq0EOVvMxAJgA88UVc"


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
    combined_string = []
    for each_tweet in tweets:
        tweet_text = each_tweet.text
        combined_string.append(str(tweet_text.encode(errors='ignore').decode('utf-8')))
    return combined_string


# def create_plot_one():


# def create_plot_two():


###############
class MainHandler(webapp2.RequestHandler):
    def genpage(self, tag="#UW"):
        if tag[0] != "#":
            tag = "#" + tag     # make sure its a valid tag
        tweets_data = tweets_search(q=tag)
        combined_tweets = tweets_combine(tweets_data)
        text = "{}".format(combined_tweets[0:5])
        output = requests.post("https://apis.paralleldots.com/v5/emotion_batch", data={"api_key": api_key, "text": text}).json()

        # not sure what type of data the function tone_analyzer returns
        #
        # plot_one = create_plot_one()
        # plot_two = create_plot_two()
        #
        # tvals = {'tag': tag, 'plot_one': plot_one, 'plot_two': plot_two}
        tvals = {'tagname': tag, 'output': output}
        template = JINJA_ENVIRONMENT.get_template('template.html')
        self.response.write(template.render(tvals))

    def get(self):
        self.genpage()

    def post(self):
        tag = self.request.get('tag')
        self.genpage(tag)


application = webapp2.WSGIApplication([('/', MainHandler)], debug=True)
