# Import de bibliothèques
import string
import flask
from flask import request, jsonify
import requests # Importe le module pour faire les requettes curl
import logging # Importe le module pour faire les logging

#init logging
logging.basicConfig (level=logging.INFO)

# Création de l'objet Flask
app = flask.Flask(__name__)
logging.info('app créée')
# Lancement du Débogueur
app.config["DEBUG"] = True
logging.info('debugger actif')
# récupération des données
url = 'https://apm-monextsaas.instana.io/api/events'
headers = {'Authorization' : 'apiToken cgKLVDihQISoLPY5JOJSZg'}
r = requests.get(url, headers=headers)
event=r.json()
logging.info('event recupere')

#fonctions de l'api
@app.route('/index.py', methods=['GET'])
def home():
    return '''<h1>Api pour raspberry pi</h1>
<p>Ce site est le prototype d une API utilise sur raspberry pi</p>'''
logging.info('page principale affiche')

# Route permettant de récupérer toutes les données de l’annuaire
@app.route('/api/event/all', methods=['GET'])
def api_all():
    l = jsonify(event)
    Var = {'r':event}
    exec(open('/home/jaime/raspberry_MONEXT/programme_led_v2.py').read(), Var)#execute le programme pour allumer la led
    return l

#recupère les event trié par type
@app.route('/api/event/type=<caract>', methods=['GET'])
def api_issue(caract) :
    r = []
    for e in event:
        if e['type']==caract :
            r.append(e)
    l=jsonify(r)
    return l
    
#recupere les events trié par niveau de severite
@app.route('/api/event/severite=<entier>',methods=['GET'])
def api_severite(entier):
    r=[]
    entier=int(entier)
    for e in event :
        if e['severity']==entier :
            r.append(e)
    l=jsonify(r)
    return l

#recupere les events trié par ID
@app.route('/api/event/Id=<id>',methods=['GET'])
def api_id(id):
    r=[]
    for e in event:
        if e['eventId']==id :
            r.append(e)
    l=jsonify(r)
    return l

#recupere les events trié par type d'entité
@app.route('/api/event/entityType=<type>',methods=['GET'])
def api_entityType(type):
    r=[]
    for e in event:
        if e['entityType']==type :
            r.append(e)
    l=jsonify(r)
    return l

#recupere les events trié par nom d'entité
@app.route('/api/event/entityName=<nom>',methods=['GET'])
def api_entityName(nom):
    r=[]
    for e in event:
        if e['entityName']==nom :
            r.append(e)
    l=jsonify(r)
    return l

#double filtrage par nom et type d'entité
@app.route('/api/event/entityName=<nom>&entityType=<type>',methods=['GET'])
def api_doubleEntity(nom, type):
    r=[]
    for e in event :
        if e['entityName']==nom and e['entityType']==type :
            r.append(e)
    l=jsonify(r)
    return l

#double filtrage par type d'event et niveau de severité
@app.route('/api/event/type=<type>&severite=<entier>',methods=['GET'])
def api_type_severite(type, entier):
    r=[]
    entier=int(entier)
    for e in event :
        if e['type']==type and e['severity']==entier :
            r.append(e)
    l=jsonify(r)
    Var = {'r':r}
    exec(open('/home/jaime/raspberry_MONEXT/programme_led_type&severite.py').read(), Var)#execute le programme pour allumer la led
    return l

#lancement 
app.run()
