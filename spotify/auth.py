import base64
import os
import requests
import time

TOKEN_URL = 'https://accounts.spotify.com/api/token'

class ClientCredential(object):

    def __init__(self, client_key=None, client_secret=None, client_token = None):
        self.client_key = client_key
        self.client_secret = client_secret
        self.client_token = client_token
    
    def prepare_authorization_headers(self, client_key, client_secret):
        header = base64.b64encode((self.client_key+":"+self.client_secret).encode("ascii"))

        return {
                'Authorization': 'Basic %s' % header.decode("ascii"),
                'Content-Type' : 'application/x-www-form-urlencoded'
            }

    def is_token_expired(self, token_expires_at):
        return is_token_expired(token_expires_at)

    def request_client_token(self, client_key, client_secret):
        headers = self.prepare_authorization_headers(self.client_key, self.client_secret)

        body_params = {
            'grant_type': "client_credentials"
        }
        try:
            res = requests.post(TOKEN_URL, headers=headers, data=body_params)
        except Exception as error:
            print(error)
        
        res.raise_for_status()
        token_info = res.json()
        
        token_info['token_expires_at'] = int(time.time()) + token_info['expires_in']
        return res.json()
    
    def get_client_token(self):
        if self.client_token and not self.is_token_expired(self.client_token['access_token']):
            return self.client_token['access_token']
        self.client_token = self.request_client_token(self.client_key, self.client_secret)
        return self.client_token['access_token']

    def set_client_key(self, client_key):
        self.client_key = client_key
    
    def set_client_secret(self, client_secret):
        self.client_secret = client_secret

    def set_client_credentials(self, client_key, client_secret):
        self.client_key = client_key
        self.client_secret = client_secret

def is_token_expired(token_expires_at):
    return token_expires_at - int(time.time()) < 30
    

class SpotifyCodeFlowOAth(object):
    
    AUTHORIZE_URL = 'https://accounts.spotify.com/authorize'

    def __init__(self, client_key, client_secret, redirect_url):
        self.client_key = client_key
        self.client_secret =  client_secret
        self.redirect_url = redirect_url
        
    
