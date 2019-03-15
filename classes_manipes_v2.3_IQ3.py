from os import getcwd,chdir,listdir
from tkinter import *

class Experiment(object):
    # L'objet Experiment recueille toutes les informations concernant une expérience sur une lamelle.
    def __init__(self):
        from os import getcwd,listdir
        self.path=getcwd()
        self.date=StringVar()
        self.passage=IntVar()
        self.lamelle=IntVar()
        self.strain=IntVar()
        self.time=StringVar()
        self.cells=[]

    def get_times(self):
        # Cette fonction récupère la liste des temps auxquelles ont été prises les images dans les noms des fichiers.
        # Les fichiers doivent etre préalablement traités pour être de la forme : "lorraine_zoneN_hhmmss *M.tif"
        self.liste_dir=listdir() # contient la liste de tous les fichiers indiqués dans le dossier actif
        self.zones={} # dictionnaire contenant la liste non ordonnées de tous les objets de type Zone créés pour recueillir les données
        zone_prec=""
        for fichier in self.liste_dir:
            # On parcourt l'intégralité des fichiers dans le dossier actif
            
            fichier_split=fichier.split("_")# contient sous forme de liste les morceaux de noms de fichiers séparés par "_"
            
            if len(fichier_split)>2:
                # On néglige tous les fichiers qui ne sont pas segmentés comme on l'attend
                if ".tif" in fichier_split[2]:
                    # Les fichiers de métadonnées ont des noms presque identiques, pour ne pas compter tout deux fois on ne prend que les images
                    time_split=fichier_split[2].split(".")# La dernière partie du nom contient l'information de l'heure
                    
                    time_raw=time_split[0]
                    # Il faut extraire cette série de chiffres pour l'afficher au format ISO
                    if fichier_split[1]!=zone_prec :
                        #Si le fichier correspond à une zone jamais observée, il faut créer un nouvel objet Zone
                        self.zones[fichier_split[1]]=Zone(fichier_split[1]) # La clé du dictionnaire self.zones est une chaîne de caractères au format "zoneN"
                        zone_prec=fichier_split[1]
                    time=time_raw[0:2]+":"+time_raw[2:4]+":"+time_raw[4:6]
##                    if len(time_raw)==5:
##                        # L'heure peut contenir 5 ou 6 caractères selon que l'heure est avant ou après 10h
##                        # Cette boucle convertit l'heure américaine en heure ISO
##                        if ("PM"  in time_split[1]):
##                            time=str(int(time_raw[0])+12)+":"+time_raw[1:3]+":"+time_raw[3:5]
##                        else :
##                            time="0"+time_raw[0:1]+":"+time_raw[1:3]+":"+time_raw[3:5]
##                    else :
##                        if ("PM" in time_split[1]):
##                            if (int(time_raw[0:2])<12):
##                                time=str(int(time_raw[0:2])+12)+":"+time_raw[2:4]+":"+time_raw[4:6]
##                            else :
##                                time=time_raw[0:2]+":"+time_raw[2:4]+":"+time_raw[4:6]
##                        else :
##                            time=time_raw[0:2]+":"+time_raw[2:4]+":"+time_raw[4:6]
                        
                    self.zones[fichier_split[1]].times.append(time) # Le temps en chaine de caractères "hh-mm" est ajoutée à la liste Zone.times
                    

class Zone(object):
    # L'objet Zone contient tous les paramètres communs à une Zone d'une expérience, en particulier la liste des temps dans self.times .
    # Cette liste des temps doit être obtenue à l'aide de la méthode get_times d'un objet Experiment.
    def __init__(self,name):
        self.times=[]
        self.nbcell=IntVar()
        self.nbGFPcell=IntVar()
        self.nbtranscell=IntVar()
        self.name=name
        
class Cellule(object):
    # L'objet Cellule contient tous les paramètres d'une Cellule d'une Zone, en particulier la liste des états aux temps de la liste Zone.times
    def __init__(self,zone):
        self.etat=[]
        self.transloc=[]
        self.MCherry=BooleanVar()
        self.MCherry.set(False)
        self.taille=0

