#! /usr/bin/env python2.7
# -*- coding: utf8 -*-

import os
import signal
import sys
import thread
import posix_ipc as pos
import time

    
#On récupère les paramètres et varables utiles        
nomFichier = sys.argv[2]    #récupère le 1er paramètre, le nom du fichier
nbsecondes = sys.argv[4]    #récupère le 2eme paramètre, le nombre de secondes
pidServeur = os.getpid()     #On récupère l'id du processus serveur, peut être inutile !

try:
    Ssupp = pos.Semaphore("/Semaphore_supp" + nomFichier ,pos.O_CREAT,initial_value=1)
except pos.ExistentialError:
    Ssupp = pos.Semaphore("/Semaphore_supp" + nomFichier,pos.O_CREAT)
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
try:
    Smodif = pos.Semaphore("/Semaphore_modif" + nomFichier ,pos.O_CREAT,initial_value=1)
except pos.ExistentialError:
    Smodif = pos.Semaphore("/Semaphore_modif" + nomFichier,pos.O_CREAT)

def fermer_serveur(signal, frame):    #Appelé quand vient l'heure de fermer le serveur avec un ^C
    print("\nFermeture du serveur")
    sys.exit(0)


def cherchefichier(fichier, rep):
 
    entrees = os.listdir(rep)

    for entree in entrees:
        if (not os.path.isdir(os.path.join(rep, entree))) and (entree==fichier):
            return rep
 
  
    for entree in entrees:
        rep2 = os.path.join(rep, entree)
        if os.path.isdir(rep2):
            chemin = cherchefichier(fichier, rep2)
            if chemin!="":
                return chemin
 
    return ""

def tempsAttente(pidC):
    try:
        FSC = pos.MessageQueue("/queueFSC"+str(pidC),pos.O_CREAT)    #création ou ouverture de la file
        #print("FSC: Creation/Ouverture de la file de message serveur to client")
    except pos.ExistentialError:
        S = pos.unlink_message_queue("/queueFSC"+str(pidC)) #destruction de la file
        FSC = pos.MessageQueue("/queueFSC"+str(pidC),pos.O_CREAT) #puis redemande
    try:
        Slaps= pos.Semaphore("/Semaphore_laps",pos.O_CREAT|pos.O_EXCL,initial_value=0)
    except pos.ExistentialError:
        Slaps= pos.Semaphore("/Semaphore_laps",pos.O_CREAT)
    try:
        Slaps.acquire(int(nbsecondes))
        FSC.send("ok")
    except pos.BusyError:
	#print("\nLe temps d'attente est depasse votre requete va etre annule")
        FSC.send("pas ok")

def consultation(pidC,numEnreg):
    try:
        FSC = pos.MessageQueue("/queueFSC"+str(pidC),pos.O_CREAT)    #création ou ouverture de la file
        #print("FSC: Creation/Ouverture de la file de message serveur to client")
    except pos.ExistentialError:
        S = pos.unlink_message_queue("/queueFSC"+str(pidC)) #destruction de la file
        FSC = pos.MessageQueue("/queueFSC"+str(pidC),pos.O_CREAT) #puis redemande
    global contenu
    find=False
    Sconsul.acquire()  #P(S) on bloque l'acces au fichier pour les autres threads
    rep = u"/"
    fichier = u"fichier.txt"
    chemin = cherchefichier(fichier,rep)
    b=chemin [0:-1]
    if b != '/':
	chemin =chemin +'/'
    cheminObs = chemin + nomFichier 
    try:    #on essaye d'ouvrir le fichier
        with open(cheminObs, "r") as fichier:  #with permet d'ouvrir le fichier puis le ferme automatiquement, ici on ouvre le fichier en lecture
            for enregistrement in fichier.readlines():  #on parcourt tout les enregistrement du fichier
		if enregistrement.startswith(numEnreg + ": "):     #On cherche l'enregistrement qui correpond au numero rechercher
                      find = True
		      contenu = enregistrement.strip('\n')     
    	    if find == False:
                    contenu = "l'enregistrement que vous cherchez n'existe pas"	    	
    except: #si il y a echec, on le notifi
        contenu = "Le fichier " + nomFichier + " est introuvable ou n'est pas accessible."
    Sconsul.release() #V(S) on libère le fichier    
    FSC.send(contenu,None,int(pidC)) #On met dans la file FSC le contenu rechercher pour le client
   	
