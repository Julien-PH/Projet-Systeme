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
        #va falloir peut Ãªtre le remplir je crois
        #mdr
    #def run(self):
        #main()
    
def init():
    #Initialisation des deux files FCS et FSC 

    #!!! problÃ¨me potentiel initialisation, si erreur Ã§a detruit puis Ã§a recreer (perte msg?)? quel erreur ?
    # a voir avec le tp ConsMessage, la partie except fait surement n'importe quoi !!!

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
    nomFichier = sys.argv[1]    #rÃ©cupÃ¨re le 1er paramÃ¨tre, le nom du fichier
    nbsecondes = sys.argv[2]    #rÃ©cupÃ¨re le 2eme paramÃ¨tre, le nombre de secondes
    pidServeur = os.getpid()     #On rÃ©cupÃ¨re l'id du processus serveur, peut Ãªtre inutile !
    
def fermer_serveur(signal, frame):    #AppelÃ© quand vient l'heure de fermer le serveur avec un ^C
    print("Fermeture du serveur")
    sys.exit(0)

def consultation(pidC,numEnreg):
    global contenu  #utile ?
    find=False
    try:
        S = pos.Semaphore("/Semaphore_consul",pos.O_CREAT|pos.O_EXCL,initial_value=1)
    except pos.ExistentialError:
        S = pos.Semaphore("/Semaphore_consul",pos.O_CREAT)
    S.acquire()  #P(S) on bloque l'acces au fichier pour les autres threads
    try:    #on essaye d'ouvrir le fichier
        with open(nomFichier, "r") as fichier:  #with permet d'ouvrir le fichier puis le ferme automatiquement, ici on ouvre le fichier en lecture
            for enregistrement in fichier.readlines():  #on parcourt tout les enregistrement du fichier
                if enregistrement.startswith(numEnreg + ": "):     #On cherche l'enregistrement qui correpond au numero rechercher
                      find = True
                      contenu = enregistrement.strip('\n')     
            if find == False:
                contenu = "l'enregistrement que vous cherchez n'existe pas"         
    except: #si il y a echec, on le notifi
        contenu = "Le fichier " + nomFichier + " est introuvable ou n'est pas accessible."
    S.release() #V(S) on libÃ¨re le fichier
    S.close()   #!!! on ferme le sÃ©maphore
    FSC.send(contenu,None,1) #On met dans la file FSC le contenu rechercher pour le client

def visualisation(pidC):
    try:
        S = pos.Semaphore("/Semaphore_visu" + nomFichier ,pos.O_CREAT,initial_value=1)
    except pos.ExistentialError:
        S = pos.Semaphore("/Semaphore_visu" + nomFichier,pos.O_CREAT)
    S.acquire()  #P(S)
    try:
        with open(nomFichier, "r") as fichier:  #On ouvre le fichier en lecture
            contenu = fichier.read()    #On rÃ©cupÃ¨re entierement le contenu du fichier
    except:
        contenu = "Le fichier " + nomFichier + " est introuvable ou n'est pas accessible."   
    S.release() #V(S)
    S.close()  
    FSC.send(contenu,None,1) 
    
