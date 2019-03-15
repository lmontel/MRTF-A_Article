import sqlite3
import numpy as np
import matplotlib.pyplot as pl

DB="D:\\Etirement.sq3"
conn=sqlite3.connect(DB)
cur=conn.cursor()




class Database(object):
    def __init__(self):
        self.liste_date=[]
        result=cur.execute("SELECT Experiments.date FROM Experiments")
        for r in result:
            self.liste_date.append(r[0])

        self.liste_passage=[]
        result=cur.execute("SELECT DISTINCT passage FROM Experiments")
        for r in result:
            self.liste_passage.append(r[0])

        self.liste_etirement=[]
        result=cur.execute("SELECT DISTINCT etirement FROM Experiments")
        for r in result:
            self.liste_etirement.append(r[0])
        self.etats=['c','h','n','d']
        self.code_couleur={}
        self.code_couleur['c']="red"
        self.code_couleur['C']="red"
        self.code_couleur['hc']="orange"
        self.code_couleur['nc']="yellow"
        self.code_couleur['ch']="green"
        self.code_couleur['cn']="lightblue"
        self.code_couleur['h']="darkgreen"
        self.code_couleur['H']="darkgreen"
        self.code_couleur['n']="darkblue"
        self.code_couleur['N']="darkblue"
        self.code_couleur['nh']="lightgreen"
        self.code_couleur['hn']="blue"
        self.code_couleur['d']="black"


class Selection(object):
    def __init__(self,
                 liste_date=[],
                 date_min=None,
                 date_max=None,
                 passage_min=None,
                 passage_max=None,
                 etirement=None,
                 densite_min=None,
                 densite_max=None,
                 AMC=None,
                 etats=[None]*8,
                 premontee=None,
                 rincee=None):
        self.liste_date=liste_date
        self.date_min=date_min
        self.date_max=date_max
        self.passage_min=passage_min
        self.passage_max=passage_max
        self.etirement=etirement
        self.densite_min=densite_min
        self.densite_max=densite_max
        self.AMC=AMC
        self.etats=etats
        self.premontee=premontee
        self.rincee=rincee
        

    
        self.select_string=" FROM Experiments,Zones,Cellules WHERE Cellules.Zone_ID=Zones.Zone_ID AND Zones.Exp_ID=Experiments.Exp_ID "

        if len(self.liste_date):
            self.select_string+="AND ("+"Experiments.date="+"'"+str(self.liste_date[0])+"'"
            for self.date in self.liste_date[1:]:
                self.select_string+=" OR Experiments.date="+"'"+str(self.date)+"'"
            self.select_string+=")"
        if self.date_min is not None:
            self.select_string+=" AND Experiments.date>'"+str(self.date_min)+"'"
        if self.date_max is not None:
            self.select_string+=" AND Experiments.date<'"+str(self.date_max)+"'"

        if self.passage_min is not None:
            self.select_string+=" AND Experiments.passage>="+str(self.passage_min)
        if self.passage_max is not None:
            self.select_string+=" AND Experiments.passage<="+str(self.passage_max)

        if self.etirement is not None:
            self.select_string+=" AND Experiments.etirement="+str(self.etirement)

        if self.densite_min is not None:
            self.select_string+=" AND Zones.densite>="+str(self.densite_min)
        if self.densite_max is not None:
            self.select_string+=" AND Zones.densite<="+str(self.densite_max)

        if self.AMC is not None:
            self.select_string+=" AND Cellules.Actine_MCherry="+str(self.AMC)

        if self.etats is not [None]*8:
            for etat in self.etats:
                if etat is not None:
                    self.select_string+=" AND Cellules.etat"+str(self.etats.index(etat))+"="+str(etat)

        if self.premontee is not None:
            self.select_string+=" AND Experiments.Premontee="+str(self.premontee)

        if self.rincee is not None:
            self.select_string+=" AND Experiments.Rincee="+str(self.rincee)

        #print(self.select_string)

    #def time_lapse(self):
        self.colonnes="Cellules.etat0,Cellules.temps0"
        for j in range(1,7):
            self.colonnes=self.colonnes+",Cellules.etat"+str(j)+","+"Cellules.temps"+str(j)
        self.colonnes=self.colonnes+",Cellules.etatf,Cellules.tempsf,Cellules.Cell_ID"
                

        self.dic=[]
        self.dic_trans=[]
        self.data={}
        self.data_trans={}
        self.data_trans_lis={}
        for minute in range(140,-1,-1):
            self.dic.append({})
            self.dic_trans.append({})



        result=cur.execute("SELECT "+self.colonnes+self.select_string)
        #print("SELECT "+self.colonnes+self.select_string)
        
        for r in result:
            #print(r)
            for minute in range(140,-1,-1):
                
                if minute<=int(r[15]) and minute>=int(r[1]):
                    n=0
                    while n<14 and minute<int(r[15-n]):
                        n=n+2
                        #print(n)
                        while(r[15-n]==None):
                            n=n+2
                    
                    if n<14 and n>0:
                        self.dic[minute][r[12-n]+r[14-n]]=self.dic[minute].get(r[12-n]+r[14-n],0)+1
                        if r[14-n]!=r[12-n] and int(r[15-n])==minute:
                            #print(n)
                            self.dic_trans[minute][r[12-n]+r[14-n]]=self.dic_trans[minute].get(r[12-n]+r[14-n],0)+1
                            
                    else :
                        self.dic[minute][r[14-n]]=self.dic[minute].get(r[14-n],0)+1   
        self.data_total=np.ones(141)
        for etat in ['c','h','n','ch','cn','hc','hn','nh','nc','d']:
            self.data[etat]=np.zeros(141)
            self.data_trans[etat]=np.zeros(141)
            self.data_trans_lis[etat]=np.zeros(141)
            if len(etat)>1:
                for minute in range(140,-1,-1):
                    self.data[etat][minute]=self.dic[minute].get(etat,0)
                    self.data_trans[etat][minute]=self.dic_trans[minute].get(etat,0)
            else:
                for minute in range(140,-1,-1):
                    self.data[etat][minute]=self.dic[minute].get(etat,0)
            self.data_total+=self.data.get(etat,np.zeros(141))
            for minute in range(140,-1,-1):
                self.data_trans_lis[etat][minute]=np.sum(self.data_trans[etat][minute-2:minute+2])
        self.data['C']=self.data['c']+self.data['hc']+self.data['nc']
        self.data['H']=self.data['h']+self.data['ch']+self.data['nh']
        self.data['N']=self.data['n']+self.data['hn']+self.data['cn']
            
        

    


        
