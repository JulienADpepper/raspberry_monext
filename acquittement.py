# Import de bibliothèques
import logging # Importe le module pour faire les logging
import pickle # pour l'utilisation des fichiers, ecriture et lecture

OL=None #lecture du fichier contenant la liste des eventId acquités
with open ('liste', 'rb') as f1: #penser a mettre le chemin complet
    OL= pickle.load(f1) #la variable OL prend la liste des enventId acquités

def allumage(listep): #fonction chargé de l'allumage de la led sur le raspberry
    logging.info('entré dans l allumage')
    #state = GPIO.input(LED) #Lit l'état actuel du GPIO, vrai si allumé, faux si éteint
    if (len(listep) != 0) : #si la liste n'est pas vide et la LED est éteinte alors il y a des alertes critical donc on allume
        logging.info('led allumé')
        #GPIO.output(LED, GPIO.HIGH) #allumage de la LED
        return True #utile pour verifier le bon fonctionnement du programme
    if (len(listep) == 0) :#si la liste est vide et la LED est allumé alors il n'y a plus d'alertes critical et donc on allume
        logging.info('led éteinte')
        #GPIO.output(LED, GPIO.LOW)#extinction de la LED
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
    with open('liste', 'wb') as f1:#remmettre le bon chemin
        pickle.dump(OL, f1)
    allumage(l)


#lancement
acquittement(l)