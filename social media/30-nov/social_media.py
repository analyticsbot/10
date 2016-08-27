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

def generateText(N_gainers, N_losers, df_diff, _type_post):
    """Function to generate relevant text
    Required params: N_gainers, N_losers, df_diff, _type_post
    """
    text_gainers = 'Crowdkast\'s top(' + str(N_gainers)+ ') ' + _type_post + ' percentage gainers -'
    text_losers = 'Crowdkast\'s top(' + str(N_losers)+ ') ' + _type_post + ' percentage losers -'

    max_row = df_diff.shape[0]
    count_gainers = 0
    count_losers = 0
    for i in range(N_gainers):
        try:
            text_gainers += ' $' + df_diff.loc[i, 'ticker'].lower() + ' ' + str(df_diff.loc[i, 'percent-change'])+ '%,'
            count_gainers +=1
        except:
            text_gainers += ''

    for i in range(N_losers):
        try:
            text_losers += ' $' + df_diff.loc[max_row - i -1, 'ticker'].lower() + ' ' +  str(df_diff.loc[max_row - i -1, 'percent-change'])+ '%,'
            count_losers +=1
        except:
            text_losers += ''

    return text_gainers[:-1].replace('(5)','('+str(count_gainers)+')'), text_losers[:-1].replace('(5)','('+str(count_losers)+')')
    
