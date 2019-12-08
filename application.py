import urllib.parse, urllib.request, urllib.error, json
from ibm_watson import ToneAnalyzerV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import ApiException

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

# get the top news articles from the New York Times in a given section
nyt_api = "CfYgzlqXRUO4GId2thWu9hB2H88bKUtk"

def nyt(section, baseurl='https://api.nytimes.com/svc/topstories/v2/'):
	url = baseurl + section + ".json?api-key=" + nyt_api
	try:
		return urllib.request.urlopen(url)
	except urllib.error.URLError as e:
		if hasattr(e,"code"):
			print("The server couldn't fulfill the request.")
			print("Error code: ", e.code)
		elif hasattr(e,'reason'):
			print("We failed to reach a server")
			print("Reason: ", e.reason)
		return None

# analyze the tone of the given text
watson_api = 'bw2x1nRlZqljWVgB7oPistFTRzsM1Evwh18R9jE8DebZ'

def tone_analyzer(tone_input, url="https://gateway.watsonplatform.net/tone-analyzer/api", content_type="application/json", sentences=False):
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

# extract the title and abstract of the top 10 news articles in the given section at NY Times
# analyze the title and abstract for each article, output interpreted tones and their strength
def analyze_nyt(section):
	print("----------- Headline Tone Analysis for %s Section -----------" % section.capitalize())
	nytresult = nyt(section).read()
	for article in json.loads(nytresult)["results"][0:10]:
		print(article["title"] + "\n" + "/" + article["abstract"] + "/")
		analyzed_text_tones = tone_analyzer(article["title"] + "\n" + article["abstract"])["document_tone"]["tones"]
		if analyzed_text_tones:
			for tone in analyzed_text_tones:
				print("<Tone> %s | <Strength> %d %%" % (tone["tone_name"], int(tone["score"] * 100)))
		else:
			print("No tone detected :(")
		print("------------------------------------------------------------")


section_list = ["opinion", "business", "fashion", "theater", "technology", "politics"]
for section in section_list:
	analyze_nyt(section)