def visualisation(pidC):
    try:
        FSC = pos.MessageQueue("/queueFSC"+str(pidC),pos.O_CREAT)    #création ou ouverture de la file
        #print("FSC: Creation/Ouverture de la file de message serveur to client")
    except pos.ExistentialError:
        S = pos.unlink_message_queue("/queueFSC"+str(pidC)) #destruction de la file
        FSC = pos.MessageQueue("/queueFSC"+str(pidC),pos.O_CREAT) #puis redemande
    Svisu.acquire()  #P(S)
    try:
        with open(nomFichier, "r") as fichier:  #On ouvre le fichier en lecture
            contenu = fichier.read()    #On récupère entierement le contenu du fichier
    except:
        contenu = "Le fichier " + nomFichier + " est introuvable ou n'est pas accessible."   
    Svisu.release() #V(S)
    FSC.send(contenu,None,int(pidC))
    
def modification(pidC,numEnreg,newEnreg):
    try:
        FSC = pos.MessageQueue("/queueFSC"+str(pidC),pos.O_CREAT)    #création ou ouverture de la file
        #print("FSC: Creation/Ouverture de la file de message serveur to client")
    except pos.ExistentialError:
        S = pos.unlink_message_queue("/queueFSC"+str(pidC)) #destruction de la file
        FSC = pos.MessageQueue("/queueFSC"+str(pidC),pos.O_CREAT) #puis redemande
    Smodif.acquire()
    Sconsul.acquire()
    Sadd.acquire()
    Svisu.acquire()
    Ssupp.acquire()
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
    Smodif.release()
    Ssupp.release() #V(S)
    Sconsul.release() #V(S)
    Sadd.release() #V(S)
    Svisu.release() #V(S)
    FSC.send(notif,None,int(pidC))

def suppression(pidC,numEnreg):
    try:
        FSC = pos.MessageQueue("/queueFSC"+str(pidC),pos.O_CREAT)    #création ou ouverture de la file
        #print("FSC: Creation/Ouverture de la file de message serveur to client")
    except pos.ExistentialError:
        S = pos.unlink_message_queue("/queueFSC"+str(pidC)) #destruction de la file
        FSC = pos.MessageQueue("/queueFSC"+str(pidC),pos.O_CREAT) #puis redemande
    Ssupp.acquire()
    Sconsul.acquire()
    Sadd.acquire()
    Svisu.acquire()
    Smodif.acquire()
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
                       fichier.write(str(numEnr)+":"+newEnregis)
                    notif = "Suppression effectue sur l'enregistrement numero " + numEnreg + "."
        except:
              notif = "Le fichier " + nomFichier + " est introuvable ou n'est pas accessible."            
    except:
           notif = "Le fichier " + nomFichier + " est introuvable ou nest pas accessible."
    Ssupp.release() #V(S)
    Smodif.release()
    Sconsul.release() #V(S)
    Sadd.release() #V(S)
    Svisu.release() #V(S)
    FSC.send(notif,None,int(pidC))

     
def adjonction(pidC,newEnreg):
    try:
        FSC = pos.MessageQueue("/queueFSC"+str(pidC),pos.O_CREAT)    #création ou ouverture de la file
        #print("FSC: Creation/Ouverture de la file de message serveur to client")
    except pos.ExistentialError:
        S = pos.unlink_message_queue("/queueFSC"+str(pidC)) #destruction de la file
        FSC = pos.MessageQueue("/queueFSC"+str(pidC),pos.O_CREAT) #puis redemande
    newNum=1
    Sadd.acquire()  #P(S)
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
    Sadd.release() #V(S)
    FSC.send(notif,None,int(pidC))

def main():
    global nomFichier
    #--- programme serveur: gère les accès concurents entre les modifications et les suppressions.

    signal.signal(signal.SIGINT, fermer_serveur) # SIGINT au Handler fermer_serveur : prévient le SE qu’à l’arrivée du signal ^C il faudra exécuter fermer_programme

    #FCS
    try:
        FCS = pos.MessageQueue("/queueFCS"+nomFichier,pos.O_CREAT)    #création ou ouverture de la file
        #print("FCS: Creation/Ouverture de la file de message client to serveur")
    except pos.ExistentialError:
        S = pos.unlink_message_queue("/queueFCS"+nomFichier) #destruction de la file
        FCS = pos.MessageQueue("/queueFCS"+nomFichier,pos.O_CREAT) #puis redemande
	
    ouvertureServ=True
    #La partie qui boucle du serveur 
    while ouvertureServ:
        try:
	    messageClient = FCS.receive()
            listInfo = messageClient[0].split("/") #ici on split les informations reçu pour les stockés et les utiliser plus tard
            action = listInfo[0]
            pidClient = listInfo[1]
            nomFichier = listInfo[2]
            numEnregistrement = listInfo[3] 
            nouvelEnreg = listInfo[4]    

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
		tempsAttente(pidClient)
	except pos.SignalError:
	    ouvertureServ=False
main()
