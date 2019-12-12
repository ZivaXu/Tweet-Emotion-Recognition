### HCDE 310 - Final Project: Tweet Emotion Recognition
### authors: Linda Lai, Ziva Xu

import webapp2, os, urllib2, json, jinja2, logging, urllib
# from django.utils.encoding import smart_str, smart_unicode

import requests

import keys as keys     # file for api keys
import twitter      # A Python wrapper around the Twitter API.


JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
                                       extensions=['jinja2.ext.autoescape'],
                                       autoescape=True)


# # Utility functions you may want to use
# def pretty(obj):
#     return json.dumps(obj, sort_keys=True, indent=2)
#
#
# def safeGet(url):  # not currently being used
#     try:
#         return urllib2.urlopen(url)
#     except urllib2.URLError as e:
#         logging.error("The server couldn't fulfill the request.")
#         logging.error("Error code: ", e.code)
#     except urllib2.URLError as e:
#         logging.error("We failed to reach a server")
#         logging.error("Reason: ", e.reason)
#     return None



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



def fetch_each_tweet_emotion(tweet):
    # response = requests.post("https://apis.paralleldots.com/v5/emotion", data={"api_key": keys.pd_api_key, "text": tweet})
    response = requests.post("https://apis.paralleldots.com/v5/emotion", data={"api_key": keys.pd_api_key, "text": tweet}).json()
    logging.info(tweet)
    # output = json.load(response)["emotion"]
    print(response)
    output = response["emotion"]
    return output


# combine all the emotions of tweets into one list returns: [{'happy': 0.001115, 'sad': 0.015291, 'angry': 0.002552,
# 'fear': 0.003962, 'excited': 0.003927, 'indifferent': 0.973152}, {'happy': 0.001115, 'sad': 0.015291,
# 'angry': 0.002552, 'fear': 0.003962, 'excited': 0.003927, 'indifferent': 0.973152}...]
def tweets_emotions_combine(tweets):
    combined_emotions = []
    for each_tweet in tweets:
        tweet_text = each_tweet.text
        clean_tweet = str(tweet_text.encode(errors='ignore').decode('utf-8'))
        one_tweet_emo = fetch_each_tweet_emotion(clean_tweet)
        combined_emotions.append(one_tweet_emo)
    return combined_emotions


# returns a dictionary of the average emotion scores of all tweets about one hashtag:
# {'happy': 0.001115, 'sad': 0.015291, 'angry': 0.002552, 'fear': 0.003962, 'excited': 0.003927, 'indifferent': 0.973152}
def tweets_average_emotions(combined_emotions):
    if len(combined_emotions) > 0:
        average = combined_emotions[0]
        average_keys = average.keys()
        for each_dict in combined_emotions[1:]:
            for average_k in average_keys:
                average[average_k] = (average[average_k] + each_dict[average_k]) / 2
    else:
        average = {'happy': 0, 'sad': 0, 'angry': 0, 'fear': 0, 'excited': 0, 'indifferent': 0}

    return average


# returns a list of average emotions scores for all the recent tweets
def create_plot_one(average_emotions, emotion_labels):
    data = []
    for emotion in emotion_labels:
        data.append(average_emotions[emotion.lower()])
    output_dataset = [{"label": 'probabilities',
                       "data": data,
                       "backgroundColor": ['rgba(255, 206, 86, 0.2)',
                                           'rgba(54, 162, 235, 0.2))',
                                           'rgba(255, 99, 132, 0.2)',
                                           'rgba(105, 0, 132, .2)',
                                           'rgba(255, 159, 64, 0.2)',
                                           'rgba(0, 137, 132, .2)'],
                       "borderColor": ['rgba(255, 206, 86, 1)',
                                       'rgba(54, 162, 235, 1)',
                                       'rgba(255, 99, 132, 1)',
                                       'rgba(200, 99, 132, .7)',
                                       'rgba(255, 159, 64, 1)',
                                       'rgba(0, 10, 130, .7)'],
                       "borderWidth": 1}]
    return output_dataset


def create_plot_two(emo_list): # compose a trend for each tweet + each emotion
    output_list = [{"label": "Happy", "data": [], "backgroundColor": ['rgba(255, 206, 86, 0.2)', ], "borderColor": ['rgba(255, 206, 86, 1)', ], "borderWidth": 2},
                   {"label": "Sad", "data": [], "backgroundColor": ['rgba(54, 162, 235, 0.2)', ], "borderColor": ['rgba(54, 162, 235, 1)', ], "borderWidth": 2},
                   {"label": "Angry", "data": [], "backgroundColor": ['rgba(255, 99, 132, 0.2)', ], "borderColor": ['rgba(255, 99, 132, 1)', ], "borderWidth": 2},
                   {"label": "Fear", "data": [], "backgroundColor": ['rgba(105, 0, 132, .2)', ], "borderColor": ['rgba(200, 99, 132, .7)', ], "borderWidth": 2},
                   {"label": "Excited", "data": [], "backgroundColor": ['rgba(255, 159, 64, 0.2)', ], "borderColor": ['rgba(255, 159, 64, 1)', ], "borderWidth": 2},
                   {"label": "Indifferent", "data": [], "backgroundColor": ['rgba(0, 137, 132, .2)', ], "borderColor": ['rgba(0, 10, 130, .7)', ], "borderWidth": 2}]

    for emo_data in output_list:
        for tweet_info in emo_list:
            emo_data["data"].append(tweet_info[emo_data["label"].lower()])
    return output_list


###############
class MainHandler(webapp2.RequestHandler):
    def genpage(self, tag="#UW"):
        if tag[0] != "#":
            tag = "#" + tag     # make sure its a valid tag
        tweets_data = tweets_search(q=tag)

        combined_emotions_10 = tweets_emotions_combine(tweets_data[0:20])

        output_two = create_plot_two(combined_emotions_10)

        # combined_emotions_all = tweets_emotions_combine(tweets_data)
        emotion_labels = ["Happy", "Sad", "Angry", "Fear", "Excited", "Indifferent"]
        data_one = create_plot_one(tweets_average_emotions(combined_emotions_10), emotion_labels)

        tvals = {'tagname': tag,
                 'emotionLabels': emotion_labels,
                 'dataOne': data_one,
                 'outputTwo': output_two,
                 'outputTwoLength': len(combined_emotions_10)}
        template = JINJA_ENVIRONMENT.get_template('template.html')
        self.response.write(template.render(tvals))

    def get(self):
        self.genpage()

    def post(self):
        tag = self.request.get('tag')
        self.genpage(tag)


application = webapp2.WSGIApplication([('/', MainHandler)], debug=True)
