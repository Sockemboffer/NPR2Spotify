class ResponseHandle:

    def HandleRespone(self, response):
        # check for valid response status
        if response.status_code != 200 or response.status_code != 201:
            print(response)
        else:
            print(response)
            raise ResponseException(response.status_code)