def modification(pidC,numEnreg):
    S = pos.Semaphore("/Semaphore_" + nomFichier ,pos.O_CREAT,initial_value=1)
    Svisu = pos.Semaphore("/Semaphore_visu" + nomFichier ,pos.O_CREAT,initial_value=1)
    Sadd = pos.Semaphore("/Semaphore_add" + nomFichier ,pos.O_CREAT,initial_value=1)
    Sconsul = pos.Semaphore("/Semaphore_consul" + nomFichier ,pos.O_CREAT,initial_value=1)

    S.acquire()
    Svisu.acquire()
    Sadd.acquire()
    Sconsul.acquire()
    
    try:
        with open(nomFichier, "r") as fichier:  #On ouvre le fichier en lecture
            listEnregistrements = fichier.readlines()   #On recupÃ¨re tout les enregistrements
        try:
            with open(nomFichier, "w") as fichier:  #On ouvre le fichier en ecriture
                for enregistrement in listEnregistrements:
                    if enregistrement.startswith(numEnreg + ": "):
                        contenu = enregistrement.strip('\n')
                        FSC.send(contenu,None,2)
                        try:
                            newEnreg = FCS.receive(int(nbsecondes))
                            enregistrement = numEnreg + ": " + newEnreg + "\n"  #On remplace l'enregistrement voulu
                            notif = "Modification effectue sur l'enregistrement numero " + numEnreg + "."
                        except pos.BusyError:
                            notif = ""
                            print("Le temps d'attente de " + nbsecondes + " secondes est dÃ©passÃ©, modification abandonnÃ©e.")
                    fichier.write(enregistrement)   #On reecrit chaque enregistrement
        except:
            notif = "Le fichier " + nomFichier + " est introuvable ou n'est pas accessible."            
    except:
        notif = "Le fichier " + nomFichier + " est introuvable ou n'est pas accessible."

    S.release() #V(S)
    Svisu.release()
    Sadd.release()
    Sconsul.release()

    S.close()
    Svisu.close()
    Sadd.close()
    Sconsul.close()

    if not notif == "":
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
    print(nbsecondes)
    try:
        S.acquire(int(nbsecondes))  #P(S)
        try:
            with open(nomFichier, "r") as fichier:
                listEnregistrements = fichier.readlines()
            try:
                with open(nomFichier, "w") as fichier:
                    for enregistrement in listEnregistrements:
                        if not enregistrement.startswith(numEnreg + ": "):
                numEnr,newEnregis=enregistrement.split(":")
                if numEnr>numEnreg:
                    numEnr=int(numEnr)-1
                    #print(numEnr)
                    #print(newEnregis)
                            fichier.write(str(numEnr)+": "+newEnregis)
                notif = "Suppression effectue sur l'enregistrement numero " + numEnreg + "."
            except:
                notif = "Le fichier " + nomFichier + " est introuvable ou n'est pas accessible."            
        except:
            notif = "Le fichier " + nomFichier + " est introuvable ou nest pas accessible."
        S.release() #V(S)
    except:
        notif = "Le temps d'attente de " + nbsecondes + " secondes est depasse, suppression abandonnee."
    S.close()   #!
    Sconsul.release() #V(S)
    Sconsul.close()
    Sadd.release() #V(S)
    Sadd.close()
    Svisu.release() #V(S)
    Svisu.close()
    FSC.send(notif,None,int(pidC))
     
def adjonction(pidC,newEnreg):
    newNum=1
    try:
        S = pos.Semaphore("/SemaphoreAdd" + nomFichier ,pos.O_CREAT|pos.O_EXCL,initial_value=1)
    except pos.ExistentialError:
        S = pos.Semaphore("/SemaphoreAdd" + nomFichier,pos.O_CREAT)
    print(nomFichier)
    S.acquire()  #P(S)
    print("adj")
    try:    #on essaye d'ouvrir le fichier
        with open(nomFichier, "r") as fichier:  #with permet d'ouvrir le fichier puis le ferme automatiquement, ici on ouvre le fichier en lecture
            for enregistrement in fichier.readlines():  #on parcourt tout les enregistrement du fichier
                newNum = newNum + 1
    except: #si il y a echec, on le notifi
        contenu = "Le fichier " + nomFichier + " est introuvable ou n'est pas accessible."    
    try:
    with open(nomFichier,"a") as fichier:  #On ouvre le fichier en ajout
            fichier.write(str(newNum) + ": " + newEnreg + "\n")    #On ajoute le nouvel enregistrement au fichier,newNum permet de classer nos enregistrement et "\n" permet de sÃ©parÃ© les enregistrements
            notif = "Enregistrement numero " + str(newNum) + " effectue."
    except:
        notif = "Le fichier " + nomFichier + " est introuvable ou n'est pas accessible."
    print("1")
    print(pidC)
    S.release() #V(S)
    S.close()   #!
    FSC.send(notif,None,int(pidC))
 


