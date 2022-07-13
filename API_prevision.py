#pour le programme sur raspberry penser a importer GPIO, a rajouter le state partout ou il faut, et a faire allumer et éteindre 
#au lieu de return true ou false

#Import de bibliothèques
#import RPi.GPIO as GPIO #Importe la bibliothèque pour contrôler les GPIOs
#from pydoc import pager
import flask
from flask import request, jsonify
import requests # Importe le module pour faire les requettes curl
import logging # Importe le module pour faire les logging
import configparser #Importe le module pour lire le fichier de configuration
import pickle
import webbrowser #sert a affichier les pages web


#definition des variables
config = configparser.ConfigParser() #initialisation du configparser pour lire le fichier de conf

config.read('config.ini') #ouvre le fichier de configuration

print(config.sections()) #pour verifier que le fichier de conf est bien ouvert

logging.basicConfig(level=logging.INFO) #config du logging 

#GPIO.setmode(GPIO.BOARD) #Définit le mode de numérotation (Board)
#GPIO.setwarnings(False) #On désactive les messages d'alerte

LED_c = int(config['Port_de_sortie']['led_c']) #Définit le numéro du port GPIO qui alimente la led
LED_p = int(config['Port_de_sortie']['led_p']) #Définit le numéro du port GPIO qui alimente la led
#GPIO.setup(LED_c, GPIO.OUT) #Active le contrôle du GPIO
#GPIO.setup(LED_p, GPIO.OUT) #Active le contrôle du GPIO

OL=None #lecture du fichier contenant la liste des eventId acquités
with open ('liste', 'rb') as f1: #penser a changer l'adresse en mettant tout le chemin
    OL= pickle.load(f1) #la variable OL prend la liste des enventId acquités
logging.info('ouverture fichier id acquitte')

CL=None #lecture du fichier contenant la liste des eventId des fichier traités
with open ('liste_controle', 'rb') as f1: #penser a changer l'adresse en mettant tout le chemin
    CL= pickle.load(f1) #la variable OL prend la liste des enventId acquités
logging.info('ouverture fichier de controle')

#liste des alertes nécessitant une prestation
#Alerte = ['3DS_ACS_PROD - Alerte Instana - Nombre de transactions trop faible', '3DS_ACS_PROD - Alerte Instana - Nombre d'erreur 5XX trop élevé']

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

#fonction de traitement de la donnés :
def controle(listep): #fonction qui controle que l'event qui arrive n'a pas deja été traité
    logging.info('entre dans la fonction de controle')
    result=[]
    for i in listep :
        if (i['eventId'] not in CL) and (i['eventId'] not in OL) and (i['state']=='open'):
            result.append(i)
            CL.append(i['eventId'])
            logging.info('event non traité présent')
    with open('liste_controle', 'wb') as f1: #penser a mettre le bon chemin sur raspberry
        pickle.dump(OL, f1)
    logging.info('ecriture dans le fichier de controle')
    return result


def liste_des_erreurs(listep) : #permet de ne récupérer que les cas qui nous interresse 
    logging.info('entre dans la fonction de filtrage generale')
    result=[] #après la requette cURL
    type_erreur = config['Filtre']['type_erreur'] #recupere du fichier de conf les bonnes valeurs
    severite = int(config['Filtre']['niveau_de_severite']) #récupere le niveau de severite du fichier de conf 
    for i in listep :
        if (i['type']==type_erreur) and (i['severity']==severite) :
            result.append(i) #result récupere les elements de l ayant le bon type d'erreur et la bonne severite
    return result

