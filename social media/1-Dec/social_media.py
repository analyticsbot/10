from twython import Twython
import facebook

class FacebookPost:

    def __init__(self, page_id, access_token):
        self.page_id = page_id
        self.access_token = access_token
        
    ## function to post a message to a facebook page
    def postToFacebook(self, message):
        self.message = message
        """Function to post to Facebook
        page_id: page id of the facebook page
        access_token: access token of the page"""
        cnfig = {
        "page_id"      : self.page_id,
        "access_token" : self.access_token   
        }
        api = self.get_api_fb(cnfig)
        status = api.put_wall_post(self.message)

    def get_api_fb(self, cnfig):
      graph = facebook.GraphAPI(cnfig['access_token'])
      resp = graph.get_object('me/accounts')
      page_access_token = None
      for page in resp['data']:
        if page['id'] == cnfig['page_id']:
          page_access_token = page['access_token']
      graph = facebook.GraphAPI(page_access_token)
      return graph

class TwitterPost:

    def __init__(self, APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET):
        self.APP_KEY = APP_KEY
        self.APP_SECRET = APP_SECRET
        self.OAUTH_TOKEN = OAUTH_TOKEN
        self.OAUTH_TOKEN_SECRET = OAUTH_TOKEN_SECRET
        self.twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
        
    ## function to post a message to twitter
    def postToTwitter(self, status):
        self.status = status
        """Function to post to facebook
        Required params: APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET
        """        
        self.twitter.update_status(status=self.status)

    
