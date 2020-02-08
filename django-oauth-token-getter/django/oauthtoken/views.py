from django.http import HttpResponse, HttpResponseRedirect
from requests_oauthlib import OAuth2Session
import os

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
redirect_uri = os.getenv('REDIRECT_URI')
scope = ['user:email']
authorize_url = 'https://github.com/login/oauth/authorize'
token_url = 'https://github.com/login/oauth/access_token'

def login(request):
    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)
    authorization_url, state = oauth.authorization_url(authorize_url)
    request.session["oauth_state"] = state
    return HttpResponseRedirect(authorization_url)

def callback(request):
    oauth = OAuth2Session(client_id, state=request.session["oauth_state"])
    token = oauth.fetch_token(token_url, client_secret=client_secret, authorization_response=request.get_full_path())
    access_token = token.get("access_token", "")
    refresh_token = token.get("refresh_token", "")
    resp = """<!DOCTYPE html><html lang="ja">
    <head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"></head>
    <body>
    <h4>access_token</h4>
    <div>{}</div>
    <h4>refresh_token</h4>
    <div>{}</div>
    <a href="/">top</a>
    </body>
    </html>""".format(access_token, refresh_token)
    return HttpResponse(resp)

def top(request):
    resp = """<!DOCTYPE html><html lang="ja">
    <head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"></head>
    <body><a href="/login">login</a></body>
    </html>
    """
    return HttpResponse(resp)
