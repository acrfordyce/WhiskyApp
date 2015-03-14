import requests
import requests.auth
import urllib.parse

from config import OAUTH_PROVIDERS
from flask import url_for, redirect, request, session
from rauth import OAuth1Service, OAuth2Service
from uuid import uuid4


class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = OAUTH_PROVIDERS[provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return url_for('oauth_callback', provider=self.provider_name, _external=True)

    @classmethod
    def get_provider(cls, provider_name):
        if cls.providers is None:
            cls.providers = {}
            for provider_class in cls.__subclasses__():
                provider = provider_class()
                cls.providers[provider.provider_name] = provider
        return cls.providers[provider_name]


class FacebookSignIn(OAuthSignIn):
    def __init__(self):
        super(FacebookSignIn, self).__init__('facebook')
        self.service = OAuth2Service(
            name='facebook',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://graph.facebook.com/oauth/authorize',
            access_token_url='https://graph.facebook.com/oauth/access_token',
            base_url='https://graph.facebook.com'
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        if 'code' not in request.args:
            return None, None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()}
        )
        me = oauth_session.get('me').json()
        return (
            'facebook$' + me['id'],
            me.get('email').split('@')[0],  # facebook does not provide username
            me.get('email'),
            None  # facebook does not provide profile picture URI on login
        )


class TwitterSignIn(OAuthSignIn):
    def __init__(self):
        super(TwitterSignIn, self).__init__('twitter')
        self.service = OAuth1Service(
            name='twitter',
            consumer_key=self.consumer_id,
            consumer_secret=self.consumer_secret,
            request_token_url='https://api.twitter.com/oauth/request_token',
            authorize_url='https://api.twitter.com/oauth/authorize',
            access_token_url='https://api.twitter.com/oauth/access_token',
            base_url='https://api.twitter.com/1.1/'
        )

    def authorize(self):
        request_token = self.service.get_request_token(
            params={'oauth_callback': self.get_callback_url()}
        )
        session['request_token'] = request_token
        return redirect(self.service.get_authorize_url(request_token[0]))

    def callback(self):
        request_token = session.pop('request_token')
        if 'oauth_verifier' not in request.args:
            return None, None, None, None
        oauth_session = self.service.get_auth_session(
            request_token[0],
            request_token[1],
            data={'oauth_verifier': request.args['oauth_verifier']}
        )
        me = oauth_session.get('account/verify_credentials.json').json()
        social_id = 'twitter$' + str(me.get('id'))
        username = me.get('screen_name')
        picture_uri = me.get('profile_image_url')
        print(picture_uri)
        return social_id, username, None, picture_uri  # Twitter does not provide email


class GoogleSignIn(OAuthSignIn):
    def __init__(self):
        super(GoogleSignIn, self).__init__('google')
        self.service = OAuth2Service(
            name='google',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://accounts.google.com/o/oauth2/auth',
            access_token_url='https://accounts.google.com/o/oauth2/token',
            base_url='https://accounts.google.com/'
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        if 'code' not in request.args:
            return None, None, None, None
        raw_oauth_session = self.service.get_raw_access_token(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()}
        )
        raw = raw_oauth_session.json()
        self.oauth_session = self.service.get_session(raw['access_token'])
        u = self.oauth_session.get('https://www.googleapis.com/oauth2/v1/userinfo').json()
        return(
            'google$' + u.get('id'),
            u.get('email').split('@')[0],
            u.get('email'),
            u.get('picture')
        )


class RedditSignIn(OAuthSignIn):
    def __init__(self):
        super(RedditSignIn, self).__init__('reddit')
        self.service = OAuth2Service(
            name='reddit',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://ssl.reddit.com/api/v1/authorize',
            access_token_url='https://ssl.reddit.com/api/v1/access_token',
            base_url='https://ssl.reddit.com/',
        )


    def authorize(self):
        state = str(uuid4())
        params = {
            "client_id": self.consumer_id,
            "response_type": "code",
            "state": state,
            "redirect_uri": self.get_callback_url(),
            "duration": "temporary",
            "scope": "identity"
        }
        url = "https://ssl.reddit.com/api/v1/authorize?" + urllib.parse.urlencode(params)
        return redirect(url)

    def callback(self):
        if 'code' not in request.args:
            return None, None, None, None
        code = request.args.get('code')
        print('code:')
        print(code)
        client_auth = requests.auth.HTTPBasicAuth(self.consumer_id, self.consumer_secret)
        post_data = {"grant_type": "authorization_code",
                     "code": code,
                     "redirect_uri": self.get_callback_url()}
        headers = {"User-Agent": "/u/_TiNe_"}
        response = requests.post("https://ssl.reddit.com/api/v1/access_token",
                                 auth=client_auth,
                                 headers=headers,
                                 data=post_data)
        token_json = response.json()
        print('token_json:')
        print(token_json)
        access_token = token_json.get("access_token")
        headers.update({"Authorization": "bearer " + access_token})
        response = requests.get("https://oauth.reddit.com/api/v1/me", headers=headers)
        me_json = response.json()
        return(
            "reddit$" + me_json.get("name"),
            me_json.get("name"),
            None,
            url_for('.static', filename='reddit_snoo.png')
        )