class Base_frame(Frame):
    # Fenêtre de base de l'application, demandant le nom du dossier de l'expérience à traiter.
    def __init__(self,boss=None):
        Frame.__init__(self)
        Label(self,text="Entrer le chemin du dossier de l'expérience").grid(row=0,column=0)
        self.entree=Entry(self,width=30)
        self.entree.grid(row=1,column=0)
        Button(self,text="Nouvelle Expérience",command=self.new_exp).grid(row=3,column=1)
        Button(self,text="Nouvel état initial",command=self.new_initialstate).grid(row=4,column=1)
        Button(self,text="Renommer les fichiers",command=self.rename).grid(row=2,column=1)
        
    def new_exp(self):
        # Fonction créant une nouvelle fenêtre Exp_Frame
        from os import chdir
        path=self.entree.get()
        print(path)
        chdir(path) # On définit comme dossier actif le chemin défini par l'utilisateur, afin d'y utiliser get_times
        self.ExpFrame=Exp_Frame()
        n=len(path.split("\\"))
        self.ExpFrame.exp.date.set(path.split("\\")[n-2])# La date de l'expérience peut être récupérée à partir d'un nom de dossier dans le chemin
        self.ExpFrame.title(path.split("\\")[n-1])
    def new_initialstate(self):
        self.ISFrame=IS_Frame()
        path=self.entree.get()
        n=len(path.split("\\"))
        self.ISFrame.date.set(path.split("\\")[n-2])
    def rename(self):
        from os import chdir,listdir,rename
        dossier=self.entree.get()
        chdir(dossier)
        liste_fichiers=listdir()
        check=False

        for image in liste_fichiers:
            image_split=image.split("_")
            if (len(image_split)>3):
                    del image_split[2]
                    check=True
            sep="_"
            new_image=sep.join(image_split)
            rename(image,new_image)
            print(image,sep="\n")

        for fichier in liste_fichiers:
                        # On parcourt l'intégralité des fichiers dans le dossier actif
            fichier_split=fichier.split("_")# contient sous forme de liste les morceaux de noms de fichiers séparés par "_"
            
            if len(fichier_split)>2 :
                # On néglige tous les fichiers qui ne sont pas segmentés comme on l'attend
                if ".tif" in fichier_split[2]:
                    # Les fichiers de métadonnées ont des noms presque identiques, pour ne pas compter tout deux fois on ne prend que les images
                    time_split=fichier_split[2].split(" ")# La dernière partie du nom contient l'information de l'heure
                    time_raw=time_split[0]
                    # Il faut extraire cette série de chiffres pour l'afficher au format ISO
                    if len(time_raw)==5:
                        # L'heure peut contenir 5 ou 6 caractères selon que l'heure est avant ou après 10h
                        # Cette boucle convertit l'heure américaine en heure ISO
                        if ("PM"  in time_split[1]):
                            time=str(int(time_raw[0])+12)+":"+time_raw[1:3]+":"+time_raw[3:5]
                        else :
                            time="0"+time_raw[0:1]+":"+time_raw[1:3]+":"+time_raw[3:5]
                    else :
                        if ("PM" in time_split[1]):
                            if (int(time_raw[0:2])<12):
                                time=str(int(time_raw[0:2])+12)+":"+time_raw[2:4]+":"+time_raw[4:6]
                            else :
                                time=time_raw[0:2]+":"+time_raw[2:4]+":"+time_raw[4:6]
                        else :
                            time=time_raw[0:2]+":"+time_raw[2:4]+":"+time_raw[4:6]
                    time_split2=time.split(":")
                    sep="-"
                    time=sep.join(time_split2)
                    print(time)
                    rename(fichier,fichier_split[0]+"_"+fichier_split[1]+'_'+time+".tif")
                    

            
        
        