database=Database()
temoin=Selection(etirement=0,rincee=0,premontee=1,densite_max=25,AMC=0,date_max="2014-01-01")
temoin_serum=Selection(etirement=0,rincee=1,densite_max=25,AMC=0,date_max="2014-01-01")
Et0_serum=Selection(etirement=0,rincee=1,densite_max=25,AMC=0,date_max="2014-01-01")
Et10=Selection(etirement=10,rincee=0,premontee=1,densite_max=25,AMC=0,date_max="2014-01-01")
Et30=Selection(etirement=30,rincee=0,premontee=1,densite_max=25,AMC=0,date_max="2014-01-01")
Et10_AMC=Selection(etirement=10,AMC=1,densite_max=25,date_max="2014-01-01")
Et30_AMC=Selection(etirement=30,AMC=1,densite_max=25,date_max="2014-01-01")
Et10_serum=Selection(etirement=10,rincee=1,AMC=0,densite_max=25,date_max="2014-01-01")
Et30_serum=Selection(etirement=30,rincee=1,AMC=0,densite_max=25,date_max="2014-01-01")
liste_Et10=[Et10,Et10_serum,Et10_AMC]
liste_Et30=[Et30,Et30_serum,Et30_AMC]
liste_temoin=[temoin,Et0_serum]
Ftractin=Selection(liste_date=["2015-03-24 12:14"],AMC=1)
Sans_Ftractin=Selection(liste_date=["2015-03-24 12:14"],AMC=0)
liste_couleurs=['r','g','b','k']
etats_simple=['C','H','N']
etats_tous=['c','hc','nc','ch','h','nh','cn','hn','n']
translocations=['ch','hc','hn','nh','cn','nc']
markers=['+','x','o','s','*','^']

        
def plot_simple_err(experiment_list,labels=[]):
	for etat in etats_simple:
		pl.subplot(3,1,etats_simple.index(etat)+1)
		pl.title(etat)
		for exp in experiment_list:
			pl.errorbar(np.arange(141),
				exp.data[etat]/exp.data_total,
                                erreurs(Liste_date(exp))[etat],    
				label=labels[experiment_list.index(exp)],
                                color=liste_couleurs[etats_simple.index(etat)],
                                alpha=1/len(experiment_list)*(experiment_list.index(exp)+1),
                                marker=markers[experiment_list.index(exp)]
				)
		limites=[(0.3,0.8),(0.1,0.45),(0.1,0.45)]
		localisation=['upper right','upper right','upper right']
		pl.xlim(3,105)
		pl.ylim(limites[etats_simple.index(etat)])
		pl.legend(loc=localisation[etats_simple.index(etat)])
		
	
