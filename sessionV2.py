#! /usr/bin/env python2.7
# -*- coding: utf8 -*-

import os
import sys
import time
import posix_ipc as pos
import subprocess

#On récupère les paramètres et varables utiles                
nomFichier = sys.argv[0]    #récupère le 1er paramètre, où le nom du fichier doit être spécifier
pidClient = os.getpid()     #On récupère l'id du processus client

def ouvrirFileServeurToClient(pidClient,nomFichier):
    FStoC = pos.MessageQueue("/queue-" + pidClient + "-" + nomFichier,pos.O_CREAT)    #création ou ouverture de la file de serveur vers client, une file par client et par fichier

def consultation():
    recupNumEnreg = raw_input("Veuillez entrer le numero d'enregistrement que vous voulez consulter.")  #on demande a l'user d'entrer son num d'enregistrement pour creer la requete
    FCS.send("consultation" + "/" + str(pidClient) + "/" + nomFichier + "/" + str(recupNumEnreg) + "/" + "-" , None, 3) #On lance le message en concéquence, et avec toutes les informations utiles
    print("Veuillez patienter le temps que le serveur traite votre requete: "+str(pidClient))
    
    ouvrirFileServeurToClient(pidClient,nomFichier)
    msgCons = FStoC.receive(int(pidClient))
    #msgCons = FSC.receive(int(pidClient)) #receive a revoir !
    print(msgCons)  #On recois et on affiche le résultat de la requete

def visualisation():
    FCS.send("visualisation" + "/" + str(pidClient) + "/" + nomFichier + "/" + "-" + "/" + "-", None, pidClient)    #On réalise une visualisation
    print("Veuillez patienter le temps que le serveur traite votre requete: "+str(pidClient))
    time.sleep(8)

    ouvrirFileServeurToClient(pidClient,nomFichier)
    msgVisu = FStoC.receive(int(pidClient))
    #msgVisu = FSC.receive(int(pidClient))  #!
    print(msgVisu)
    
def modification():
    try:
        Slaps= pos.Semaphore("/Semaphore_laps",pos.O_CREAT|pos.O_EXCL,initial_value=0)
    except pos.ExistentialError:
        Slaps= pos.Semaphore("/Semaphore_laps",pos.O_CREAT)
    #subprocess.call("start python prog2.py")
    recupNumEnreg = raw_input("Veuillez entrer le numero d'enregistrement que vous voulez modifier.")
    FCS.send("consultation" + "/" + str(pidClient) + "/" + nomFichier + "/" + str(recupNumEnreg) + "/" + "-" , None, pidClient) #On réalise déjà une consultation
    print("Veuillez patienter le temps que le serveur traite votre requete")

    ouvrirFileServeurToClient(pidClient,nomFichier)
    msgCons = FStoC.receive(pidClient)
    #msgCons = FSC.receive(pidClient) #!
    print(format(msgCons))
    FCS.send("tempsAttente"+ "/" + str(pidClient) + "/" + nomFichier +"/ - / -", None, 2)
    choixModif = raw_input("Voulez vous changer ce contenu ? O/N")  #on demande a l'user si il veut vraiment modifier l'enregistrement qu'on vient de lui afficher
    if choixModif == "O":
	Slaps.release()
	msgAttente=FSC.receive()
	msgA,pidMes=msgAttente
	if msgA == "ok":
           NouvelEnreg = raw_input("Veuillez entrer le nouvel enregistrement.")    #si oui, il entre le nouveau
           FCS.send("modification" + "/" + str(pidClient) + "/" + nomFichier + "/" + str(recupNumEnreg) + "/" + str(NouvelEnreg) , None, 1)    #On réalise mtn une modification
           print("Veuillez patienter le temps que le serveur traite votre requete")
           msgModif = FStoC.receive(pidClient)
           #msgModif = FSC.receive(pidClient)   #!
           print(format(msgModif))
        else:
	   print("Le temps d'attente de votre reponse est depasse votre requete va etre annule")
    elif choixModif == "N":
        Slaps.release()
	msgAttente=FSC.receive()
        print("Modification annulée.")
    else:
        print("Entrée invalide, modification annulée.")
    Slaps.close()

