import json
import requests
from .exceptions import AuthenticationFailed, BadRequest, DoesNotExist
from .resource import DRESTResource


class DRESTClient(object):
    """DREST Python client.

    Exposes a DREST API to Python using a Django-esque interface.
    Resources are available on the client through access-by-name.

    Arguments:
        host: hostname to a DREST API
        version: version (defaults to no version)
        client: HTTP client (defaults to requests.session)
        scheme: defaults to https
        authentication: if unset, authentication is disabled.
            If set, provides a dictionary of credentials: {
                usename: login username,
                password: login password,
                login_endpoint: username/password login endpoint
                    defaults to '/accounts/login/'

                token: authorization token value
                token_type: token type
                    defaults to 'JWT'

                cookie: session cookie value
                cookie_name: session cookie name
                    defaults to 'sessionid'
            }
            Either username/password, token, or cookie should be provided.
        mocks: if set, provides mocks for specific methods and resources.
            For example, the mock:
            {
                'users': [{
                    'id': 1,
                    'name': 'Joe Smith'
                }, {
                    'id': 2,
                    'name': 'John Smith'
                }]
            }
            Would cause the client to short-circuit the API backend whenever
            "users" are requested, returning only the two users specified.

    Examples:

    Assume there is a DREST resource at "https://my.api.io/v0/users",
    and that we can access this resource with an auth token "secret".

    Getting a client:

        client = DRESTClient(
            'my.api.io',
            version='v0',
            authentication={'token': 'secret'}
        )

    Getting a single record of the Users resource

        client.Users.get('123')

    Getting all records (automatic pagination):

        client.Users.all()

    Filtering records:

        client.Users.filter(name__icontains='john')
        other_users = client.Users.exclude(name__icontains='john')

    Ordering records:

        users = client.Users.sort('-name')

    Including / excluding fields:

        users = client.Users.all()
        .excluding('birthday')
        .including('events.*')
        .get('123')

    Mapping by field:

        users_by_id = client.Users.map()
        users_by_name = client.Users.map('name')

    Updating records:

        user = client.Users.first()
        user.name = 'john'
        user.save()

    Creating records:

        user = client.Users.create(name='john')
    """
    def __init__(
        self,
        host,
        version=None,
        client=None,
        scheme='https',
        authentication=None,
        mocks=None
    ):
        self._host = host
        self._version = version
        self._client = client or requests.session()
        self._client.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self._resources = {}
        self._mocks = mocks or {}
        self._scheme = scheme
        self._authenticated = True
        authentication = authentication or {}
        self._authentication = authentication
        # authentication defaults
        self._token_type = authentication.get(
            'token_type', 'JWT'
        )
        self._cookie_name = authentication.get(
            'cookie_name', 'sessionid'
        )
        self._login_endpoint = authentication.get(
            'login_endpoint', '/accounts/login/'
        )

        if authentication:
            self._authenticated = False
            token = authentication.get('token')
            cookie = authentication.get('cookie')
            if token:
                self._use_token(token)
            if cookie:
                self._use_cookie(cookie)

    @property
    def mocks(self):
        return self._mocks

    def __repr__(self):
        return '%s%s' % (
            self._host,
            '/%s/' % self._version if self._version else ''
        )

    def _use_token(self, value):
        self._token = value
        self._authenticated = bool(value)
        self._client.headers.update({
            'Authorization': '%s %s' % (
                self._token_type, self._token if value else ''
            )
        })

    def _use_cookie(self, value):
        self._cookie = value
        self._authenticated = bool(value)
        self._client.headers.update({
            'Cookie': '%s=%s' % (self._cookie_name, value)
        })

    def __getattr__(self, key):
        key = key.lower()
        return self._resources.get(key, DRESTResource(self, key))

    def _login(self, raise_exception=True):
        username = self._authentication.get('username')
        password = self._authentication.get('password')
        if not username or not password:
            if raise_exception:
                raise AuthenticationFailed('No username or password provided')
            else:
                return

        response = requests.post(
            self._build_url(self._login_endpoint),
            data={
                'login': username,
                'password': password
            },
            allow_redirects=False
        )
        if raise_exception:
            response.raise_for_status()

        self._use_cookie(response.cookies.get(self._cookie_name))

    def _authenticate(self, raise_exception=True):
        response = None
        if not self._authenticated:
            self._login(raise_exception)
        if raise_exception and not self._authenticated:
            raise AuthenticationFailed(
                response.text if response else 'Unknown error'
            )
        return self._authenticated

    def _build_url(self, url, prefix=None):
        if not url.startswith('/'):
            url = '/%s' % url

        if prefix:
            if not prefix.startswith('/'):
                prefix = '/%s' % prefix

            url = '%s%s' % (prefix, url)
        return '%s://%s%s' % (self._scheme, self._host, url)

    def request(self, method, url, params=None, data=None):
        self._authenticate()
        response = self._client.request(
            method,
            self._build_url(url, prefix=self._version),
            params=params,
            data=data
        )

        if response.status_code == 401:
            raise AuthenticationFailed()

        if response.status_code == 404:
            raise DoesNotExist()

        if response.status_code >= 400:
            raise BadRequest()

        return json.loads(response.content.decode('utf-8'))
