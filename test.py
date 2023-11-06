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

def process_get_request(event: dict) -> dict:

    params = event['queryStringParameters']
    summary_id = req_utils.get_params(params, 'summaryId')
    youtube_link = req_utils.get_params(params, 'youtubeLink')
    extract_type = req_utils.get_params(params, 'extractType')
    session_id = req_utils.get_params(params, 'sessionId')
    previous_session_summaries = req_utils.get_params(
        params, "previousSessionSummaries"
    )
    video_id = get_video_id_from_url(youtube_link)
    print("Video ID", video_id)

    # get the processed transcript from the youtube videeo
    try:
        full_converation, ten_min_conversation = process_youtube_script(video_id)
        print("characters in full conversation: ", len(full_converation))
    except TranscriptsDisabled as error:
        message = f"Transcripts disabled: {error}"
        print(message)
        record_summary_result(summary_id, "failure", summary=message, homework="")
        return None
    except Exception as error:
        message = f"Unable to get the content from the youtube video err: {error}"
        print(message)
        record_summary_result(summary_id, "failure", summary=message, homework="")
        return None

    # first try to get the summary assuming tokens are not exceeding the limit
    try:
        summary, homework = get_summary(full_converation, ten_min_conversation)
        print("final summary: ", summary)
        print("homework: ", homework)
        record_summary_result(summary_id, "success", summary, homework)
        if extract_type == "auto":
            previous_session_summaries.append(summary)
            record_summary_to_project_session(session_id, previous_session_summaries)
            record_homework(homework, session_id)
    except Exception as error:
        print("Error message for the first summary attempt: {}".format(error))
        # it may fail due to large number of tokens
        # try again to get the summary by taking chunks
        try:
            split_ratio = int(np.ceil(len(full_converation) / MAX_CHARACTERS_ALLOWED))
            print("split ratio", split_ratio)
            summary, homework = get_summary(
                full_converation, ten_min_conversation, split_ratio
            )
            print("final summary: ", summary)
            print("homework: ", homework)
            record_summary_result(summary_id, "success", summary, homework)
            if extract_type == "auto":
                previous_session_summaries.append(summary)
                record_summary_to_project_session(session_id, previous_session_summaries)
                record_homework(homework, session_id)
        except Exception as error:
            message = f"Unable to get the summary for the transcript err: {str(error)}"
            print(message)
            record_summary_result(summary_id, "failure", "", "")