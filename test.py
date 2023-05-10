#This is to test git
MAX_CHARACTERS_ALLOWED = 30000 
MAX_LINES_PROCESSED = 200
MINIMUM_CHARACTERS = 200
MIN_LENGTH = 10


def record_summary_result(summary_id:str, status: str, summary: str, homework: str):
    function_name = req_utils.get_fn_prefix() + "sessionSummary"
    query_params = {"summaryId": summary_id}
    body = {"status": status, "summary": summary, "homework": homework}

    response = lutils.invoke_lambda(
        function_name,
        body=body,
        query_string_params=query_params,
        invocation_type="RequestResponse",
        http_method="PATCH",
    )

    return response


def remove_lines_from_conversation(list_of_lines: list, cutoff: int) -> list:
    list_of_lines_kept = []
    cutoff = max(25, cutoff)
    # Remove lines to bring the total down. 
    # Do not remove sentences with the word homework. 
    for line in list_of_lines:
        line = line.lower()
        if len(line) > cutoff or 'homework' in line:
            list_of_lines_kept.append(line)
    return list_of_lines_kept


def get_video_id_from_url(url):
    url_chunks = urlparse(url)
    if not url_chunks.query:
        video_id = url_chunks.path.split("/")[-1]
        return video_id
    
    video_id= url_chunks.query
    return video_id.split("=")[-1]
from requests_toolbelt.multipart.encoder import MultipartEncoder
import xml.etree.ElementTree as ET
import requests
import json
import time

class OtterAIException(Exception):
    pass

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


    def login(self, username, password):
        # API URL
        auth_url = OtterAI.API_BASE_URL + 'login'
        # Query Parameters
        payload = {'username': username}
        # Basic Authentication
        self._session.auth = (username, password)
        # GET
        response = self._session.get(auth_url, params=payload)
        # Check
        if response.status_code != requests.codes.ok:
            return self._handle_response(response)
        # Set userid & cookies
        self._userid = response.json()['userid']
        self._cookies = response.cookies.get_dict()

        return self._handle_response(response)


    def upload_speech_get_transcript(self, file_name, content_type='audio/wav'):
        # API URL
        speech_upload_params_url = OtterAI.API_BASE_URL + 'speech_upload_params'
        speech_upload_prod_url = OtterAI.S3_BASE_URL + 'speech-upload-prod'
        finish_speech_upload = OtterAI.API_BASE_URL + 'finish_speech_upload'

        if self._is_userid_invalid():
            raise OtterAIException('userid is invalid')

        # First grab upload params (aws data)
        payload = {'userid': self._userid}
        response = self._session.get(speech_upload_params_url, params=payload)

        if response.status_code != requests.codes.ok:
            return self._handle_response(response)

        response_json = response.json()
        params_data = response_json['data']

        # Send options (precondition) request
        prep_req = requests.Request('OPTIONS', speech_upload_prod_url).prepare()
        prep_req.headers['Accept'] = '*/*'
        prep_req.headers['Connection'] = 'keep-alive'
        prep_req.headers['Origin'] = 'https://otter.ai'
        prep_req.headers['Referer'] = 'https://otter.ai/'
        prep_req.headers['Access-Control-Request-Method'] = 'POST'
        # POST
        response = self._session.send(prep_req)

        if response.status_code != requests.codes.ok:
            return self._handle_response(response)
        
        # Post file to bucket
        fields = {}
        params_data['success_action_status'] = str(params_data['success_action_status'])
        del params_data['form_action']
        fields.update(params_data)
        fields['file'] = (file_name, open(file_name, mode='rb'), content_type)
        multipart_data = MultipartEncoder(fields=fields)
        # POST
        response = requests.post(speech_upload_prod_url, data=multipart_data,
            headers={'Content-Type': multipart_data.content_type})

        if response.status_code != 201:
            return self._handle_response(response)

        # Pase xml response
        xmltree = ET.ElementTree(ET.fromstring(response.text))
        xmlroot = xmltree.getroot()
        location = xmlroot[0].text
        bucket = xmlroot[1].text
        key = xmlroot[2].text

        # Call finish api
        payload = {'bucket': bucket, 'key': key, 'language': 'en', 'country': 'us', 'userid': self._userid}
        response = self._session.get(finish_speech_upload, params=payload)

        response = self._handle_response(response)

        #get the ot id from the response
        ot_id = response['data']['otid']

        #when the audio is uploaded, it will start preprocessing
        #first send the request to check the preprocessing status
        speech_response = self._get_speech(ot_id)
        preprocessing_status = speech_response['data']['speech']['process_finished']
        print("preprocessing status: {}".format(preprocessing_status))

        #loop until status comes true indicates preprocessing has finished
        #sleep for 5 seconds to avoid the high request rate
        while not preprocessing_status:
            time.sleep(5)
            speech_get_response = self._get_speech(ot_id)
            preprocessing_status = speech_get_response['data']['speech']['process_finished']
            print("preprocessing status: {}".format(preprocessing_status))

        full_transcripts = " ".join([script['transcript'] for script in speech_get_response['data']['speech']['transcripts']])

        return full_transcripts