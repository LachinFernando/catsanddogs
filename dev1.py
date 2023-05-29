class OtterAI:
    API_BASE_URL = 'https://otter.ai/forward/api/v1/'
    S3_BASE_URL = 'https://s3.us-west-2.amazonaws.com/'

    def __init__(self):
        self._session = requests.Session()
        self._userid = None
        self._cookies = None

    def _is_userid_invalid(self):
        if not self._userid:
            return True
        return False

    def _handle_response(self, response):
        try:
            return {'status': response.status_code, 'data': response.json()}
        except ValueError:
            return {'status': response.status_code, 'data': {}}

    def _get_speech(self, speech_id):
        # API URL
        speech_url = OtterAI.API_BASE_URL + 'speech'
        if self._is_userid_invalid():
            raise OtterAIException('userid is invalid')
        # Query Params
        payload = {'userid': self._userid, 'otid': speech_id}
        # GET
        response = self._session.get(speech_url, params=payload)

        return self._handle_response(response)
    
def addition(num1, num2):
    return num1 + num2

def substraction(num1, num2):
    return num1 - num2

def multi(num1, num2):
    return num1 * num2

def divider(num1, num2):
    return num1/num2

def print_strings(args):
    for word in args:
        print(word)
xbbxbxb