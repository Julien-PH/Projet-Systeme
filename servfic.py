#! /usr/bin/env python2.7
# -*- coding: utf8 -*-

import os
import signal
import sys
from threading import Thread
import posix_ipc as pos
import time
from daemon import runner
 
class Deamon():
    def __init__(self):
        #va falloir peut être le remplir je crois

    def run(self):
        main()
    

def fermer_serveur(signal, frame):    #Appelé quand vient l'heure de fermer le serveur avec un ^C
    print("Fermeture du serveur")
    sys.exit(0)

def consultation(pidC,numEnreg):
    S = pos.Semaphore("/Semaphore_" + nomFichier ,pos.O_CREAT,initial_value=0)
    S.acquire()  #P(S)

    #On récup le contenu avec numEnreg et nomFichier

    S.release() #V(S)
    S.close()   #!
    FSC.send(contenu,None,pidC)
    
def modification(pidC,numEnreg,newEnreg):
    S = pos.Semaphore("/Semaphore_" + nomFichier ,pos.O_CREAT,initial_value=0)
    try:
        S.acquire(nbsecondes)  #P(S)

        #réaliser modification avec numEnreg, newEnreg et nomFichier
        #Notif de reussite ou non

        S.release() #V(S)
    except pos.BusyError:
        notif = "Le temps d'attente de " + nbsecondes + " secondes est dépassé, modification abandonnée."
    S.close()   #!
    FSC.send(notif,None,pidC)

def suppression(pidC,numEnreg):
    S = pos.Semaphore("/Semaphore_" + nomFichier ,pos.O_CREAT,initial_value=0)
    try:
        S.acquire()  #P(S)

        #réaliser la suppression avec numEnreg et nomFichier
        #Notif de reussite ou non

        S.release() #V(S)
    except:
        notif = "Le temps d'attente de " + nbsecondes + " secondes est dépassé, suppression abandonnée."
    S.close()   #!
    FSC.send(notif,None,pidC)
     
def adjonction(pidC,newEnreg):
    S = pos.Semaphore("/Semaphore_" + nomFichier ,pos.O_CREAT,initial_value=0)
    S.acquire()  #P(S)

    #On ajoute le contenu avec nuwEnreg et nomFichier
    #Notif de reussite ou non
    
    S.release() #V(S)
    S.close()   #!
    FSC.send(notif,None,pidC)
 
def visualisation(pidC):
    S = pos.Semaphore("/Semaphore_" + nomFichier ,pos.O_CREAT,initial_value=0)
    S.acquire()  #P(S)

    #On récup le contenu avec nomFichier

    S.release() #V(S)
    S.close()   #!
    FSC.send(contenu,None,pidC)

def main():
    #--- programme serveur: gère les accès concurents entre les modifications et les suppressions.

    signal.signal(signal.SIGINT, fermer_serveur) # SIGINT au Handler fermer_serveur : prévient le SE qu’à l’arrivée du signal ^C il faudra exécuter fermer_programme
    #Initialisation des deux files FCS et FSC 

    #!!! problème potentiel initialisation, si erreur ça detruit puis ça recreer (perte msg?)? quel erreur ?
    # a voir avec le tp ConsMessage, la partie except fait surement n'importe quoi !!!

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
    nomFichier = sys.argv[0]    #récupère le 1er paramètre, le nom du fichier
    nbsecondes = sys.argv[1]    #récupère le 2eme paramètre, le nombre de secondes
    pidServeur = os.getpid()     #On récupère l'id du processus serveur, peut être inutile !

    #La partie qui boucle du serveur 
    while True:
        messageClient = FCS.receive(0)   # 0 car on prend en FIFO, voir "TP UNIX-Python SEANCE 2016v2 tout à la fin"
        #!! receive retourne, selon ce même pdf, un tuple de (message,type), comment récupérer juste le msg ? j'ai mis [0] dans le doute, à tester
        listInfo = messageClient[0].split("/") #ici on split les informations reçu pour les stockés et les utiliser plus tard
        action = listInfo[0]
        pidClient = listInfo[1]
        nomFichier = listInfo[2]
        numEnregistrement = listInfo[3]     #numEnreg peut être "-" parfois
        nouvelEnreg = listInfo[4]     #nouvelEnreg peut être "-" parfois
        
        #New thread(split(3), (split 1 et 2)) /*split 1 et 2 correspondent aux autres infos envoyées comme par exemple le pid ou le numéro d’enregistrement*/

        #On determine la fonction à exécuter en selon l'action demandé par le client
        if action == 'consultation':
                consultation(pidClient,numEnregistrement)
        elif action == 'modification':
                modification(pidClient,numEnregistrement,nouvelEnreg)
        elif action == 'suppression':
                suppression(pidClient,numEnregistrement)
        elif action == 'adjonction':
                adjonction(pidClient,nouvelEnreg)
        elif action == 'visualisation':
                visualisation(pidClient)


serveur = Daemon()
daemon_runner = runner.DaemonRunner(serveur)
daemon_runner.do_action()

#--TODO--

#en faire un daemon -> à tester
    #au besoin : sudo apt-get install python-daemon
    #faire un signal d'arret -> à tester

#regler l'init des files (l'except puis ce qu'il execute m'inquite)
            
#créer les threads
            
#effectuer chaque operation sur fichier
    #j'ai toujours pas compris comment on va s'y prendre avec les enregistrements
            
#s'occuper des sémaphores
    #On utilise close() ou unlink() selon vous ? http://semanchuk.com/philip/posix_ipc/
    #pour leurs création, j'ai mis en parametre O.CREAT uniquement, on s'en fou d'avoir une erreur si la sémaphore existe dèjà, c'est pas comme le tp
    #temps limite a faire avec -d -> à tester
        #nbsecondes int ou float à tester
        #Vous pensez qu'il faut mettre un temps min aussi pour les autres requetes ? genre adjonction pour moi c'est aussi important qu'une modif

#tester tout

#commenter