def main():
    #--- programme serveur: gÃ¨re les accÃ¨s concurents entre les modifications et les suppressions.

    signal.signal(signal.SIGINT, fermer_serveur) # SIGINT au Handler fermer_serveur : prÃ©vient le SE quâ€™Ã  lâ€™arrivÃ©e du signal ^C il faudra exÃ©cuter fermer_programme
    
    init()  #on init les variables globales et les files

    #La partie qui boucle du serveur 
    while True:
        try:
            messageClient = FCS.receive(60)   # 60 car on attent une minute l'arrivé d'un msg si la liste est vide   
            #!! receive retourne, selon ce mÃªme pdf, un tuple de (message,type), comment rÃ©cupÃ©rer juste le msg ? j'ai mis [0] dans le doute, Ã  tester
            listInfo = messageClient[0].split("/") #ici on split les informations reÃ§u pour les stockÃ©s et les utiliser plus tard
            action = listInfo[0]
            pidClient = listInfo[1]
            nomFichier = listInfo[3]
            numEnregistrement = listInfo[4]     #numEnreg peut Ãªtre "-" parfois
            nouvelEnreg = listInfo[5]     #nouvelEnreg peut Ãªtre "-" parfois
            
            #On determine la fonction Ã  exÃ©cuter en selon l'action demandÃ© par le client
            if action == 'consultation':
                   thread.start_new_thread(consultation,(pidClient,numEnregistrement))
            elif action == 'modification':
                    thread.start_new_thread(modification,(pidClient,numEnregistrement))
            elif action == 'suppression':
                    thread.start_new_thread(suppression,(pidClient,numEnregistrement))
            elif action == 'adjonction':
                    thread.start_new_thread(adjonction,(pidClient,nouvelEnreg))
            elif action == 'visualisation':
                    thread.start_new_thread(visualisation,(pidClient))
        except pos.BusyError:
            print("En attente") #je precise l'attente

#on lance le daemon, main etant dans le run de ce dernier
#serveur = Daemon()
#daemon_runner = runner.DaemonRunner(serveur)
#daemon_runner.do_action()

#sinon si Ã§a marche pas avec le daemon :
main()



#--TODO--

#regler le problème où le fichier est different entre le client et le serveur

#a revoir la syntaxe des send, les send de réponse a l'interieur de modif et suppr en particulier

#en faire un daemon -> Ã  tester (serieux Ã§a a l'air chaud)
    #au besoin : sudo apt-get install python-daemon
    #faire un signal d'arret -> Ã  tester

#regler l'init des files (l'except puis ce qu'il execute m'inquite)
    #faut t'il aussi les detruire si on tue le serveur ?

#crÃ©er les threads (j'ai regardÃ© des tutos, mÃªme genre de bourbier que le deamon, testons le deamon avant de faire les thread sinon Ã§a marchera jamais.)
    # j'ai pas lu mais voilÃ  le lien de la prof : https://www.python-course.eu/advanced_topics.php      
#effectuer chaque operation sur fichier -> Ã  tester
    #garder en tÃªte que la reception de message est douteuse, voir mon commentaire en debut de boucle true du serveur
            
#s'occuper des sÃ©maphores -> Ã  tester
    #On utilise close() ou unlink() selon vous ? http://semanchuk.com/philip/posix_ipc/
    #pour leurs crÃ©ation, j'ai mis en parametre O.CREAT uniquement, on s'en fou d'avoir une erreur si la sÃ©maphore existe dÃ¨jÃ , c'est pas comme le tp
    #temps limite a faire avec -d -> Ã  tester
        #nbsecondes int ou float Ã  tester
        #Vous pensez qu'il faut mettre un temps min aussi pour les autres requetes ? genre adjonction pour moi c'est aussi important qu'une modif

#tester tout

#commenter
