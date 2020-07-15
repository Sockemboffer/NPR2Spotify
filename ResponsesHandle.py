class ResponseException(Exception):
    def __init__(self, status_code, message=""):
        self.message = message
        self.status_code = status_code

    def __str__(self):
        # check for valid response status
        if response.status_code != 200 or response.status_code != 201:
            return self.message + f"Response gave status code {self.status_code}"