class Exp_Frame(Toplevel):
    # Exp_Frame est une fenêtre indépendante de Base_Frame
    def __init__(self,boss=None):
        Toplevel.__init__(self)
        #Définition des paramètres, champs et boutons de l'interface graphique
        self.bind("<Double-Button-1>",self.callback)
        self.title("Expérience")
        self.exp=Experiment() # On crée un nouvel objet Experiment
        self.exp.get_times() # On lui applique immédiatement get_times pour extraire les zones et les temps.
        # On crée des champs pour que l'utilisateur renseigne les paramètres de l'expérience
        Label(self,text="Date ").grid(row=0,column=0)
        self.date=Label(self,textvariable=self.exp.date)
        self.date.grid(row=0,column=1)
        Label(self,text="Passage ").grid(row=1,column=0)
        self.passage=Entry(self,textvariable=self.exp.passage)
        self.passage.grid(row=1,column=1)
        Label(self,text="Lamelle ").grid(row=2,column=0)
        self.lamelle=Entry(self,textvariable=self.exp.lamelle)
        self.lamelle.grid(row=2,column=1)
        Label(self,text="Taux d'étirement ").grid(row=3,column=0)
        self.strain=Entry(self,textvariable=self.exp.strain)
        self.strain.grid(row=3,column=1)
        Label(self,text="Heure ").grid(row=4,column=0)
        self.time=Entry(self,textvariable=self.exp.time)
        self.time.grid(row=4,column=1)

        # Recensement des zones, création des Zone_Frames et affichage des boutons permettant d'y accéder
        self.zoneframes={} # Dictionnaire contenant les Zone_Frames, avec la même chaîne de caractères "zoneN" que exp.zones pour y accéder. 
        i=0 # Compteur de lignes pour aligner les boutons
        self.cur_zoneframekey=StringVar() # Contient la clé de la Zone Active dans le dictionnaire des Zone_Frames
        self.exp.zones_sorted=list(self.exp.zones.keys()) # liste triée par ordre aphabétique (attention pas numérique)des noms de Zones
        self.exp.zones_sorted.sort()
        for zone in self.exp.zones_sorted:
            # Affichage d'un bouton radio pour chaque zone qui change la valeur de cur_zoneframekey pour celle sélectionnée 
            self.create_zone(zone)
            self.bouton=Radiobutton(self,text=zone,variable=self.cur_zoneframekey,value=zone)
            self.bouton.grid(row=i,column=2)
            i=i+1

        # Défition de compteurs de valeurs
        self.nbtrans=IntVar() # Compte le nombre de translocations recensées sur toutes les zones
        self.nbGFP=IntVar() # Compte le nombre de cellules observées sur toutes les zones
        self.nbetrans=IntVar() # Compte le nombre de translocations entrantes
        self.nbstrans=IntVar() # Compte le nombre de translocations sortantes

        # Défition de boutons-fonctions
        Button(self,text="Afficher la zone",command=self.open_zone).grid(row=i,column=1)
        Button(self,text="Compter les cellules translocantes",command=self.count_transloc).grid(row=5,column=0)
        Button(self,text="Compter les cellules GFP",command=self.count_GFP).grid(row=6,column=0)
        Label(self,textvariable=self.nbtrans).grid(row=5,column=1)
        Label(self,textvariable=self.nbGFP).grid(row=6,column=1)
        Label(self,text="Translocations entrantes").grid(row=7,column=0)
        Label(self,text="Translocations sortantes").grid(row=8,column=0)
        Label(self,textvariable=self.nbetrans).grid(row=7,column=1)
        Label(self,textvariable=self.nbstrans).grid(row=8,column=1)
        Button(self,text="Enregistrer les résultats dans la base de données",command=self.save_in_DB).grid(row=9,column=0)

        
    def create_zone(self,zone):
        # Sert à créer une nouvelle Zone_Frame
        self.cur_zoneframe=Zone_Frame(zone=self.exp.zones[zone],boss=self)
        self.zoneframes[zone]=self.cur_zoneframe
        self.cur_zoneframe.iconify()
    def open_zone(self):
        # Sert à faire apparaître à l'écran la Zone_Frame sélectionnée grâce au Bouton Radio. 
        self.cur_zoneframe.iconify()
        self.cur_zoneframe=self.zoneframes[self.cur_zoneframekey.get()]
        self.cur_zoneframe.deiconify()
        self.cur_zoneframe.callback()
    def callback(self,event=None):
        #change le Focus (pour les raccourcis clavier)
        self.focus_set() 
    def count_transloc(self):
        # Comptage des translocations en parcourant toutes les cellules de toutes les zones.
        n=0 # Compteur de translocations
        ne=0 # Compteur de translocations entrantes
        ns=0 # Compteur de translocations sortantes
        for zoneframe in self.zoneframes.values():
            for cellframe in zoneframe.cells:
                if len(cellframe.cell.transloc)>0:
                    n=n+1
                    for transloc in cellframe.cell.transloc:
                        if transloc in ["ch","hn","cn"]:
                            ne=ne+1
                        elif transloc in ["nh","nc","hc"]:
                            ns=ns+1                    
        self.nbtrans.set(n)
        self.nbetrans.set(ne)
        self.nbstrans.set(ns)
    
    def count_GFP(self):
        # Compteur de cellules observées
        n=0
        for zoneframe in self.zoneframes.values():
            n=n+len(zoneframe.cells)
        self.nbGFP.set(n)

    
    def save_in_DB(self):
        # Cette fonction sert à prendre toutes les données rassemblées jusque là et à les inscrire dans une base de données SQLite.
        # Etablissement de la connexion à la base de données
        import sqlite3
        DB="O:\\Etirement.sq3"
        connexion=sqlite3.connect(DB)
        cur=connexion.cursor()
        
        # Enregistrement des données générales de l'expérience
        date=self.exp.date.get()+" "+self.exp.time.get()[:2]+":"+self.exp.time.get()[3:]
        print(date)
        time_str=self.exp.time.get()
        time0=int(time_str[0:2])*60+int(time_str[3:5])
        passage=self.exp.passage.get()
        etirement=self.exp.strain.get()
        lamelle=self.exp.lamelle.get()
        tu=(date,passage,etirement,lamelle)
        order="SELECT Exp_ID FROM Experiments "+"WHERE Experiments.date="+"'"+date+"'"+" AND Experiments.passage="+str(passage)+" AND Experiments.etirement="+str(etirement)+" AND Experiments.lamelle="+str(lamelle)
        print(order)
        result=cur.execute(order)
        
        if result.fetchall()==[]:
            cur.execute("INSERT INTO Experiments (date,passage,etirement,lamelle) VALUES (?,?,?,?)",tu)
        
        # Enregistrement des données relatives à chaque Zone
        for zonekey in self.exp.zones_sorted:
            zone=self.exp.zones[zonekey]
            densite=zone.nbcell.get()
            Exp_ID_cur=cur.execute("SELECT Exp_ID FROM Experiments WHERE date="+"'"+date+"'")
            for i in Exp_ID_cur:
                Exp_ID=i
            tu=(densite,)+Exp_ID+(zonekey,)
            #print(tu)
            order="SELECT Zone_ID FROM Zones WHERE Exp_ID="+str(Exp_ID[0])+ " AND densite="+str(densite)+ " AND Zone_loc='"+str(zonekey)+"'"
            print(order)
            resulte=cur.execute(order)
            if result.fetchall()==[]:
                cur.execute("INSERT INTO Zones (densite,Exp_ID,Zone_loc) VALUES (?,?,?)",tu)
            zoneframe=self.zoneframes[zonekey]
            time=[]
            Zone_ID_cur=cur.execute("SELECT Zone_ID FROM Zones WHERE (Zone_loc="+"'"+str(zonekey)+"' AND Exp_ID="+str(Exp_ID[0])+")")
            for z in Zone_ID_cur:
                Zone_ID=z
                print(z)
            for i in range(len(zone.times)):
                time.append(int(zone.times[i][0:2])*60+int(zone.times[i][3:5])-time0)
            for cellframe in zoneframe.cells:
                # Enregistrement des données relatives à chaque Cellule
                cell=cellframe.cell
                AMC=int(cell.MCherry.get())
                Cell_loc=cellframe.titre
                tu=(AMC,Cell_loc)+Zone_ID
                n=1
                col="(Actine_MCherry,Cell_loc,Zone_ID"
                val="(?,?,?"
                selection="SELECT Cell_ID FROM Cellules WHERE Zone_ID="+str(Zone_ID[0])+ " AND Actine_MCherry="+str(AMC)+ " AND Cell_loc='"+Cell_loc+"'"

                for i in range(len(zone.times)):
                    if (i==0):
                        tu=tu+(cell.etat[i].get(),time[i])
                        col=col+",etat0,temps0"
                        val=val+",?,?"
                        selection=selection+" AND etat0='"+cell.etat[i].get()+"'"+" AND temps0="+str(time[i])
                    elif (cell.etat[i-1].get()!=cell.etat[i].get()):
                        tu=tu+(cell.etat[i].get(),time[i])
                        col=col+",etat"+str(n)+",temps"+str(n)
                        val=val+",?,?"
                        selection=selection+" AND etat"+str(n)+"='"+cell.etat[i].get()+"'"+" AND temps"+str(n)+"="+str(time[i])
                        n=n+1
                tu=tu+(cell.etat[len(zone.times)-1].get(),time[len(zone.times)-1])
                                            
                col=col+",etatf,tempsf)"
                val=val+",?,?)"
                selection=selection+" AND etatf='"+cell.etat[len(zone.times)-1].get()+"'"+" AND tempsf="+str(time[len(zone.times)-1])
                print(selection)
                order="INSERT INTO Cellules "+col+" VALUES "+val
                print(order)
                print(tu)
                result=cur.execute(selection)
                if result.fetchall()==[]:
                    cur.execute(order,tu)
                                       
                #print(col)
                #print(tu)

        connexion.commit()
        cur.close()

        
                        
        

        

