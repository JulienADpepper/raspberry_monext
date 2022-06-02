#definition des imports
import RPi.GPIO as GPIO #Importe la bibliothèque pour contrôler les GPIOs
import requests #Importe le module pour faire les requettes curl
import logging # Importe le module pour faire les logging
import configparser #Importe le module pour lire le fichier de configuration
import pickle

#definition des variables
config = configparser.ConfigParser() #initialisation du configparser pour lire le fichier de conf

config.read('config.ini') #ouvre le fichier de configuration

print(config.sections()) #pour verifier que le fichier de conf est bien ouvert

logging.basicConfig(level=logging.INFO) #config du logging 

GPIO.setmode(GPIO.BOARD) #Définit le mode de numérotation (Board)
GPIO.setwarnings(False) #On désactive les messages d'alerte

LED = int(config['Port_de_sortie']['led']) #Définit le numéro du port GPIO qui alimente la led

GPIO.setup(LED, GPIO.OUT) #Active le contrôle du GPIO

url = config['Curl']['url'] #définition de l'url de l'api pour extraire les informations 

type_header = config['Curl']['type_header'] #définition des variables du headers
token = config['Curl']['token']
headers = {type_header : token} # definition des headers 

r = requests.get(url, headers=headers)#requette curl dans python #la requette curl est stoqué dans une variable r

l=r.json() #le fichier json extrait de l'api est stoqué dans la liste de dictionnaires l

OL=None #lecture du fichier contenant la liste des eventId acquités
with open ('liste', 'rb') as f1:
    OL= pickle.load(f1) #la variable OL prend la liste des enventId acquités

#definition des fonctions

def liste_des_erreurs(listep) : #permet de ne récupérer que les cas qui nous interresse 
    result=[] #après la requette cURL
    type_erreur = config['Filtre']['type_erreur'] #recupere du fichier de conf les bonnes valeurs
    severite = int(config['Filtre']['niveau_de_severite']) #récupere le niveau de severite du fichier de conf 
    for i in listep :
        if (i['type']==type_erreur) and (i['severity']==severite) and (i['eventId'] not in OL):
            result.append(i) #result récupere les elements de l ayant le bon type d'erreur et la bonne severite
    return result

def allumage(listep): #programme chargé de l'allumage de la led sur le raspberry
    logging.info('entré dans l allumage')
    state = GPIO.input(LED) #Lit l'état actuel du GPIO, vrai si allumé, faux si éteint
    if (len(listep) != 0) and not(state) : #si la liste n'est pas vide et la LED est éteinte alors il y a des alertes critical donc on allume
        logging.info('led allumé')
        GPIO.output(LED, GPIO.HIGH) #allumage de la LED
        return True #utile pour verifier le bon fonctionnement du programme
    if (len(listep) == 0) and state :#si la liste est vide et la LED est allumé alors il n'y a plus d'alertes critical et donc on allume
        logging.info('led éteinte')
        GPIO.output(LED, GPIO.LOW)#extinction de la LED
        return False #utile pour verifier le bon fonctionnement du programme

def acquittement(listep): #demande a l'utilisateur s'il veut acquitter les evennements et enrichie la liste des evenemments acquittés
    logging.info('entré dans l acquittement')
    for i in listep :
        question = "voulez-vous acquiter l'event : ",  i['eventId'], "?"
        resp = input (question)
        if resp == 'oui' :
            OL.append(i['eventId'])
            print("event acquitté")
            logging.info('event acquitté')
    with open('liste', 'wb') as f1:
        pickle.dump(OL, f1)
    allumage(liste_des_erreurs(l)) #éteind la LED si tout est acquitté

#affichage
allumage(liste_des_erreurs(l)) #lancement du code, mettre print devant pour verifier les sortie true et false
print(acquittement(liste_des_erreurs(l))) #lance la procédure d'acquittement