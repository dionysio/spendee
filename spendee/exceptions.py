from requests.exceptions import RequestException


class SpendeeError(RequestException):
    def __init__(self, message, response=None):
        self.message = message
        self.response = response
        super(SpendeeError, self).__init__()

    def __str__(self):
        return self.message