class Zone_Frame(Toplevel):
    def __init__(self,zone,boss=None):
        Toplevel.__init__(self,boss)
        self.bind("<Double-Button-1>",self.callback)
        self.zone=zone # Contient l'objet Zone associé à cette fenêtre
        self.title(self.zone.name)
        self.cells=[]# Contient la liste des Cell_Frames dépendant de cette Zone
        #Affichage et boutons
        Label(self,text="Nombre de cellules : ").grid(row=0,column=0)
        Entry(self,textvariable=self.zone.nbcell).grid(row=0,column=1)
        Label(self,text="Nombre de cellules GFP : ").grid(row=1,column=0)
        Label(self,textvariable=self.zone.nbGFPcell).grid(row=1,column=1)
        Label(self,text="Nombre de cellules transloc. : ").grid(row=2,column=0)
        Label(self,textvariable=self.zone.nbtranscell).grid(row=2,column=1)
        self.bouton=Button(self,text="Nouvelle Cellule",command=self.new_cell)
        self.bouton.grid(row=3,column=1)
        Button(self,text="Afficher la Cellule",command=self.open_cell).grid(row=4,column=1)
        Button(self,text="Fermer la Cellule",command=self.close_cell).grid(row=5,column=1)
        Button(self,text="Compter les translocations",command=self.count_transloc).grid(row=2,column=2)
        Button(self,text="Supprimer la Cellule",command=self.destroy_cell).grid(row=6,column=1)
        # Raccourcis clavier
        self.bind("s",self.destroy_cell)
        self.bind("n",self.new_cell)
        self.bind("a",self.open_cell)
        self.bind("c",self.count_transloc)
        self.cur_cell=IntVar()
        self.boutonsR=[] # Liste des boutons Radio permettant d'afficher les cellules
    def new_cell(self,event=None):
        # Création d'une nouvelle Cell_Frame et mise à jour de l'affichage
        cur_zone=self.zone
        self.cell=Cell_Frame(cur_zone,boss=self)
        self.cells.append(self.cell)
        nb=self.zone.nbGFPcell.get()
        self.zone.nbGFPcell.set(nb+1)
        self.cell.title("Cellule n°"+str(nb))
        self.cell.titre="Cellule n°"+str(nb)
        self.boutonR=Radiobutton(self,text="cellule n°"+str(nb),variable=self.cur_cell,value=nb)
        self.boutonR.grid(row=nb,column=3)
        self.boutonsR.append(self.boutonR)
        #self.cell.iconify()
        self.cell.focus_set()
    def open_cell(self,event=None):
        # Réouverture de la cellule sélectionnée par le bouton Radio
        self.cells[self.cur_cell.get()].deiconify()
    def close_cell(self):
        # Fermeture de la cellule sélectionnée par le bouton Radio
        self.cells[self.cur_cell.get()].iconify()
    def count_transloc(self,event=None):
        # Comptage des translocations sur la Zone
        self.zone.nbtranscell.set(0)
        for cellule in self.cells:
            if len(cellule.cell.transloc)>0:
                n=self.zone.nbtranscell.get()
                self.zone.nbtranscell.set(n+1)
    def callback(self,event=None):
        # Mettre le Focus sur cette fenêtre pour les raccourcis clavier
        self.focus_set()   
    def destroy_cell(self,event=None):
        # Détruire une Cell_Frame et toutes les informations qui y sont relatives.
        for i in range(len(self.cells)):
            self.boutonsR[i].destroy()
        self.cells[self.cur_cell.get()].destroy()
        del self.cells[self.cur_cell.get()]
        self.boutonsR=[]
        for i in range(len(self.cells)):
            self.boutonR=Radiobutton(self,text="cellule n°"+str(i),variable=self.cur_cell,value=i)
            self.boutonR.grid(row=i,column=3)
            self.boutonsR.append(self.boutonR)
        self.zone.nbGFPcell.set(len(self.cells))


        

