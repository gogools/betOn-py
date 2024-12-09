import facebook

class FacebookSentiments:

    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.graph = facebook.GraphAPI(access_token=app_id + "|" + app_secret)
