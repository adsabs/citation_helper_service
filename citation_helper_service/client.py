from flask import current_app
from flask import request


class Client:
    """
    The Client class is a thin wrapper around adsmutils ADSFlask client; Use it as a centralized
    place to set application specific parameters, such as the oauth2
    authorization header
    """
    def __init__(self):
        """
        Constructor
        :param client_config: configuration dictionary of the client
        """

        self.client = current_app.client # Use HTTP pool provided by adsmutils ADSFlask
    
    def get(self, *args, **kwargs):
        
        headers = {'Authorization':
               request.headers.get('X-Forwarded-Authorization', request.headers.get('Authorization', ''))}
        if 'headers' in kwargs:
            kwargs['headers'].update(headers)
        else:
            kwargs['headers'] = headers
        
        return self.client.get(*args, **kwargs)
