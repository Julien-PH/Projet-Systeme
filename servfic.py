#! /usr/bin/env python2.7
# -*- coding: utf8 -*-

import os
import signal
import sys
import thread
import posix_ipc as pos
import time
from daemon import runner
 
#class Deamon():
   # def __init__(self):
        #va falloir peut être le remplir je crois
        #mdr
    #def run(self):
        #main()

#On rÃ©cupÃ¨re les paramÃ¨tres et varables utiles        
nomFichier = sys.argv[1]    #rÃ©cupÃ¨re le 1er paramÃ¨tre, le nom du fichier
nbsecondes = sys.argv[2]    #rÃ©cupÃ¨re le 2eme paramÃ¨tre, le nombre de secondes
pidServeur = os.getpid()     #On rÃ©cupÃ¨re l'id du processus serveur, peut Ãªtre inutile !


#FSC
try:
    FSC = pos.MessageQueue("/queueFSC",pos.O_CREAT)    #crÃ©ation ou ouverture de la file
    print("FSC: Creation/Ouverture de la file de message serveur to client")
except pos.ExistentialError:
    S = pos.unlink_message_queue("/queueFSC") #destruction de la file
    FSC = pos.MessageQueue("/queueFSC",pos.O_CREAT) #puis redemande    

def fermer_serveur(signal, frame):    #Appelé quand vient l'heure de fermer le serveur avec un ^C
    print("Fermeture du serveur")
    sys.exit(0)



def fermer_serveur(signal, frame):    #AppelÃ© quand vient l'heure de fermer le serveur avec un ^C
    print("Fermeture du serveur")
    sys.exit(0)

def consultation(pidC,numEnreg):
    global contenu
    print(pidC)
    try:
        S = pos.Semaphore("/Semaphore_consul",pos.O_CREAT|pos.O_EXCL,initial_value=1)
    except pos.ExistentialError:
        S = pos.Semaphore("/Semaphore_consul",pos.O_CREAT)
    S.acquire()  #P(S) on bloque l'acces au fichier pour les autres threads 
    try:    #on essaye d'ouvrir le fichier
        with open(nomFichier, "r") as fichier:  #with permet d'ouvrir le fichier puis le ferme automatiquement, ici on ouvre le fichier en lecture
            for enregistrement in fichier.readlines():  #on parcourt tout les enregistrement du fichier
        if enregistrement.startswith(numEnreg + ": "):     #On cherche l'enregistrement qui correpond au numero rechercher
                    contenu = enregistrement.strip('\n')    #On rÃ©cup le contenu de l'enregistrement que le client souhaite (sans le saut de ligne)  
    except: #si il y a echec, on le notifi
        contenu = "Le fichier " + nomFichier + " est introuvable ou n'est pas accessible."
    S.release() #V(S) on libÃ¨re le fichier
    S.close()   #!!! on ferme le sÃ©maphore
    print(contenu)
    FSC.send(contenu,None,int(pidC)) #On met dans la file FSC le contenu rechercher pour le client 


def visualisation(pidC):
    try:
        S = pos.Semaphore("/Semaphore_visu" + nomFichier ,pos.O_CREAT,initial_value=1)
    except pos.ExistentialError:
        S = pos.Semaphore("/Semaphore_visu" + nomFichier,pos.O_CREAT)
    S.acquire()  #P(S)
    try:
        with open(nomFichier, "r") as fichier:  #On ouvre le fichier en lecture
            contenu = fichier.read()    #On récupère entierement le contenu du fichier
    except:
        contenu = "Le fichier " + nomFichier + " est introuvable ou n'est pas accessible."   
    S.release() #V(S)
    S.close()   #!
    FSC.send(contenu,None,int(pidC))
    