def suppression():
    try:
        Slaps= pos.Semaphore("/Semaphore_laps",pos.O_CREAT|pos.O_EXCL,initial_value=0)
    except pos.ExistentialError:
        Slaps= pos.Semaphore("/Semaphore_laps",pos.O_CREAT)
    #subprocess.call("start python prog2.py")
    recupNumEnreg = raw_input("Veuillez entrer le numero d'enregistrement que vous voulez supprimer.")
    FCS.send("consultation" + "/" + str(pidClient) + "/" + nomFichier + "/" + str(recupNumEnreg) + "/" + "-" , None, 2)  #On réalise déjà une consultation
    print("Veuillez patienter le temps que le serveur traite votre requete")
    ouvrirFileServeurToClient(pidClient,nomFichier)
    msgCons = FStoC.receive(pidClient)
    #msgCons = FSC.receive(pidClient) #!
    print(format(msgCons))
    FCS.send("tempsAttente"+ "/" + str(pidClient) + "/" + nomFichier +"/ - / -", None, 2)
    choixModif = raw_input("Voulez vous supprimer ce contenu ? O/N") #on demande a l'user si il veut vraiment supprimer l'enregistrement qu'on vient de lui afficher
    if choixModif == "O":
        Slaps.release()
	msgAttente=FSC.receive()
	msgA,pidMes=msgAttente
	if msgA == "ok":
            FCS.send("suppression" + "/" + str(pidClient) + "/" + nomFichier + "/" + str(recupNumEnreg) + "/" + "-" , None, 1)  #Si oui, on réalise mtn une suppression
            print("Veuillez patienter le temps que le serveur traite votre requete")
            msgSupp = FStoC.receive(pidClient)
            #msgSupp = FSC.receive(pidClient)   #!
            print(format(msgSupp))
	else:
	    print("Le temps d'attente de votre reponse est depasse votre requete va etre annule")
    elif choixModif == "N":
	Slaps.release()
	msgAttente=FSC.receive()
	print(msgAttente)
        print("Suppression annulée.")
    else:
        print("Entrée invalide, suppression annulée.")
    Slaps.close()
     
def adjonction():
    recupNouvelEnreg = raw_input("Veuillez entrer votre nouvel enregistrement.")
    FCS.send("adjonction" + "/" + str(pidClient) + "/" + nomFichier + "/" + "-" + "/" + str(recupNouvelEnreg) , None, 3)  #On réalise une adjonction
    print("Veuillez patienter le temps que le serveur traite votre requete")
    ouvrirFileServeurToClient(pidClient,nomFichier)
    msgAdj = FStoC.receive(pidClient)
    #msgAdj = FSC.receive(pidClient) #!
    print(format(msgAdj))
 
def quitter():
    sys.exit(0)

#--- programme client: l'on demande à l'utilisateur ce qu'il veut faire sur le fichier en paramètre, l'on réalise l'action, envois des messages puis réception du résultat/notification.
#Initialisation des deux files FCS et FSC

#!!! problème potentiel initialisation,  si erreur ça detruit puis ça recreer (perte msg?)? quel erreur ?
# a voir avec le tp ConsMessage !!!

#FCS
try:
    FCS = pos.MessageQueue("/queueFCS",pos.O_CREAT)    #création ou ouverture de la file
    print("FCS: Creation/Ouverture de la file de message client to serveur")
except pos.ExistentialError:
    S = pos.unlink_message_queue("/queueFCS") #destruction de la file
    FCS = pos.MessageQueue("/queueFCS",pos.O_CREAT) #puis redemande

#FSC
try:
    FSC = pos.MessageQueue("/queueFSC",pos.O_CREAT)    #création ou ouverture de la file
    print("FSC: Creation/Ouverture de la file de message serveur to client")
except pos.ExistentialError:
    S = pos.unlink_message_queue("/queueFSC") #destruction de la file
    FSC = pos.MessageQueue("/queueFSC",pos.O_CREAT) #puis redemande



actionEffectue = False
while actionEffectue == False:   #On recommence tant qu'on a pas une action valide
    recupValeur = raw_input("Choisissez le type de requete : C, M, S, A, V ou F ")  #On fait choisir une action à l'utilisateur
    if recupValeur == 'C':
            consultation()
            actionEffectue = True
    elif recupValeur == 'M':
            modification()
            actionEffectue = True
    elif recupValeur == 'S':
            suppression()
            actionEffectue = True
    elif recupValeur == 'A':
            adjonction()
            actionEffectue = True
    elif recupValeur == 'V':
            visualisation()
            actionEffectue = True
    elif recupValeur == 'F':
            quitter()
            actionEffectue = True
    else:
        print("Entrée invalide, veuillez recommencer.")
    
quitter()
