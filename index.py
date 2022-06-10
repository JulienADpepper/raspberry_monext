import cgi

# Import de bibliothèques
import sys
import logging # Importe le module pour faire les logging

#init logging

logging.basicConfig (level=logging.INFO)

logging.info('ouverture')
exec(open("api_test.py").read())
logging.info('roger')