import json

from AiService import aiservice_utils as ais_utils
from Utils import request_utils as req_utils
from SES import ses_utils
from Utils import response_utils as rutils

def notify_coordinators(event):

    if isinstance(event['body'], str):
        params = json.loads(event['body'])
    else:
        params = event['body']

    payment_event = req_utils.get_params(params, 'event')

    statement = "select * from payments.transactions where event_id =\"" +payment_event+"\""
    transaction_records = ais_utils.execute_db_query('transactions', statement)
   
    response = {"sent": "Student registration to this class already started."}
    if len(transaction_records) == 1:
        is_email_send = ses_utils.notify_coordinators(payment_event)
        response = {"sent": is_email_send}
        if is_email_send:
            return rutils.success_response(response)
        message = "Email not send to the coordinators."
        print(message)
        error = {
            "errorCode": None,
            "message": message,
            "suggestions": None,
        }
        return rutils.failure_response(error)
    
    return rutils.success_response(response)


def process_post_request(event: dict) -> bool:
    params = event["body"]
    first_name = req_utils.get_params(params, "firstName")
    last_name = req_utils.get_params(params, "lastName")
    email = req_utils.get_params(params, "email")
    tx_id = req_utils.get_params(params, "txId")
    amount = req_utils.get_params(params, "amount")
    event = req_utils.get_params(params, "event")
    discount = req_utils.get_params(params, "discount")
    class_date = req_utils.get_params(params, "classDate")

    if event == "one-to-one-class" and amount > 0:
        try:
            result = ses_utils.send_one_to_one_payment_email(
                first_name, last_name, email, tx_id, amount, discount
            )
            response = {"sent": result}
            return rutils.success_response(response)

        except Exception as error:
            message = f"Error occured while sending one on one payment email err: {str(error)}"
            ais_utils.add_log_record(
                email,
                event,
                "Payments",
                None,
                "ERROR",
                message,
                sub_stage="One on one payment",
            )
            print(message)
            error = {"errorCode": None, "message": message, "suggestions": None}
            return rutils.failure_response([error])

    elif event == "one-to-one-cancel" and amount > 0 and class_date:
        try:
            result = ses_utils.send_one_to_one_cancellation_payment_email(
                first_name, last_name, email, tx_id, amount, class_date
            )
            response = {"sent": result}
            return rutils.success_response(response)

        except Exception as error:
            message = f"Error occured while sending one on one cancellation payment email err: {str(error)}"
            ais_utils.add_log_record(
                email,
                event,
                "Payments",
                None,
                "ERROR",
                message,
                sub_stage="One on one payment",
            )
            print(message)
            error = {"errorCode": None, "message": message, "suggestions": None}
            return rutils.failure_response([error])
        

def lambda_handler(event, context):
    """Handle the request from the API gateway

    Arguments:
        event {Dict} -- Dictionary containing the input to the REST requests
        context {Dict} -- Context object associated with the call

    Returns:
        Dict -- Response to the REST API request
    """
    req_utils.prepare_process_event(event, context, 'AiClub Registration', None)
    path = event['path']
    print('Path: {}'.format(event['path']))
    print('Method: {}'.format(event['httpMethod']))

    try:
        if path == '/checkouts/notify-coordinators':
            if event['httpMethod'] == 'POST':
                response = notify_coordinators(event)
        elif path =='/checkouts/send-email':
            if event['httpMethod'] == 'POST':
                response = process_post_request(event)
                print("Response", response)

        else:
            print('Unsupported Method: {} or unsupported path {}'.format(event['httpMethod']), path)
    except Exception as e:
        return rutils.unsupported_method(event, context, e)

    return rutils.success_method(context, response)