class Cell_Frame(Toplevel):
    def __init__(self,zone,boss=None):
        Toplevel.__init__(self,boss)
        self.boss=boss
        # Raccourcis clavier
        self.bind("<Double-Button-1>",self.callback)
        self.bind("c",self.set_c)
        self.bind("h",self.set_h)
        self.bind("n",self.set_n)
        self.bind("f",self.close_cell)
        self.bind("a",self.actine)
        self.bind("d",self.set_d)
        # Référence à la Zone dans laquelle est contenue la cellule
        self.zone=zone
        self.cell=Cellule(zone) # Création d'un objet Cellule
        # Affichage des temps de la zone et création des champs où l'utilisateur peut entrer l'état des cellules.
        self.zone.times.sort()
        for time in self.zone.times:
            cur_state=StringVar()
            self.cell.etat.append(cur_state)
            i=self.cell.etat.index(cur_state)
            Label(self,text=time).grid(row=self.zone.times.index(time),column=0)
            Entry(self,textvariable=self.cell.etat[i]).grid(row=self.zone.times.index(time),column=1)
        Checkbutton(self,text="Actine MCherry",variable=self.cell.MCherry).grid(row=0,column=2)
        Button(self,text="Fermer la cellule", command=self.close_cell).grid(row=len(self.zone.times),column=1)
        self.cur_entry=0
    def close_cell(self,event=None):
        # Réduction de la fenêtre avec vérification de l'accord des données entrées avec les restrictions et comptage des translocations
        val_autoris=["c","h","n","d"]
        i=0
        for etat in self.cell.etat:
            if etat.get() not in val_autoris:
                if i==0:
                    self.erreur=Toplevel(self)
                ind=self.cell.etat.index(etat)
                str_etat=etat.get()
                Label(self.erreur,text="L'entrée n°"+str(ind)+" : "+str_etat+" à "+self.zone.times[ind]+" n'est pas dans un des états autorisés : c,h,n,d").grid(row=i,column=0)
                i=i+1
        if i==0:
            for i in range(len(self.cell.etat)-1):
                etat_av=self.cell.etat[i].get()
                etat_ap=self.cell.etat[i+1].get()
                if etat_av!=etat_ap and etat_ap!="d":
                    self.cell.transloc.append(etat_av+etat_ap)
            print(self.cell.transloc)
            self.iconify()
            self.boss.callback()
    #Raccourcis clavier
    def callback(self,event):
        self.focus_set() 
    def set_c(self,event):
        self.cell.etat[self.cur_entry].set("c")
        self.cur_entry=self.cur_entry+1
        if self.cur_entry > len(self.cell.etat)-1:
            self.cur_entry=0
    def set_h(self,event):
        self.cell.etat[self.cur_entry].set("h")
        self.cur_entry=self.cur_entry+1
        if self.cur_entry > len(self.cell.etat)-1:
            self.cur_entry=0
    def set_n(self,event):
        self.cell.etat[self.cur_entry].set("n")
        self.cur_entry=self.cur_entry+1
        if self.cur_entry > len(self.cell.etat)-1:
            self.cur_entry=0
    def set_d(self,event):
        self.cell.etat[self.cur_entry].set("d")
        self.cur_entry=self.cur_entry+1
        if self.cur_entry>len(self.cell.etat)-1:
            self.cur_entry=0
    def actine(self,event):
        if self.cell.MCherry.get()==0:
            self.cell.MCherry.set(1)
        else:
            self.cell.MCherry.set(0)


