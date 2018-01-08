#! /usr/bin/env python2.7
# -*- coding: utf8 -*-

import os
import sys
import posix_ipc as pos
#import subprocess
#subprocess.call("start python prog2.py")

def consultation():
    recupNumEnreg = raw_input("Veuillez entrer le numero d'enregistrement que vous voulez consulter.")  #on demande a l'user d'entrer son num d'enregistrement pour creer la requete
    FCS.send("consultation" + "/" + str(pidClient) + "/" + nomFichier + "/" + str(recupNumEnreg) + "/" + "-" , None, 3) #On lance le message en concéquence, et avec toutes les informations utiles
    print("Veuillez patienter le temps que le serveur traite votre requete")
    msgCons = FSC.receive() 
    print(msgCons)  #On recois et on affiche le résultat de la requete

def visualisation():
    FCS.send("visualisation" + "/" + str(pidClient) + "/" + nomFichier + "/" + "-" + "/" + "-", None, 3)    #On réalise une visualisation
    print("Veuillez patienter le temps que le serveur traite votre requete")
    msgVisu = FSC.receive()  #!
    print(msgVisu)   
    
def modification():
    Slaps = pos.Semaphore("/Semaphore_laps" + nomFichier ,pos.O_CREAT,initial_value=0)
    recupNumEnreg = raw_input("Veuillez entrer le numero d'enregistrement que vous voulez modifier.")
    FCS.send("modification" + "/" + str(pidClient) + "/" + nomFichier + "/" + str(recupNumEnreg) + "/" + "-" , None, 1)
    print("Veuillez patienter le temps que le serveur traite votre requete")
    msgCons = FSC.receive(pidClient) #!
    print(format(msgCons))
    choixModif = raw_input("Voulez vous changer ce contenu ? O/N")  #on demande a l'user si il veut vraiment modifier l'enregistrement qu'on vient de lui afficher
    if choixModif == "O":
        NouvelEnreg = raw_input("Veuillez entrer le nouvel enregistrement.")    #si oui, il entre le nouveau
        FCS.send("modification" + "/" + str(pidClient) + "/" + nomFichier + "/" + str(recupNumEnreg) + "/" + "-" , None, 1)    #On réalise mtn une modification
        Slaps.release()
        print("Veuillez patienter le temps que le serveur traite votre requete")
        msgModif = FSC.receive(pidClient)   #!
        print(format(msgModif))
    elif choixModif == "N":
        print("Modification annulée.")
    else:
        print("Entrée invalide, modification annulée.")
    Slaps.close()

def suppression():
    recupNumEnreg = raw_input("Veuillez entrer le numero d'enregistrement que vous voulez supprimer.")
    FCS.send("consultation" + "/" + str(pidClient) + "/" + nomFichier + "/" + str(recupNumEnreg) + "/" + "-" , None, 2)  #On réalise déjà une consultation
    print("Veuillez patienter le temps que le serveur traite votre requete")
    msgCons = FSC.receive(pidClient) #!
    print(format(msgCons))
    choixSupp = raw_input("Voulez vous supprimer ce contenu ? O/N") #on demande a l'user si il veut vraiment supprimer l'enregistrement qu'on vient de lui afficher
    if choixModif == "O":
        FCS.send("suppression" + "/" + str(pidClient) + "/" + nomFichier + "/" + str(recupNumEnreg) + "/" + "-" , None, 1)  #Si oui, on réalise mtn une suppression
        print("Veuillez patienter le temps que le serveur traite votre requete")
        msgSupp = FSC.receive(pidClient)   #!
        print(format(msgSupp))
    elif choixModif == "N":
        print("Suppression annulée.")
    else:
        print("Entrée invalide, suppression annulée.")
     
def adjonction():
    recupNouvelEnreg = raw_input("Veuillez entrer votre nouvel enregistrement.")
    FCS.send("adjonction" + "/" + str(pidClient) + "/" + nomFichier + "/" + "-" + "/" + str(recupNouvelEnreg) , None, 3)  #On réalise une adjonction
    print("Veuillez patienter le temps que le serveur traite votre requete")
    msgAdj = FSC.receive(pidClient) #!
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

#On récupère les paramètres et varables utiles                
nomFichier = sys.argv[0]    #récupère le 1er paramètre, où le nom du fichier doit être spécifier
pidClient = os.getpid()     #On récupère l'id du processus client

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
