from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import http.client
import json

app = Flask(__name__)

#Configuracion de la base de datos SQLITE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metapython.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db =SQLAlchemy(app)

#Modelo de la tabla log
class Log(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    fecha_y_hora = db.Column(db.DateTime, default=datetime.utcnow)
    texto = db.Column(db.TEXT)

#Crear la tabla si no existe
with app.app_context():
    db.create_all()

#Funcion para ordenar los registros por fecha y hora
def ordenar_por_fecha_y_hora(registros):
    return sorted(registros, key=lambda x: x.fecha_y_hora,reverse=True)

@app.route('/')
def index():
    #obtener todos los registros ed la base de datos
    registros = Log.query.all()
    registros_ordenados = ordenar_por_fecha_y_hora(registros)
    return render_template('index.html',registros=registros_ordenados)

mensajes_log = []

#Funcion para agregar mensajes y guardar en la base de datos
def agregar_mensajes_log(texto):
    mensajes_log.append(texto)

    #Guardar el mensaje en la base de datos
    nuevo_registro = Log(texto=texto)
    db.session.add(nuevo_registro)
    db.session.commit()

#Token de verificacion para la configuracion
TOKEN_ANDERCODE = "ANDERCODE"

@app.route('/webhook', methods=['GET','POST'])
def webhook():
    if request.method == 'GET':
        challenge = verificar_token(request)
        return challenge
    elif request.method == 'POST':
        reponse = recibir_mensajes(request)
        return reponse

def verificar_token(req):
    token = req.args.get('hub.verify_token')
    challenge = req.args.get('hub.challenge')

    if challenge and token == TOKEN_ANDERCODE:
        return challenge
    else:
        return jsonify({'error':'Token Invalido'}),401

def recibir_mensajes(req):
    try:
        req = request.get_json()
        entry =req['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        objeto_mensaje = value['messages']

        if objeto_mensaje:
            messages = objeto_mensaje[0]

            if "type" in messages:
                tipo = messages["type"]

                #Guardar Log en la BD
                agregar_mensajes_log(json.dumps(messages))

                if tipo == "interactive":
                    tipo_interactivo = messages["interactive"]["type"]

                    if tipo_interactivo == "button_reply":
                        text = messages["interactive"]["button_reply"]["id"]
                        numero = messages["from"]

                        enviar_mensajes_whatsapp(text,numero)
                    
                    elif tipo_interactivo == "list_reply":
                        text = messages["interactive"]["list_reply"]["id"]
                        numero = messages["from"]

                        enviar_mensajes_whatsapp(text,numero)

                if "text" in messages:
                    text = messages["text"]["body"]
                    numero = messages["from"]

                    enviar_mensajes_whatsapp(text,numero)

                    #Guardar Log en la BD
                    agregar_mensajes_log(json.dumps(messages))

        return jsonify({'message':'EVENT_RECEIVED'})
    except Exception as e:
        return jsonify({'message':'EVENT_RECEIVED'})

def enviar_mensajes_whatsapp(texto,number):
    texto = texto.lower()

    if "hola" in texto:
        data={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "🚀 Hola, ¿Cómo estás? Bienvenido."
            }
        }
    elif "1" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "La Ludoteca de Loja, Ecuador, es un espacio dedicado al desarrollo infantil y a la educación lúdica. Este tipo de instalaciones suelen ofrecer actividades recreativas y educativas para niños, fomentando el aprendizaje a través del juego. A continuación, te proporciono información general que podría ser relevante sobre ludotecas en general y específicamente sobre la de Loja"
            }
        }
    elif "2" in texto:
        data = {
            "messaging_product": "whatsapp",
            "to": number,
            "type": "location",
            "location": {
                "latitude": "-4.003840842975254",
                "longitude": "-79.2007854169413",
                "name": "Ludus tu Ludoteca Infantil",
                "address": "Bernardo Valdivieso entre Cariamanga, y, Loja 110109"
            }
        }
    elif "3" in texto:
        data={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                    "link": "https://www.turnerlibros.com/wp-content/uploads/2021/02/ejemplo.pdf",
                    "caption": "Temario del Curso #001"
                }
            }
    elif "4" in texto:
        data={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "audio",
            "audio": {
                "link": "https://filesamples.com/samples/audio/mp3/sample1.mp3"
            }
        }
    elif "5" in texto:
        data = {
            "messaging_product": "whatsapp",
            "to": number,
            "text": {
                "preview_url": True,
                "body": "Introduccion al curso! https://youtu.be/6ULOE2tGlBM"
            }
        }
    elif "6" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "🤝 En breve me pondre en contacto contigo. 🤓"
            }
        }
    elif "7" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "📅 Horario de Atención : Lunes a Domingo. \n🕜 Horario : 8:00 am a 19:00 pm 🤓"
            }
        }
    elif "0" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "🚀 Hola, visita https://www.facebook.com/share/AtEXPDQsHYbGSwhY/?mibextid=qi2Omg para más información.\n \n📌Por favor, ingresa un número #️⃣ para recibir información.\n \n1️⃣. Información de Ludoteca. ❔\n2️⃣. Ubicación del local. 📍\n3️⃣. Enviar temario en PDF. 📄\n4️⃣. Audio explicando curso. 🎧\n5️⃣. Video de Introducción. ⏯️\n6️⃣. Hablar con Ludoteca. 🙋‍♂️\n7️⃣. Horario de Atención. 🕜 \n0️⃣. Regresar al Menú. 🕜"
            }
        }
    elif "boton" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive":{
                "type":"button",
                "body": {
                    "text": "¿Confirmas tu registro?"
                },
                "footer": {
                    "text": "Selecciona una de las opciones"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply":{
                                "id":"btnsi",
                                "title":"Si"
                            }
                        },{
                            "type": "reply",
                            "reply":{
                                "id":"btnno",
                                "title":"No"
                            }
                        },{
                            "type": "reply",
                            "reply":{
                                "id":"btntalvez",
                                "title":"Tal Vez"
                            }
                        }
                    ]
                }
            }
        }
    elif "btnsi" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Muchas Gracias por Aceptar."
            }
        }
    elif "btnno" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Es una Lastima."
            }
        }
    elif "btntalvez" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Estare a la espera."
            }
        }
    elif "lista" in texto:
        data ={
            "messaging_product": "whatsapp",
            "to": number,
            "type": "interactive",
            "interactive":{
                "type" : "list",
                "body": {
                    "text": "Selecciona Alguna Opción"
                },
                "footer": {
                    "text": "Selecciona una de las opciones para poder ayudarte"
                },
                "action":{
                    "button":"Ver Opciones",
                    "sections":[
                        {
                            "title":"Compra y Venta",
                            "rows":[
                                {
                                    "id":"btncompra",
                                    "title" : "Comprar",
                                    "description": "Compra los mejores articulos de tecnologia"
                                },
                                {
                                    "id":"btnvender",
                                    "title" : "Vender",
                                    "description": "Vende lo que ya no estes usando"
                                }
                            ]
                        },{
                            "title":"Distribución y Entrega",
                            "rows":[
                                {
                                    "id":"btndireccion",
                                    "title" : "Local",
                                    "description": "Puedes visitar nuestro local."
                                },
                                {
                                    "id":"btnentrega",
                                    "title" : "Entrega",
                                    "description": "La entrega se realiza todos los dias."
                                }
                            ]
                        }
                    ]
                }
            }
        }
    elif "btncompra" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Los mejos articulos top en ofertas."
            }
        }
    elif "btnvender" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Excelente elección."
            }
        }
    else:
        data={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "🚀 Hola, visita https://www.facebook.com/share/AtEXPDQsHYbGSwhY/?mibextid=qi2Omg para más información.\n \n📌Por favor, ingresa un número #️⃣ para recibir información.\n \n1️⃣. Información de Ludoteca. ❔\n2️⃣. Ubicación del local. 📍\n3️⃣. Enviar temario en PDF. 📄\n4️⃣. Audio explicando curso. 🎧\n5️⃣. Video de Introducción. ⏯️\n6️⃣. Hablar con Ludoteca. 🙋‍♂️\n7️⃣. Horario de Atención. 🕜 \n0️⃣. Regresar al Menú. 🕜"
            }
        }

    #Convertir el diccionaria a formato JSON
    data=json.dumps(data)

    headers = {
        "Content-Type" : "application/json",
        "Authorization" : "Bearer EAAOttkFM0QUBO48Ll0d7zJ2rx8rp9zEHJK042rZCe8SwDMaWy5mD4LZB1ZADlYd908V2C4FgXJqrRcuAwCBLwX3oxVbwNUkgyNafH9tT30ax1JrXuO5bJOm8HlThgTyWwnV8bZBEEhJOlcPKPJ0MNv7sEKGQuRIBSh3p3CjW2BEy7ePinc6Y1X652BNI8bJ5jgZDZD"
    }

    connection = http.client.HTTPSConnection("graph.facebook.com")

    try:
        connection.request("POST","/v20.0/435809882950120/messages", data, headers)
        response = connection.getresponse()
        print(response.status, response.reason)
    except Exception as e:
        agregar_mensajes_log(json.dumps(e))
    finally:
        connection.close()

if __name__=='__main__':
    #app.run(host='0.0.0.0',port=80,debug=True)
    app.run(host='0.0.0.0', port=5001, debug=True)
