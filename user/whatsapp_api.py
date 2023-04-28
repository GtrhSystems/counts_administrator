import requests
from django.conf import settings

def send_message(phone, message):

    url = "https://api.ultramsg.com/"+settings.INSTANCE_WHATSAPP_API+"/messages/chat"

    payload = "token="+settings.TOKEN_WHATSAPP_API+"&to="+ phone + "&body="+ message
    payload = payload.encode('utf8').decode('iso-8859-1')
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.request("POST", url, data=payload, headers=headers)
    return response.text