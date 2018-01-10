#! /usr/bin/env python2.7
# -*- coding: utf8 -*-

import os
import sys
import time
import posix_ipc as pos
import subprocess

def init():
    #Initialisation des deux files FCS et FSC
    #!!! problÃ¨me potentiel initialisation,  si erreur Ã§a detruit puis Ã§a recreer (perte msg?)? quel erreur ?
    # a voir avec le tp ConsMessage !!!

    #FCS
    try:
        FCS = pos.MessageQueue("/queueFCS",pos.O_CREAT)    #crÃ©ation ou ouverture de la file
        print("FCS: Creation/Ouverture de la file de message client to serveur")
    except pos.ExistentialError:
        S = pos.unlink_message_queue("/queueFCS") #destruction de la file
        FCS = pos.MessageQueue("/queueFCS",pos.O_CREAT) #puis redemande

    #FSC
    try:
        FSC = pos.MessageQueue("/queueFSC",pos.O_CREAT)    #crÃ©ation ou ouverture de la file
        print("FSC: Creation/Ouverture de la file de message serveur to client")
    except pos.ExistentialError:
        S = pos.unlink_message_queue("/queueFSC") #destruction de la file
        FSC = pos.MessageQueue("/queueFSC",pos.O_CREAT) #puis redemande

    #On rÃ©cupÃ¨re les paramÃ¨tres et varables utiles                
    nomFichier = sys.argv[0]    #rÃ©cupÃ¨re le 1er paramÃ¨tre, oÃ¹ le nom du fichier doit Ãªtre spÃ©cifier
    pidClient = os.getpid()     #On rÃ©cupÃ¨re l'id du processus client

def consultation():
    recupNumEnreg = raw_input("Veuillez entrer le numero d'enregistrement que vous voulez consulter.")  #on demande a l'user d'entrer son num d'enregistrement pour creer la requete
    FCS.send("consultation" + "/" + str(pidClient) + "/" + nomFichier + "/" + str(recupNumEnreg) + "/" + "-" , None, 1) #On lance le message en concÃ©quence, et avec toutes les informations utiles
    print("Veuillez patienter le temps que le serveur traite votre requete: "+str(pidClient))
    msgCons = FSC.receive() #receive a revoir !
    print(msgCons)  #On recois et on affiche le rÃ©sultat de la requete

def visualisation():
    FCS.send("visualisation" + "/" + str(pidClient) + "/" + nomFichier + "/" + "-" + "/" + "-", None, 1)    #On rÃ©alise une visualisation
    print("Veuillez patienter le temps que le serveur traite votre requete: "+str(pidClient))
    msgVisu = FSC.receive()  #!
    print(msgVisu)
    
def modification():
    #subprocess.call("start python prog2.py")
    recupNumEnreg = raw_input("Veuillez entrer le numero d'enregistrement que vous voulez modifier.")
    FCS.send("modifiation" + "/" + str(pidClient) + "/" + nomFichier + "/" + str(recupNumEnreg) + "/" + "-" , None, 2) #On rÃ©alise dÃ©jÃ  une consultation
    print("Veuillez patienter le temps que le serveur traite votre requete")
    msgCons = FSC.receive() #!
    print(format(msgCons))
    choixModif = raw_input("Voulez vous changer ce contenu ? O/N")  #on demande a l'user si il veut vraiment modifier l'enregistrement qu'on vient de lui afficher
    if choixModif == "O":
        nouvelEnreg = raw_input("Veuillez entrer le nouvel enregistrement.")    #si oui, il entre le nouveau
        FCS.send(str(nouvelEnreg) , None, 2)
        print("Veuillez patienter le temps que le serveur traite votre requete")
        msgModif = FSC.receive()   #!
        print(format(msgModif))
    elif choixModif == "N":
        print("Modification annulÃ©e.")
    else:
        print("EntrÃ©e invalide, modification annulÃ©e.")

def suppression():
    #subprocess.call("start python prog2.py")
    recupNumEnreg = raw_input("Veuillez entrer le numero d'enregistrement que vous voulez supprimer.")
    FCS.send("suppression" + "/" + str(pidClient) + "/" + nomFichier + "/" + str(recupNumEnreg) + "/" + "-" , None, 2)  #On rÃ©alise dÃ©jÃ  une consultation
    print("Veuillez patienter le temps que le serveur traite votre requete")
    msgCons = FSC.receive(pidClient) #!
    print(format(msgCons))
    choixModif = raw_input("Voulez vous supprimer ce contenu ? O/N") #on demande a l'user si il veut vraiment supprimer l'enregistrement qu'on vient de lui afficher
    if choixModif == "O":
        FCS.send("suppression" + "/" + str(pidClient) + "/" + nomFichier + "/" + str(recupNumEnreg) + "/" + "-" , None, 1)  #Si oui, on rÃ©alise mtn une suppression
        print("Veuillez patienter le temps que le serveur traite votre requete")
        msgSupp = FSC.receive(pidClient)   #!
        print(format(msgSupp))
    elif choixModif == "N":
        print("Suppression annulÃ©e.")
    else:
        print("EntrÃ©e invalide, suppression annulÃ©e.")
     
def adjonction():
    recupNouvelEnreg = raw_input("Veuillez entrer votre nouvel enregistrement.")
    FCS.send("adjonction" + "/" + str(pidClient) + "/" + nomFichier + "/" + "-" + "/" + str(recupNouvelEnreg) , None, 3)  #On rÃ©alise une adjonction
    print("Veuillez patienter le temps que le serveur traite votre requete")
    msgAdj = FSC.receive(pidClient) #!
    print(format(msgAdj))
 
def quitter():
    sys.exit(0)

#--- programme client: l'on demande Ã  l'utilisateur ce qu'il veut faire sur le fichier en paramÃ¨tre, l'on rÃ©alise l'action, envois des messages puis rÃ©ception du rÃ©sultat/notification.

init()  #on init les variables globales et les files

actionEffectue = False
while actionEffectue == False:   #On recommence tant qu'on a pas une action valide
    recupValeur = raw_input("Choisissez le type de requete : C, M, S, A, V ou F ")  #On fait choisir une action Ã  l'utilisateur
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
        print("EntrÃ©e invalide, veuillez recommencer.")
    
quitter()