def modification(pidC,numEnreg,newEnreg):
    try:
        S = pos.Semaphore("/Semaphore_" + nomFichier ,pos.O_CREAT,initial_value=1)
    except pos.ExistentialError:
        S = pos.Semaphore("/Semaphore_" + nomFichier,pos.O_CREAT)
    try:
        Slaps = pos.Semaphore("/Semaphore_laps" + nomFichier ,pos.O_CREAT,initial_value=0)
    except pos.ExistentialError:
        Slaps = pos.Semaphore("/Semaphore_laps" + nomFichier,pos.O_CREAT)
    try:
        Svisu = pos.Semaphore("/Semaphore_visu" + nomFichier ,pos.O_CREAT,initial_value=1)
    except pos.ExistentialError:
        Svisu = pos.Semaphore("/Semaphore_visu" + nomFichier,pos.O_CREAT)   
    try:
        Sadd = pos.Semaphore("/Semaphore_add" + nomFichier ,pos.O_CREAT,initial_value=1)
    except pos.ExistentialError:
        Sadd = pos.Semaphore("/Semaphore_add" + nomFichier,pos.O_CREAT)
    try:
        Sconsul = pos.Semaphore("/Semaphore_consul" + nomFichier ,pos.O_CREAT,initial_value=1)
    except pos.ExistentialError:
        Sconsul = pos.Semaphore("/Semaphore_consul" + nomFichier,pos.O_CREAT) 
    S.acquire()  #P(S) avant de bloquer le fichier, on attend un temps donné maximum au delà du quel on abandonne
    Sconsul.acquire() # on bloque les sémaphores des autres fonctions
    Sadd.acquire()
    Svisu.acquire()
    try:
        with open(nomFichier, "r") as fichier:  #On ouvre le fichier en lecture
            listEnregistrements = fichier.readlines()   #On recupère tout les enregistrements
        try:
            with open(nomFichier, "w") as fichier:  #On ouvre le fichier en ecriture
                for enregistrement in listEnregistrements:
                    if enregistrement.startswith(numEnreg + ": "):
                        contenu = enregistrement.strip('\n')
                        FSC.send(contenu,None,pidC) # envoie du contenu au user
                        #!! msgCons pas initialisé, ça gene en python ?
                        try:
                            Slaps.acquire(nbsecondes) # on attend la réponse de l'utilisateur un temps maximum donnée en parametre du serveur
                            msgCons = FCS.receive(pidClient) #message reçu 
                        except pos.BusyError:   #si le temps d'attente max est dépasser, on notifie l'échec
                            notif = "Le temps d'attente de " + nbsecondes + " secondes est dépassé, modification abandonnée."v
                        if(msgCons == "o" or msgCons == "O"):
                            enregistrement = numEnreg + ":" + newEnreg + "\n"  #On remplace l'enregistrement voulu
                            fichier.write(enregistrement)    #On réécrit chaque enregistrement
                            notif = "Modification effectué sur l'enregistrement numéro " + numEnreg + "."
                        else:
                            notif = "Annulation de l'enregistrement"    
        except:
            notif = "Le fichier " + nomFichier + " est introuvable ou n'est pas accessible."            
    except:
        notif = "Le fichier " + nomFichier + " est introuvable ou n'est pas accessible."
    S.release() #V(S)
    Slaps.close()   #!
    S.close()   #!
    FSC.send(notif,None,pidC)

def suppression(pidC,numEnreg):
    try:
        S = pos.Semaphore("/Semaphore_" + nomFichier ,pos.O_CREAT,initial_value=1)
    except pos.ExistentialError:
        S = pos.Semaphore("/Semaphore_" + nomFichier,pos.O_CREAT)
    try:
        Slaps = pos.Semaphore("/Semaphore_laps" + nomFichier ,pos.O_CREAT,initial_value=1)
    except pos.ExistentialError:
        Slaps = pos.Semaphore("/Semaphore_laps" + nomFichier,pos.O_CREAT)
    try:
        Svisu = pos.Semaphore("/Semaphore_visu" + nomFichier ,pos.O_CREAT,initial_value=1)
    except pos.ExistentialError:
        Svisu = pos.Semaphore("/Semaphore_visu" + nomFichier,pos.O_CREAT)   
    try:
        Sadd = pos.Semaphore("/Semaphore_add" + nomFichier ,pos.O_CREAT,initial_value=1)
    except pos.ExistentialError:
        Sadd = pos.Semaphore("/Semaphore_add" + nomFichier,pos.O_CREAT)
    try:
        Sconsul = pos.Semaphore("/Semaphore_consul" + nomFichier ,pos.O_CREAT,initial_value=1)
    except pos.ExistentialError:
        Sconsul = pos.Semaphore("/Semaphore_consul" + nomFichier,pos.O_CREAT)
    Sconsul.acquire()
    Sadd.acquire()
    Svisu.acquire()      
    try:
        S.acquire(nbsecondes)  #P(S)
        try:
            with open(nomFichier, "r") as fichier:  #On ouvre le fichier en lecture
                listEnregistrements = fichier.readlines()   #On recupère tout les enregistrements
            try:
                with open(nomFichier, "w") as fichier:  #On ouvre le fichier en ecriture
                    for enregistrement in listEnregistrements:
                        if not enregistrement.startswith(numEnreg + ": "):  
                            fichier.write(enregistrement)    #On réécrit chaque enregistrement si ce n'est pas celui qui doit être effacer
                notif = "Suppression effectué sur l'enregistrement numéro " + numEnreg + "."
            except:
                notif = "Le fichier " + nomFichier + " est introuvable ou n'est pas accessible."            
        except:
            notif = "Le fichier " + nomFichier + " est introuvable ou n'est pas accessible."
        S.release() #V(S)
    except:
        notif = "Le temps d'attente de " + nbsecondes + " secondes est dépassé, suppression abandonnée."
    S.close()   #!
    FSC.send(notif,None,pidC)
     