class IS_Frame(Toplevel):
    def __init__(self,boss=None):
        Toplevel.__init__(self,boss)
        self.lamelle=IntVar()
        self.date=StringVar()
        self.time=StringVar()
        self.c=IntVar()
        self.h=IntVar()
        self.n=IntVar()
        self.AMC=IntVar()
        
        
        Label(self,text="C").grid(column=0,row=1)
        Label(self,text="H").grid(column=1,row=1)
        Label(self,text="N").grid(column=2,row=1)
        Label(self,textvariable=self.c).grid(column=0,row=2)
        Label(self,textvariable=self.h).grid(column=1,row=2)
        Label(self,textvariable=self.n).grid(column=2,row=2)
        self.bind("c",self.add_c)
        self.bind("h",self.add_h)
        self.bind("n",self.add_n)        
        self.bind("C",self.sub_c)
        self.bind("H",self.sub_h)
        self.bind("N",self.sub_n)
        self.bind("<Double-Button-1>",self.callback)
        Label(self,textvariable=self.date).grid(row=0,column=0)
        Label(self,text="Lamelle ").grid(row=0,column=1)
        Label(self,text="heure ").grid(row=0,column=2)
        Entry(self,textvariable=self.time).grid(row=0,column=3)
        self.lamelle=Entry(self,textvariable=self.lamelle)
        self.lamelle.grid(row=0,column=2)
        Checkbutton(self,text="Actine MCherry",variable=self.AMC).grid(row=0,column=4)
        Button(self,text="Enregistrer dans la base de données",command=self.save).grid(column=3,row=3)
    def add_c(self,event):
        self.c.set(self.c.get()+1)
    def add_h(self,event):
        self.h.set(self.h.get()+1)    
    def add_n(self,event):
        self.n.set(self.n.get()+1)
    def sub_c(self,event):
        self.c.set(self.c.get()-1)
    def sub_h(self,event):
        self.h.set(self.h.get()-1)
    def sub_n(self,event):
        self.n.set(self.n.get()-1)
    def callback(self,event):
        self.focus_set()
    def save(self):
        import sqlite3
        DB="O:\\Etirement.sq3"
        connexion=sqlite3.connect(DB)
        cur=connexion.cursor()
        self.date.set(self.date.get()+" "+self.time.get())

        #print("UPDATE Experiments SET init_a"+str(self.AMC.get())+"_c="+str(self.c.get())+" WHERE Experiments.date='"+self.date.get()+"' AND Experiments.lamelle="+str(self.lamelle.get()))
        cur.execute("UPDATE Experiments SET init_a"+str(self.AMC.get())+"_c="+str(self.c.get())+" WHERE Experiments.date='"+self.date.get()+"' AND Experiments.lamelle="+str(self.lamelle.get()))
        
        cur.execute("UPDATE Experiments SET init_a"+str(self.AMC.get())+"_h="+str(self.h.get())+" WHERE Experiments.date='"+self.date.get()+"' AND Experiments.lamelle="+str(self.lamelle.get()))
        
        cur.execute("UPDATE Experiments SET init_a"+str(self.AMC.get())+"_n="+str(self.n.get())+" WHERE Experiments.date='"+self.date.get()+"' AND Experiments.lamelle="+str(self.lamelle.get()))
        connexion.commit()
        cur.close()
        connexion.close()
        
                
        
        
# Lancement de l'application.
BF=Base_frame()
BF.grid(row=0,column=0)

