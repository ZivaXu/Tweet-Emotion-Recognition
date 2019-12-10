### HCDE310-HW7
### Linda Lai
### The code can be run both locally on dev_appservery.py .
### and Google's servers (at https://hcde310-hw7-linda.appspot.com)
import webapp2, os, urllib2, json, jinja2, logging, urllib

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


### code from hw6
### Utility functions you may want to use
def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

def safeGet(url):
    try:
        return urllib2.urlopen(url)
    except urllib2.URLError as e:
        logging.error("The server couldn't fulfill the request." )
        logging.error("Error code: ", e.code)
    except urllib2.URLError as e:
        logging.error("We failed to reach a server")
        logging.error("Reason: ", e.reason)
    return None

### flickrREST
import flickr_key as flickr_key
def flickrREST(baseurl = 'https://api.flickr.com/services/rest/',
    method = 'flickr.photos.search',
    api_key = flickr_key.key,
    format = 'json',
    params={},
    printurl = False
    ):
    params['method'] = method
    params['api_key'] = api_key
    params['format'] = format
    if format == "json": params["nojsoncallback"]=True
    url = baseurl + "?" + urllib.urlencode(params)
    if printurl:
        logging.info(url)
    return safeGet(url)

## getPhotoIDs() ###
# getPhotoIDs() uses the flickr API to search
# for photos with a given tag, and return a list of photo IDs for the
# corresponding photos. Use a list comprehension to generate the list.
#
# Inputs:
#   tag: a tag to search for
#   n: the number of search results per page (default value should be 100)
#
# Returns: a list of (at most) n photo ids, or None if an error occured

def getPhotoIDs(tags="Seattle",n=100):
    resp = flickrREST(params={"tags":tags,"per_page":n})
    if resp is not None:
        photosdict = json.loads(resp.read())['photos']
        if photosdict is not None:
            if 'photo' in photosdict and len(photosdict['photo']) > 0:
                return [photo['id'] for photo in photosdict['photo']]
    return None

## getPhotoInfo() ##
# getPhotoInfo() uses the flickr API to
# get information about a particular photo id. The information should be
# returned as a dictionary Hint: use flickrREST and the flickr API method
# flickr.photos.getInfo, documented at
# http://www.flickr.com/services/api/flickr.photos.getInfo.html
#
# Inputs:
#   photoID: the id of the photo you to get information about
#
# Returns: a dictionary with photo info, or None if an error occurred

def getPhotoInfo(photoID):
     resp = flickrREST(method="flickr.photos.getInfo",params={"photo_id":photoID})
     if resp is not None:
         return json.load(resp)['photo']
     else:
        return None


## a class called Photo to represent Flickr photos ##
class Photo():
    def __init__(self,pd):
        self.title=pd['title']['_content']
        self.author=pd['owner']['username']
        self.userid = pd['owner']['nsid']
        self.tags = [tag["_content"] for tag in pd['tags']['tag']]
        self.numViews = int(pd['views'])
        self.commentcount = int(pd['comments']['_content'])
        self.url = pd['urls']['url'][0]['_content']
        self.thumbnailURL = self.makePhotoURL(pd)

    def makePhotoURL(self,pd,size="q"):
        ## get a photo url, following documentation at https://www.flickr.com/services/api/misc.urls.html
        url = "https://farm%s.staticflickr.com/%s/%s_%s_%s.jpg"%(pd['farm'],pd['server'],pd['id'],pd['secret'],size)
        return url

    def __str__(self):
        return "~~~ %s ~~~\nauthor: %s\nnumber of tags: %d\nviews: %d\ncomments: %d"%(self.title ,self.author ,len(self.tags),self.numViews,self.commentcount)


###############
class MainHandler(webapp2.RequestHandler):
    def genpage(self, tag="northcascades"):
        photos = [Photo(getPhotoInfo(pid)) for pid in getPhotoIDs(tag)]
        tvals = {'results': {}, 'tag': tag}
        tvals['results']['views'] = sorted(photos, key=lambda x: x.numViews, reverse=True)[:3]

        template = JINJA_ENVIRONMENT.get_template('hw6flickrtemplate-sol.html')
        self.response.write(template.render(tvals))

    def get(self):
        self.genpage()

    def post(self):
        tag = self.request.get('tag')
        self.genpage(tag)

application = webapp2.WSGIApplication([('/', MainHandler)], debug=True)