import webapp2, os, urllib2, json, jinja2, logging
from ibm_watson import ToneAnalyzerV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import ApiException

import plotly
import plotly.graph_objs as go
import pandas as pd
import numpy as np

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
                                       extensions=['jinja2.ext.autoescape'],
                                       autoescape=True)


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


# analyze the tone of the given text
watson_api = 'bw2x1nRlZqljWVgB7oPistFTRzsM1Evwh18R9jE8DebZ'


def tone_analyzer(tone_input, url="https://gateway.watsonplatform.net/tone-analyzer/api",
                  content_type="application/json", sentences=False):
    authenticator = IAMAuthenticator(watson_api)
    tone_analyzer = ToneAnalyzerV3(version='2017-09-21', authenticator=authenticator)
    tone_analyzer.set_service_url(url)
    text = tone_input
    try:
        return tone_analyzer.tone({'text': text}, content_type=content_type, sentences=sentences).get_result()
    except ApiException as ex:
        if hasattr(ex, "code"):
            print("The server couldn't fulfill the request.")
            print("Error code: ", ex.code)
        elif hasattr(ex, 'reason'):
            print("We failed to reach a server")
            print("Reason: ", ex.message)
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


def create_plot_two():



class MainHandler(webapp2.RequestHandler):
    def genpage(self, tag="northcascades"):
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