def plot_transloc(experiment_list,labels=[]):
	for etat in translocations:
		pl.subplot(3,2,translocations.index(etat)+1)
		pl.title(etat)
		pl.ylim(0,0.1)
		for exp in experiment_list:
			pl.plot(np.arange(141),
				exp.data_trans_lis[etat]/exp.data_total,
				label=labels[experiment_list.index(exp)])
		pl.legend()
        
def plot_detaille(experiment_list,labels=[]):
	for etat in etats_tous:
		pl.subplot(3,3,etats_tous.index(etat)+1)
		pl.title(etat)
		for exp in experiment_list:
			pl.plot(np.arange(141),
				exp.data[etat]/exp.data_total,
				label=labels[experiment_list.index(exp)]
				)
		pl.legend(fontsize='x-small')
	pl.show()

def Liste_date(selection):
    result=cur.execute("SELECT DISTINCT Experiments.date  "+selection.select_string)
    liste_date=[]
    for r in result:
        liste_date.append(r[0])
    return liste_date
        


def erreurs(liste_date):
	liste_exp=[]
	erreurs={}
	for date in liste_date:
		exp=Selection(liste_date=[date])
		liste_exp.append(exp)
	for etat in ['C','H','N']:
		erreurs[etat]=[]
		for i in range(141):
			liste=[]
			for exp in liste_exp:
				liste.append(exp.data[etat][i]/exp.data_total[i])
				#print(exp.data[etat][i]/exp.data_total[i])

			#print(liste)
			erreurs[etat].append(np.std(liste)/(len(liste))**(1/2))

	return erreurs

def erreurs_transloc(liste_date):
	liste_exp=[]
	erreur_e=np.zeros(141)
	erreur_s=np.zeros(141)
	erreur={}
	for date in liste_date:
		exp=Selection(liste_date=[date])
		liste_exp.append(exp)
	for etat in ['ch','hn','cn']:
		erreur[etat]=[]
		for i in range(141):
			liste=[]
			for exp in liste_exp:
				liste.append(exp.data_trans_lis[etat][i]/exp.data_total[i])
				#print(exp.data[etat][i]/exp.data_total[i])

			#print(liste)
			erreur[etat].append(np.std(liste)/(len(liste)*(len(liste)-1))**(1/2))
		erreur_e+=np.array(erreur[etat])
	for etat in ['hc','nh','nc']:
		erreur[etat]=[]
		for i in range(141):
			liste=[]
			for exp in liste_exp:
				liste.append(exp.data_trans_lis[etat][i]/exp.data_total[i])
				#print(exp.data[etat][i]/exp.data_total[i])

			#print(liste)
			erreur[etat].append(np.std(liste)/(len(liste)*(len(liste)-1))**(1/2))	
		erreur_s+=np.array(erreur[etat])
	return erreur_e,erreur_s