def adjonction(pidC,newEnreg):
    try:
        S = pos.Semaphore("/Semaphore_add" + nomFichier ,pos.O_CREAT,initial_value=1)
    except pos.ExistentialError:
        S = pos.Semaphore("/Semaphore_add" + nomFichier,pos.O_CREAT)
    S.acquire()  #P(S)
    try:
        with open(nomFichier, "a") as fichier:  #On ouvre le fichier en ajout
            #creer newNum !!
            fichier.write(newNum + ": " + newEnreg + "\n")    #On ajoute le nouvel enregistrement au fichier,newNum permet de classer nos enregistrement et "\n" permet de séparé les enregistrements
            notif = "Enregistrement numéro " + newNum + " effectué."
    except:
        notif = "Le fichier " + nomFichier + " est introuvable ou n'est pas accessible."
    
    S.release() #V(S)
    S.close()   #!
    FSC.send(notif,None,pidC)
 


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

    #La partie qui boucle du serveur 
    while True:
        messageClient = FCS.receive()   # 0 car on prend en FIFO, voir "TP UNIX-Python SEANCE 2016v2 tout à la fin"
        #!! receive retourne, selon ce même pdf, un tuple de (message,type), comment récupérer juste le msg ? j'ai mis [0] dans le doute, à tester
        listInfo = messageClient[0].split("/") #ici on split les informations reçu pour les stockés et les utiliser plus tard
        action = listInfo[0]
        pidClient = listInfo[1]
        nomFichier = listInfo[3]
        numEnregistrement = listInfo[4]     #numEnreg peut être "-" parfois
        nouvelEnreg = listInfo[5]     #nouvelEnreg peut être "-" parfois
        
        #On determine la fonction à exécuter en selon l'action demandé par le client
        if action == 'consultation':
               thread.start_new_thread(consultation(pidClient,numEnregistrement))
        elif action == 'modification':
                thread.start_new_thread(modification(pidClient,numEnregistrement,nouvelEnreg))
        elif action == 'suppression':
                thread.start_new_thread(suppression(pidClient,numEnregistrement))
        elif action == 'adjonction':
                thread.start_new_thread(adjonction(pidClient,nouvelEnreg))
        elif action == 'visualisation':
                thread.start_new_thread(visualisation,(pidClient,))

#on lance le daemon, main etant dans le run de ce dernier
#serveur = Daemon()
#daemon_runner = runner.DaemonRunner(serveur)
#daemon_runner.do_action()

#sinon si ça marche pas avec le daemon :
main()



#--TODO--

#en faire un daemon -> à tester (serieux ça a l'air chaud)
    #au besoin : sudo apt-get install python-daemon
    #faire un signal d'arret -> à tester

#regler l'init des files (l'except puis ce qu'il execute m'inquite)
    #faut t'il aussi les detruire si on tue le serveur ?

#créer les threads (j'ai regardé des tutos, même genre de bourbier que le deamon, testons le deamon avant de faire les thread sinon ça marchera jamais.)
    # j'ai pas lu mais voilà le lien de la prof : https://www.python-course.eu/advanced_topics.php
    
#effectuer chaque operation sur fichier -> à tester
    #garder en tête que la reception de message est douteuse, voir mon commentaire en debut de boucle true du serveur
            
#s'occuper des sémaphores -> à tester
    #On utilise close() ou unlink() selon vous ? http://semanchuk.com/philip/posix_ipc/
    #pour leurs création, j'ai mis en parametre O.CREAT uniquement, on s'en fou d'avoir une erreur si la sémaphore existe dèjà, c'est pas comme le tp
        #les try/except sur chaque creation sont INUTILE
    #temps limite a faire avec -d -> à tester
        #nbsecondes int ou float à tester
        #Vous pensez qu'il faut mettre un temps min aussi pour les autres requetes ? genre adjonction pour moi c'est aussi important qu'une modif
    #le nom du semaphore Slaps doit etre None, le SE chosira un nom arbitraire et on supprime ça (unlink) ensuite, personne d'autre doit pourvoir utiliser le meme sémaphore pour chronometré
        
#tester tout

#commenter
