import http.server
#import socketserver

#init du server 
PORT = 5000 
server_address = ("", PORT) #on ne met rien car on est en local

server = http.server.HTTPServer
handler = http.server.CGIHTTPRequestHandler #gestionnaire des requetes 
handler.cgi_directories = ["/"]
httpd = server(server_address, handler)
print("Serveur actif sur le port :", PORT)

httpd.serve_forever()