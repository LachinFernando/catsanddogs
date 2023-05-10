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