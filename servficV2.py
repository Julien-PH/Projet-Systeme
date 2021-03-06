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
    
#On récupère les paramètres et varables utiles        
nomFichier = sys.argv[1]    #récupère le 1er paramètre, le nom du fichier
nbsecondes = sys.argv[2]    #récupère le 2eme paramètre, le nombre de secondes
pidServeur = os.getpid()     #On récupère l'id du processus serveur, peut être inutile !


#FSC
try:
    FSC = pos.MessageQueue("/queueFSC",pos.O_CREAT)    #création ou ouverture de la file
    print("FSC: Creation/Ouverture de la file de message serveur to client")
except pos.ExistentialError:
    S = pos.unlink_message_queue("/queueFSC") #destruction de la file
    FSC = pos.MessageQueue("/queueFSC",pos.O_CREAT) #puis redemande

def fermer_serveur(signal, frame):    #Appelé quand vient l'heure de fermer le serveur avec un ^C
    print("Fermeture du serveur")
    sys.exit(0)

def ouvrirFileServeurToClient(pidC,nomFichier):
    FStoC = pos.MessageQueue("/queue-" + pidC + "-" + nomFichier,pos.O_CREAT)    #création ou ouverture de la file de serveur vers client, une file par client et par fichier

def tempsAttente():
    #print("1")
    try:
        Slaps= pos.Semaphore("/Semaphore_laps",pos.O_CREAT|pos.O_EXCL,initial_value=0)
    except pos.ExistentialError:
        Slaps= pos.Semaphore("/Semaphore_laps",pos.O_CREAT)
    try:
        Slaps.acquire(4)
        FSC.send("ok")
    except pos.BusyError:
	print("Le temps d'attente est depasse votre requete va etre annule")
	Slaps.acquire()
        FSC.send("pas ok")

def consultation(pidC,numEnreg):
    global contenu
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
    S.release() #V(S) on libère le fichier
    S.close()   #!!! on ferme le sémaphore

    ouvrirFileServeurToClient(pidC,nomFichier)
    FStoC.send(contenu,None,int(pidC))
    #FSC.send(contenu,None,int(pidC)) #On met dans la file FSC le contenu rechercher pour le client
    

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
    S.close()

    ouvrirFileServeurToClient(pidC,nomFichier)
    FStoC.send(contenu,None,int(pidC))
    #FSC.send(contenu,None,int(pidC)) 
    
def modification(pidC,numEnreg,newEnreg):
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
    S.acquire()
    try:
        with open(nomFichier, "r") as fichier:
            listEnregistrements = fichier.readlines()
        try:
            with open(nomFichier, "w") as fichier:
                for enregistrement in listEnregistrements:
                    if enregistrement.startswith(numEnreg + ": "):
			enregistrement = numEnreg + ": " + newEnreg + "\n"
                    fichier.write(enregistrement)
                notif = "Modification effectue sur l'enregistrement numero " + numEnreg + "."	               
	except:
              notif = "Le fichier " + nomFichier + " est introuvable ou n'est pas accessible."            
    except:
           notif = "Le fichier " + nomFichier + " est introuvable ou nest pas accessible."
    S.release() #V(S)
    S.close()
    Sconsul.release() #V(S)
    Sconsul.close()
    Sadd.release() #V(S)
    Sadd.close()
    Svisu.release() #V(S)
    Svisu.close()

    ouvrirFileServeurToClient(pidC,nomFichier)
    FStoC.send(contenu,None,int(pidC))
    #FSC.send(notif,None,int(pidC))

def suppression(pidC,numEnreg):
    try:
        S = pos.Semaphore("/Semaphore_" + nomFichier ,pos.O_CREAT,initial_value=1)
    except pos.ExistentialError:
        S = pos.Semaphore("/Semaphore_" + nomFichier,pos.O_CREAT)
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
    S.acquire()
    #print(nbsecondes)
    #try:
        #S.acquire(int(nbsecondes))  #P(S)
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
    #except:
        #notif = "Le temps d'attente de " + nbsecondes + " secondes est depasse, suppression abandonnee."
    S.close()   #!
    Sconsul.release() #V(S)
    Sconsul.close()
    Sadd.release() #V(S)
    Sadd.close()
    Svisu.release() #V(S)
    Svisu.close()

    ouvrirFileServeurToClient(pidC,nomFichier)
    FStoC.send(contenu,None,int(pidC))
    #FSC.send(notif,None,int(pidC))
     
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
            fichier.write(str(newNum) + ": " + newEnreg + "\n")    #On ajoute le nouvel enregistrement au fichier,newNum permet de classer nos enregistrement et "\n" permet de séparé les enregistrements
            notif = "Enregistrement numero " + str(newNum) + " effectue."
    except:
        notif = "Le fichier " + nomFichier + " est introuvable ou n'est pas accessible."
    print("1")
    print(pidC)
    S.release() #V(S)
    S.close()   #!

    ouvrirFileServeurToClient(pidC,nomFichier)
    FStoC.send(contenu,None,int(pidC))
    #FSC.send(notif,None,int(pidC))
 

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

    
	
    ouvertureServ=True
    #La partie qui boucle du serveur 
    while ouvertureServ:
        try:
	    messageClient = FCS.receive()   # 0 car on prend en FIFO, voir "TP UNIX-Python SEANCE 2016v2 tout à la fin"
            #!! receive retourne, selon ce même pdf, un tuple de (message,type), comment récupérer juste le msg ? j'ai mis [0] dans le doute, à tester
            listInfo = messageClient[0].split("/") #ici on split les informations reçu pour les stockés et les utiliser plus tard
            action = listInfo[0]
            pidClient = listInfo[1]
            nomFichier = listInfo[3]
            numEnregistrement = listInfo[4]     #numEnreg peut être "-" parfois
            nouvelEnreg = listInfo[5]     #nouvelEnreg peut être "-" parfois
        
            #New thread(split(3), (split 1 et 2)) /*split 1 et 2 correspondent aux autres infos envoyées comme par exemple le pid ou le numéro d’enregistrement*/

            #On determine la fonction à exécuter en selon l'action demandé par le client
            if action == 'consultation':
               thread.start_new_thread(consultation,(pidClient,numEnregistrement))
            elif action == 'modification':
                thread.start_new_thread(modification,(pidClient,numEnregistrement,nouvelEnreg))
            elif action == 'suppression':
                thread.start_new_thread(suppression,(pidClient,numEnregistrement))
            elif action == 'adjonction':
                thread.start_new_thread(adjonction,(pidClient,nouvelEnreg))
            elif action == 'visualisation':
                thread.start_new_thread(visualisation,(pidClient,))
	    elif action == 'tempsAttente':
		tempsAttente()
	except pos.SignalError:
	    ouvertureServ=False
	#except pos.BusyError:
	    #print("Delai d'attente depasse")
	    #print("Fermeture serveur")

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
    #temps limite a faire avec -d -> à tester
        #nbsecondes int ou float à tester
        #Vous pensez qu'il faut mettre un temps min aussi pour les autres requetes ? genre adjonction pour moi c'est aussi important qu'une modif

#tester tout

#commenter
