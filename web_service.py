'''
Created on Feb 19, 2013

@author: yaocheng
'''

from urllib import urlopen, urlencode

class WebService(object):
    
    def __init__(self, server, scheme='http'):
        self._scheme = scheme
        self._server = server
        self._resource = ''
        self._params = {}
        self._request_url = None
        
    @property
    def resource(self):
        return self._resource
        
    @resource.setter
    def resource(self, val=''):
        self._resource = val
        
    @property
    def params(self):
        return self._params
        
    @params.setter
    def params(self, val={}, **kwargs):
        self.params = val
        if kwargs:
            self._params = self._params.update(kwargs)
            
    def _construct_url(self, resource=None, **kwargs):
        """
        CAUTION! If the kwargs or the self._params contains unicode character (usually in value)
        which can not be encoded in ascii (remeber, before "encode", there is an implicit process
        of "decode" to identify which character (coding point) it is), urlencode() will fail because
        it will try to encode the character with ascii by calling str(). 
        Encode the problematic value with utf-8, then a string representation (or I guess it can be
        called "ascii representation") of the "code" will return, which urlencode() won't complain 
        about. And in order for this to work, I think the server side must be aware of this "ascii 
        representation" of the unicode character and will proceed accordingly.
        """
        try:
            url_dict = {'scheme': self._scheme, 'server': self._server,
                        'resource': resource if resource else self._resource,
                        'params': urlencode(kwargs) if kwargs!={} else urlencode(self._params)}
        except UnicodeEncodeError:
            kwargs = dict([(k, v.encode('utf-8')) for k, v in kwargs.items() if isinstance(v, unicode)])
            self._params = dict([(k, v.encode('utf-8')) for k, v in self._params.items() if isinstance(v, unicode)])
            url_dict = {'scheme': self._scheme, 'server': self._server,
                        'resource': resource if resource else self._resource,
                        'params': urlencode(kwargs) if kwargs!={} else urlencode(self._params)}
        self._request_url = '%(scheme)s://%(server)s/%(resource)s?%(params)s' % url_dict
    
    def _sent_request(self):
        try:
            response = urlopen(self._request_url)
            return response
        except IOError:
            print 'URL request IOError!'
            
    @staticmethod
    def _parametric_url_request(func):
        def decorated(self, resource=None, **kwargs):
            self._construct_url(resource, **kwargs)
            func(self)
            res = self._sent_request()
            if res:
                return res
        return decorated
    
    @staticmethod
    def _default_url_request(func):
        def decorated(self):
            self._construct_url()
            func(self)
            res = self._sent_request()
            if res:
                return res
        return decorated
    
    
class GeoNames(WebService):
    
    def __init__(self, server, username=None):
        super(GeoNames, self).__init__(server)
        self._username = username
        
    @property
    def username(self):
        return self._username
        
    @username.setter
    def username(self, val):
        self._username = val
        
    @WebService._parametric_url_request
    def request(self, resource=None, **kwargs):
        if self._username and 'username=' not in self._request_url:
            self._request_url += '&' + urlencode({'username': self._username})
            
    @WebService._default_url_request
    def send(self):
        if self._username and 'username=' not in self._request_url:
            self._request_url += '&' + urlencode({'username': self._username})
    
    
class WeatherBug(WebService):
    
    def __init__(self, server, api_key=None):
        super(WeatherBug, self).__init__(server)
        self._api_key = api_key
        
    @property
    def api_key(self):
        return self._api_key
        
    @api_key.setter
    def api_key(self, val):
        self._api_key = val
        
    @WebService._parametric_url_request
    def request(self, resource=None, **kwargs):
        if self._api_key and 'api_key=' not in self._request_url:
            self._request_url += '&' + urlencode({'api_key': self._api_key})
            
    @WebService._default_url_request
    def send(self):
        if self._api_key and 'api_key=' not in self._request_url:
            self._request_url += '&' + urlencode({'api_key': self._api_key})


if __name__ == '__main__':
    pass