def allumage_filtre_critical(listep): #fonction chargé de l'allumage de la led sur le raspberry
    logging.info('entré dans l allumage avec filtre pour event critical')
    #state_c = GPIO.input(LED_c) #Lit l'état actuel du GPIO, vrai si allumé, faux si éteint
    #state_p = GPIO.input(LED_p) #Lit l'état actuel du GPIO, vrai si allumé, faux si éteint
    result = []
    for i in listep :
        if (i['state']=='open'):
            result.append(i) #result récupere les elements de l ayant le bon type d'erreur et la bonne severite
    if (len(result) != 0) : #si la liste n'est pas vide et la LED est éteinte alors il y a des alertes critical donc on allume et rajouter if state
        logging.info('led_c allumé')
        #GPIO.output(LED_c, GPIO.HIGH) #allumage de la LED
        #if (i['detail'] in Alertes) and not state_p :
            #GPIO.output(LED_p, GPIO.HIGH) #allumage de la LED
        #if (i['detail'] not in Alertes) and state_p :
            #GPIO.output(LED_p, GPIO.LOW) #extinction de la LED
        page_web(listep)
        Var = {'l': listep}
        exec(open('acquittement.py').read(), Var) #lancement de la procédure d'acquittement
        return True #utile pour verifier le bon fonctionnement du programme
    if (len(result) == 0) :#si la liste est vide et la LED est allumé alors il n'y a plus d'alertes critical et donc on allume
        logging.info('led_c éteinte')
        #GPIO.output(LED, GPIO.LOW)#extinction de la LED
        #if (i['detail'] in Alertes) and not state_p :
            #GPIO.output(LED_p, GPIO.HIGH) #allumage de la LED
        #if (i['detail'] not in Alertes) and state_p :
            #GPIO.output(LED_p, GPIO.LOW) #extinction de la LED
        return False #utile pour verifier le bon fonctionnement du programme

def allumage(listep): #fonction chargé de l'allumage de la led sur le raspberry
    logging.info('entré dans l allumage') 
    #state_c = GPIO.input(LED_c) #Lit l'état actuel du GPIO, vrai si allumé, faux si éteint
    #state_p = GPIO.input(LED_p) #Lit l'état actuel du GPIO, vrai si allumé, faux si éteint
    if (len(listep) != 0) : #si la liste n'est pas vide et la LED est éteinte alors il y a des alertes critical donc on allume, rajouter if state
        logging.info('led allumé')
        #GPIO.output(LED, GPIO.HIGH) #allumage de la LED
        page_web(listep)
        Var = {'l': listep}
        exec(open('acquittement.py').read(), Var) #lancement de la procédure d'acquittement
        return True #utile pour verifier le bon fonctionnement du programme
    if (len(listep) == 0) :#si la liste est vide et la LED est allumé alors il n'y a plus d'alertes critical et donc on allume
        logging.info('led éteinte')
        #GPIO.output(LED, GPIO.LOW)#extinction de la LED
        return False #utile pour verifier le bon fonctionnement du programme

def page_web(listep):
    if len(listep) >1 :
        page = 'https://apm-monextsaas.instana.io/#/events;view=issue;orderDirection=DESC;orderBy=start'
    if len(listep) == 1 :
        id = listep[0]['eventId']
        page = 'https://apm-monextsaas.instana.io/#/events;eventId=', id
    webbrowser.open(page)


#fonctions de l'api
@app.route('/', methods=['GET'])
def home():
    return '''<h1>Api pour raspberry pi</h1>
<p>Ce site est le prototype d une API utilise sur raspberry pi</p>'''
logging.info('page principale affiche')

# Route permettant de récupérer toutes les données de l’annuaire
@app.route('/api/event/all', methods=['GET'])
def api_all():
    l = jsonify(event)
    print(allumage(liste_des_erreurs(controle(event))))#allumage et filtrage, penser a enlever le print sur raspberry
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

#filtrage par detail de l'event
@app.route('/api/event/detail=<detail>',methods=['GET'])
def api_titre(detail):
    r=[]
    for e in event:
        if e['detail']==detail :
            r.append(e)
    l=jsonify(r)
    print(allumage_filtre_critical(controle(r)))
    return l

#double filtrage par type d'event et niveau de severité plus gestion des erreurs nécéssitant une prestation
@app.route('/api/event/type=<type>&severite=<entier>',methods=['GET'])
def api_type_severite(type, entier):
    r=[]
    entier=int(entier)
    for e in event :
        if e['type']==type and e['severity']==entier :
            r.append(e)
    l=jsonify(r)
    print(allumage_filtre_critical(controle(r)))#allumage, penser a enlever le print sur raspberry
    return l

#lancement 
app.run()