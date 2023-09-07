import requests
from django.conf import settings


url = "https://api.ultramsg.com/"+settings.INSTANCE_WHATSAPP_API+"/messages/chat"


def message_sale(data):
    message =  f"Hola, tu servicio {data['platform']} está activo, \n" \
                f"👤USUARIO:  {data['email']}   \n" \
                f"🔐CONTRASEÑA: {data['password']} \n" \
                f"📺: PERFIL {data['profile']}  \n" \
                f"🔒 PIN: {data['pin']} \n" \
                f"📅 Fecha de corte: {data['date_limit']} \n" \
                f"Condiciones del servicio:  \n" \
                f"1.-No modifique ninguna información de la cuenta \n" \
                f"2.-No puede estar en 2 o más dispositivos simultáneamente  \n" \
                f"3.-No agregue ni elimine ningún perfil \n" \
                f"4.-Este es un producto digital. Después de la compra, no se puede  \n" \
                f"hacer ningún reembolso. Solo garantía de reemplazo. \n" \
                f"Nota: Si viola algunas de estas condiciones la garantía será suspendida \n" \
                f"Muchas gracias 😊 "

    send_message(data['phone'], message)


def message_renew(profile, phone, date_limit):

    message =  f"Hola, tu servicio {profile.count.platform.name} ha sido renovado y se encuentra activo, \n" \
                f"👤USUARIO:  {profile.count.email}   \n" \
                f"🔐CONTRASEÑA: {profile.count.password} \n" \
                f"📺: PERFIL {profile.profile}  \n" \
                f"🔒 PIN: {profile.pin} \n" \
                f"📅 Fecha de corte: {date_limit.strftime('%d/%m/%Y')} \n" \
                f"Condiciones del servicio:  \n" \
                f"1.-No modifique ninguna información de la cuenta \n" \
                f"2.-No puede estar en 2 o más dispositivos simultáneamente  \n" \
                f"3.-No agregue ni elimine ningún perfil \n" \
                f"4.-Este es un producto digital. Después de la compra, no se puede  \n" \
                f"hacer ningún reembolso. Solo garantía de reemplazo. \n" \
                f"Nota: Si viola algunas de estas condiciones la garantía será suspendida \n" \
                f"Muchas gracias 😊 "
    send_message(str(phone), message)

def send_message(phone, message):

    try:
        payload = "token="+settings.TOKEN_WHATSAPP_API+"&to="+ phone + "&body="+ message
        payload = payload.encode('utf8').decode('iso-8859-1')
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        response = requests.request("POST", url, data=payload, headers=headers)
        return response.text
    except:

        return "Hubo un error al enviar el mensaje"
