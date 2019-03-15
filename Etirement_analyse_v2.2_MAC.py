from os import getcwd,chdir,listdir
import xlrd
import numpy as np
import pylab as pl
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import sqlite3

disque="//Volumes//DDLorraine//These//DocumentsLorraine//"
# Création de 4 dictionnaires qui vont contenir
# les informations d'aire (en pixels carrés)
# d'intensité moyenne par pixel
# d'intensité totale
# et le numéro de slice
# pour toutes les expériences et toutes les zones examinées
# Les clés de ces 4 dictionnaires sont les références de l'expérience
# Le contenu est un autre dictionnaire indexé par les régions observées
aire={}
mean={}
intden={}
sl={}
gain={}
exposure={}
times={}

# ce dictionnaire permet d'indexer les noms des 4 dictionnaires créés
dic_value={}
dic_value['aire']=aire
dic_value['mean']=mean
dic_value['intden']=intden
dic_value['slice']=sl

#Dictionnaire des légendes des expériences
dic_exp_label={}


# Liste des régions observées pour chaque cellule. Ce sont les clés de chaque dictionnaire d'expérience.
regions=['F_tot','G_tot','F/G_tot','G_noyau','MRTFA_noyau','F/G_noyau','G_peri','MRTFA_peri']

DB=disque+'//Etirement.sq3'
conn=sqlite3.connect(DB)
cur=conn.cursor()
# New_Results et ses variantes sont des fonctions qui ouvrent un fichiers Excel de données créé par ImageJ
# et vont lire les colonnes et les lignes dans l'ordre pour remplir les tableaux indexés dans le dictionnaire value[experiment][region]
# Cette fonction prend pour argument la clé de dictionnaire sous laquelle l'expérience sera référencée
# et la localisation du fichier Excel à lire
# Attention, le fichier doit être un classeur Excel et non un tab-delimited text comme généré par ImageJ
# La feuille Excel contenue dans ce fichier doit être nommée "Results"
def New_Results(temps,file):

    
    workbook=xlrd.open_workbook(file)
    sh=workbook.sheet_by_name('Results')

    
    #Création des sous-dictionnaires de l'expérience
    aire[temps]={}
    mean[temps]={}
    intden[temps]={}

    measurements=[aire,mean,intden]
    regions=['F_tot','G_tot','F/G_tot','G_noyau','MRTFA_noyau','F/G_noyau','G_peri','MRTFA_peri']

    # Dans chaque sous-dictionnaire, pour chaque region, on crée une liste vide qui accueillera les données pour chaque cellule
    for m in measurements:
        for r in regions:
            m[temps][r]=[]

    # On va lire les colonnes du fichier Excel
    col={}
    col[0]=sh.col_values(1,start_rowx=1)
    col[1]=sh.col_values(2,start_rowx=1)
    col[2]=sh.col_values(7,start_rowx=1)
    channel=sh.col_values(9,start_rowx=1)

    # Cette boucle lit dans l'ordre toutes les valeurs mesurées pour chaque région et les ajoute à la liste correspondante
    for i in range(len(channel)-8):
        if channel[i:i+8]==[1.0,2.0,5.0,2.0,3.0,5.0,2.0,3.0]:
            for m in measurements:
                for r in regions:
                    m[temps][r].append(float(col[measurements.index(m)][i+regions.index(r)]))
                    
    # Une fois la transposition terminée, on transforme les listes en numpy arrays
    for m in measurements:
        for r in regions:
            m[temps][r]=np.array(m[temps][r])

    # On peut calculer des valeurs secondaires à partir des valeurs mesurées directement dans ImageJ
    mean[temps]['MRTFA_ratio']=mean[temps]['MRTFA_peri']/mean[temps]['MRTFA_noyau']
    intden[temps]["MRTFA_ratio"]=intden[temps]["MRTFA_noyau"]/(mean[temps]["MRTFA_peri"]*aire[temps]["F_tot"])
    intden[temps]['MRTFA_total']=intden[temps]['MRTFA_peri']+intden[temps]['MRTFA_noyau']
    intden[temps]["G_ratio"]=intden[temps]["G_noyau"]/(intden[temps]["G_tot"])
    mean[temps]['F_tot/G_tot']=mean[temps]['F_tot']/mean[temps]['G_tot']

    mean[temps]['F/G_noyau']=intden[temps]['F/G_noyau']/aire[temps]['F/G_noyau']
    mean[temps]['F/G_tot']=intden[temps]['F/G_tot']/aire[temps]['F/G_tot']
     
    mean[temps]['F_cyto']=(intden[temps]['F_tot']-mean[temps]['F/G_noyau']*intden[temps]['G_noyau'])/(aire[temps]['F_tot']-aire[temps]['G_noyau'])

    mean[temps]['G_cyto']=(intden[temps]['G_tot']-intden[temps]['G_noyau'])/(aire[temps]['G_tot']-aire[temps]['G_noyau'])

    mean[temps]['F_cyto/G_cyto']=mean[temps]['F_cyto']/mean[temps]['G_cyto']
    mean[temps]['G_peri/G_noyau']=mean[temps]['G_peri']/mean[temps]['G_noyau']

def New_Results2(temps,file):

    #file=input("File to read : ")
    workbook=xlrd.open_workbook(file)
    sh=workbook.sheet_by_name('Results_sup')

    #temps=input("Etirement et temps : ")

    measurements=[aire,mean,intden]
    regions=['F_tot2','G_tot2','F/G_tot2','F_noyau2','G_noyau2','F/G_noyau2']

    for m in measurements:
        for r in regions:
            m[temps][r]=[]

    col={}
    col[0]=sh.col_values(1,start_rowx=1)
    col[1]=sh.col_values(2,start_rowx=1)
    col[2]=sh.col_values(10,start_rowx=1)
    channel=sh.col_values(12,start_rowx=1)
    sl=sh.col_values(13,start_rowx=1)

    for i in range(len(channel)-6):
        if channel[i:i+6]==[1.0,2.0,5.0,1.0,2.0,5.0] and sl[i]==sl[i+3] and col[0][i]>col[0][i+3]:
            for m in measurements:
                for r in regions:
                    m[temps][r].append(float(col[measurements.index(m)][i+regions.index(r)]))
                    
    for m in measurements:
        for r in regions:
            m[temps][r]=np.array(m[temps][r])

    
    mean[temps]['F_cyto2']=(intden[temps]['F_tot2']-intden[temps]['F_noyau2'])/(aire[temps]['F_tot2']-aire[temps]['F_noyau2'])
    intden[temps]['F_cyto2']=(intden[temps]['F_tot2']-intden[temps]['F_noyau2'])
    
    mean[temps]['G_cyto2']=(intden[temps]['G_tot2']-intden[temps]['G_noyau2'])/(aire[temps]['G_tot2']-aire[temps]['G_noyau2'])
    intden[temps]['G_cyto2']=(intden[temps]['G_tot2']-intden[temps]['G_noyau2'])
    
    mean[temps]['F_cyto2/G_cyto2']=mean[temps]['F_cyto2']/mean[temps]['G_cyto2']
    
def New_Results3(temps,file):

    #file=input("File to read : ")
    workbook=xlrd.open_workbook(file)
    sh=workbook.sheet_by_name('Results_sup')

    #temps=input("Etirement et temps : ")

    measurements=[aire,mean,intden]
    regions=['F_tot2','G_tot2','F/G_tot2','F_noyau2','G_noyau2','F/G_noyau2']

    for m in measurements:
        for r in regions:
            m[temps][r]=[]

    col={}
    col[0]=sh.col_values(1,start_rowx=1)
    col[1]=sh.col_values(2,start_rowx=1)
    col[2]=sh.col_values(7,start_rowx=1)
    channel=sh.col_values(10,start_rowx=1)
    sl=sh.col_values(11,start_rowx=1)

    for i in range(len(channel)-6):
        if channel[i:i+6]==[1.0,2.0,5.0,1.0,2.0,5.0] and sl[i]==sl[i+3] and col[0][i]>col[0][i+3]:
            for m in measurements:
                for r in regions:
                    m[temps][r].append(float(col[measurements.index(m)][i+regions.index(r)]))
                    
    for m in measurements:
        for r in regions:
            m[temps][r]=np.array(m[temps][r])

    
    mean[temps]['F_cyto2']=(intden[temps]['F_tot2']-intden[temps]['F_noyau2'])/(aire[temps]['F_tot2']-aire[temps]['F_noyau2'])
    intden[temps]['F_cyto2']=(intden[temps]['F_tot2']-intden[temps]['F_noyau2'])
    
    mean[temps]['G_cyto2']=(intden[temps]['G_tot2']-intden[temps]['G_noyau2'])/(aire[temps]['G_tot2']-aire[temps]['G_noyau2'])
    intden[temps]['G_cyto2']=(intden[temps]['G_tot2']-intden[temps]['G_noyau2'])
    
    mean[temps]['F_cyto2/G_cyto2']=mean[temps]['F_cyto2']/mean[temps]['G_cyto2']
    
    
def New_Results4(temps,file):

    #file=input("File to read : ")
    workbook=xlrd.open_workbook(file)
    sh=workbook.sheet_by_name('Results')

    #temps=input("Etirement et temps : ")

    aire[temps]={}
    mean[temps]={}
    intden[temps]={}
    sl[temps]={}

    measurements=[aire,mean,intden,sl]
    regions=['F_tot','G_tot','F/G_tot','F_noyau','G_noyau','MRTFA_noyau','F/G_noyau','G_peri','MRTFA_peri']

    for m in measurements:
        for r in regions:
            m[temps][r]=[]

    col={}
    col[0]=sh.col_values(1,start_rowx=1)
    col[1]=sh.col_values(2,start_rowx=1)
    col[2]=sh.col_values(10,start_rowx=1)
    col[3]=sh.col_values(13,start_rowx=1)
    channel=sh.col_values(12,start_rowx=1)
    

    for i in range(len(channel)-9):
        if channel[i:i+9]==[1.0,2.0,5.0,1.0,2.0,3.0,5.0,2.0,3.0]:
            for m in measurements:
                for r in regions:
                    m[temps][r].append(float(col[measurements.index(m)][i+regions.index(r)]))
                    
    for m in measurements:
        for r in regions:
            m[temps][r]=np.array(m[temps][r])

    
    mean[temps]['MRTFA_ratio']=mean[temps]['MRTFA_peri']/mean[temps]['MRTFA_noyau']
    intden[temps]["MRTFA_ratio"]=intden[temps]["MRTFA_noyau"]/(mean[temps]["MRTFA_peri"]*aire[temps]["F_tot"])
    intden[temps]['MRTFA_total']=intden[temps]['MRTFA_peri']+intden[temps]['MRTFA_noyau']
    intden[temps]["G_ratio"]=intden[temps]["G_noyau"]/(intden[temps]["G_tot"])
    mean[temps]['F_tot/G_tot']=mean[temps]['F_tot']/mean[temps]['G_tot']

    mean[temps]['F/G_noyau']=intden[temps]['F/G_noyau']/aire[temps]['F/G_noyau']
    mean[temps]['F/G_tot']=intden[temps]['F/G_tot']/aire[temps]['F/G_tot']
    
    mean[temps]['F_cyto']=(intden[temps]['F_tot']-intden[temps]['F_noyau'])/(aire[temps]['F_tot']-aire[temps]['F_noyau'])

    mean[temps]['G_cyto']=(intden[temps]['G_tot']-intden[temps]['G_noyau'])/(aire[temps]['G_tot']-aire[temps]['G_noyau'])

    mean[temps]['F_cyto/G_cyto']=mean[temps]['F_cyto']/mean[temps]['G_cyto']
    mean[temps]['G_peri/G_noyau']=mean[temps]['G_peri']/mean[temps]['G_noyau']

def New_Results5(temps,file):

    #file=input("File to read : ")
    workbook=xlrd.open_workbook(file)
    sh=workbook.sheet_by_name('Results')

    #temps=input("Etirement et temps : ")

    aire[temps]={}
    mean[temps]={}
    intden[temps]={}
    sl[temps]={}
    gain[temps]=[]
    exposure[temps]={}
    ch_list=["F","G","MRTFA","DAPI"]
    for ch in ch_list:
        exposure[temps][ch]=[]

    measurements=[aire,mean,intden,sl]
    regions=['F_tot','G_tot','DAPI','G_noyau','MRTFA_noyau','G_peri','MRTFA_peri']

    for m in measurements:
        for r in regions:
            m[temps][r]=[]

    col={}
    col[0]=sh.col_values(2,start_rowx=1)
    col[1]=sh.col_values(3,start_rowx=1)
    col[2]=sh.col_values(8,start_rowx=1)
    col[3]=sh.col_values(11,start_rowx=1)
    channel=sh.col_values(10,start_rowx=1)
    label=sh.col_values(1,start_rowx=1)
    
    

    for i in range(len(channel)-7):
        if channel[i:i+7]==[1.0,2.0,4.0,2.0,3.0,2.0,3.0]:
            for j in range(len(measurements)):
                m=measurements[j]
                for r in regions:
##                    print(m)
##                    print(measurements.index(m))
##                    test=input("continue ?(y/n)")
##                    if test=="n":
##                        break
                    m[temps][r].append(float(col[j][i+regions.index(r)]))
            image=label[i].split(':')[1]
            with open(file[:-11]+image[:-4]+".txt",'r') as ouvert:
                lignes=ouvert.read().split("\n")
                gain[temps].append([])
                
                for line in [28,68,108,148]:
                    gain[temps][-1].append(float(lignes[line+1][21:]))
                    exposure[temps][ch_list[[28,68,108,148].index(line)]].append(float(lignes[line+4][31:]))
    
    for m in measurements:
        for r in regions:
            if m is mean or m is intden:
                m[temps][r]=np.array(m[temps][r])/np.array(exposure[temps][r.split('_')[0]])
            else:
                m[temps][r]=np.array(m[temps][r])

    
    mean[temps]['MRTFA_ratio']=mean[temps]['MRTFA_peri']/mean[temps]['MRTFA_noyau']
    intden[temps]["MRTFA_ratio"]=intden[temps]["MRTFA_noyau"]/(mean[temps]["MRTFA_peri"]*aire[temps]["F_tot"])
    intden[temps]['MRTFA_total']=intden[temps]['MRTFA_peri']+intden[temps]['MRTFA_noyau']

    mean[temps]['F_tot/G_tot']=mean[temps]['F_tot']/mean[temps]['G_tot']

    
    
    
    

    mean[temps]['G_cyto']=(intden[temps]['G_tot']-intden[temps]['G_noyau'])/(aire[temps]['G_tot']-aire[temps]['G_noyau'])

    
    mean[temps]['G_peri/G_noyau']=mean[temps]['G_peri']/mean[temps]['G_noyau']
def New_Results6(temps,file):

    #file=input("File to read : ")
    workbook=xlrd.open_workbook(file)
    sh=workbook.sheet_by_name('Results')

    #temps=input("Etirement et temps : ")

    aire[temps]={}
    mean[temps]={}
    intden[temps]={}
    sl[temps]={}
    gain[temps]=[]
    exposure[temps]={}
    ch_list=["F","G","MRTFA","DAPI"]
    for ch in ch_list:
        exposure[temps][ch]=[]

    measurements=[aire,mean,intden,sl]
    regions=['F_tot','G_tot','DAPI','G_noyau','G_peri']

    for m in measurements:
        for r in regions:
            m[temps][r]=[]

    col={}
    col[0]=sh.col_values(2,start_rowx=1)
    col[1]=sh.col_values(3,start_rowx=1)
    col[2]=sh.col_values(8,start_rowx=1)
    col[3]=sh.col_values(11,start_rowx=1)
    channel=sh.col_values(10,start_rowx=1)
    label=sh.col_values(1,start_rowx=1)
    
    

    for i in range(len(channel)-7):
        if channel[i:i+5]==[1.0,2.0,4.0,2.0,2.0]:
            for j in range(len(measurements)):
                m=measurements[j]
                for r in regions:
##                    print(m)
##                    print(measurements.index(m))
##                    
##                    test=input("continue ?(y/n)")
##                    if test=="n":
##                        break
                    m[temps][r].append(float(col[j][i+regions.index(r)]))
            image=label[i].split(':')[1]
            with open(file[:-18]+image[:-4]+".txt",'r') as ouvert:
                lignes=ouvert.read().split("\n")
                gain[temps].append([])
                
                for line in [28,68,108,148]:
                    gain[temps][-1].append(float(lignes[line+1][21:]))
                    exposure[temps][ch_list[[28,68,108,148].index(line)]].append(float(lignes[line+4][31:]))
    
    for m in measurements:
        for r in regions:
            if m is mean or m is intden:
                m[temps][r]=np.array(m[temps][r])/np.array(exposure[temps][r.split('_')[0]])
            else:
                m[temps][r]=np.array(m[temps][r])

    
    
    
    

    mean[temps]['F_tot/G_tot']=mean[temps]['F_tot']/mean[temps]['G_tot']

    
    
    
    

    mean[temps]['G_cyto']=(intden[temps]['G_tot']-intden[temps]['G_noyau'])/(aire[temps]['G_tot']-aire[temps]['G_noyau'])

    
    mean[temps]['G_peri/G_noyau']=mean[temps]['G_peri']/mean[temps]['G_noyau']

def New_Results7(temps,file):

    #file=input("File to read : ")
    workbook=xlrd.open_workbook(file)
    sh=workbook.sheet_by_name('Results-temoin')

    #temps=input("Etirement et temps : ")

    aire[temps]={}
    mean[temps]={}
    intden[temps]={}
    sl[temps]={}
    gain[temps]={}
    exposure[temps]={}
    ch_list=["Far_Red","rhodamine","GFP","DAPI","BF"]
    for ch in ch_list:
        exposure[temps][ch]=[]
        gain[temps][ch]=[]

    measurements=[aire,mean,intden,sl]
    regions=['F_tot','G_tot','Actin_tot','DAPI','G_noyau','Actin_noyau','G_peri','Actin_peri']

    for m in measurements:
        for r in regions:
            m[temps][r]=[]

    col={}
    col[0]=sh.col_values(2,start_rowx=1)
    col[1]=sh.col_values(3,start_rowx=1)
    col[2]=sh.col_values(8,start_rowx=1)
    col[3]=sh.col_values(11,start_rowx=1)
    channel=sh.col_values(10,start_rowx=1)
    label=sh.col_values(1,start_rowx=1)
    dic_channel={}
    dic_channel['F']='Far_Red'
    dic_channel['G']='rhodamine'
    dic_channel['Actin']='GFP'
    dic_channel['DAPI']='DAPI'
    

    for i in range(len(channel)-8):
        if channel[i:i+8]==[1.0,2.0,3.0,4.0,2.0,3.0,2.0,3.0]:
            for j in range(len(measurements)):
                m=measurements[j]
                for r in regions:
##                    print(m)
##                    print(measurements.index(m))
##                    test=input("continue ?(y/n)")
##                    if test=="n":
##                        break
                    m[temps][r].append(float(col[j][i+regions.index(r)]))
            image=label[i].split(':')[1]
            with open(file[:-11]+image[:-4]+".txt",'r') as ouvert:
                lignes=ouvert.read().split("\n")
                
                for l in range(len(lignes)):
                    if 'Move Channel' in lignes[l]:

                        gain[temps][lignes[l].split('- ')[-1]].append(float(lignes[l+1].split('- ')[-1]))
                        exposure[temps][lignes[l].split('- ')[-1]].append(float(lignes[l+4].split('- ')[-1]))
##                for line in [29,69,109,149]:
##                    print(lignes[line+1][21:])
##                    gain[temps][-1].append(float(lignes[line+1][21:]))
##                    exposure[temps][ch_list[[29,69,109,149].index(line)]].append(float(lignes[line+4][31:]))
##    
    for m in measurements:
        for r in regions:
            if m is mean or m is intden:
                m[temps][r]=np.array(m[temps][r])/np.array(exposure[temps][dic_channel[r.split('_')[0]]])
            else:
                m[temps][r]=np.array(m[temps][r])

    
    mean[temps]['Actin_ratio']=mean[temps]['Actin_peri']/mean[temps]['Actin_noyau']
    
    

    mean[temps]['F_tot/G_tot']=mean[temps]['F_tot']/mean[temps]['G_tot']

    
    
    
    

    mean[temps]['G_cyto']=(intden[temps]['G_tot']-intden[temps]['G_noyau'])/(aire[temps]['G_tot']-aire[temps]['G_noyau'])

    
    mean[temps]['G_peri/G_noyau']=mean[temps]['G_peri']/mean[temps]['G_noyau']

def New_Results8(temps,file):

    #file=input("File to read : ")
    workbook=xlrd.open_workbook(file)
    sh=workbook.sheet_by_name('Results')

    #temps=input("Etirement et temps : ")

    aire[temps]={}
    mean[temps]={}
    intden[temps]={}
    sl[temps]={}
    gain[temps]={}
    exposure[temps]={}
    times[temps]={}
    
    ch_list=["Far_Red","rhodamine"]
    for ch in ch_list:
        exposure[temps][ch]=[]
        gain[temps][ch]=[]

    measurements=[aire,mean,intden,sl]
    regions=['F_tot','G_tot','F_noyau','G_noyau','F_peri','G_peri']

    for m in measurements:
        for r in regions:
            m[temps][r]=[]
    for r in regions:
        times[temps][r]=[]

    dic_col={}
    for col_name in sh.row_values(rowx=0):
        dic_col[col_name]=sh.col_values(sh.row_values(rowx=0).index(col_name),start_rowx=1)
    channel=dic_col["Ch"]
    col={}
    col[0]=dic_col['Area']
    col[1]=dic_col["Mean"]
    col[2]=dic_col["RawIntDen"]
    col[3]=dic_col["Slice"]
    label=sh.col_values(1,start_rowx=1)
    
    dic_channel={}
    dic_channel['F']='Far_Red'
    dic_channel['G']='rhodamine'
    

    for i in range(0,len(channel)-6,6):
        if channel[i:i+6]==[1.0,2.0]*3:
            for j in range(len(measurements)):
                m=measurements[j]
                for r in regions:
##                    print(m)
##                    print(measurements.index(m))
##                    test=input("continue ?(y/n)")
##                    if test=="n":
##                        break
                    m[temps][r].append(float(col[j][i+regions.index(r)]))
            image=label[i].split(':')[1]
            with open('//'.join(file.split("//")[:-1])+"//"+image[:-4]+".txt",'r') as ouvert:
                lignes=ouvert.read().split("\n")
                
                for l in range(len(lignes)):
                    if 'Move Channel' in lignes[l]:
                        if 'Far_Red' in lignes[l] or "rhodamin" in lignes[l]:
    
                            gain[temps][lignes[l].split('- ')[-1]].append(float(lignes[l+1].split('- ')[-1]))
                            exposure[temps][lignes[l].split('- ')[-1]].append(float(lignes[l+4].split('- ')[-1]))
 
    for m in measurements:
        for r in regions:
            if m is mean or m is intden:
                m[temps][r]=np.array(m[temps][r])/np.array(exposure[temps][dic_channel[r.split('_')[0]]])
            else:
                m[temps][r]=np.array(m[temps][r])

    
    mean[temps]['F_ratio']=mean[temps]['F_peri']/mean[temps]['F_noyau']
    
    

    mean[temps]['F_tot/G_tot']=mean[temps]['F_tot']/mean[temps]['G_tot']

    
    
    
    

    mean[temps]['G_cyto']=(intden[temps]['G_tot']-intden[temps]['G_noyau'])/(aire[temps]['G_tot']-aire[temps]['G_noyau'])

    
    mean[temps]['G_peri/G_noyau']=mean[temps]['G_peri']/mean[temps]['G_noyau']

def New_Results9(temps,file):

    #file=input("File to read : ")
    workbook=xlrd.open_workbook(file)
    sh=workbook.sheet_by_index(0)

    #temps=input("Etirement et temps : ")

    aire[temps]={}
    mean[temps]={}
    intden[temps]={}
    sl[temps]={}
    gain[temps]={}
    exposure[temps]={}
    times[temps]={}
    
    ch_list=["Far_Red","rhodamine"]
    for ch in ch_list:
        exposure[temps][ch]=[]
        gain[temps][ch]=[]

    measurements=[aire,mean,intden,sl]
    regions=['F_tot_basal','G_tot','F_tot_apical','F_noyau_basal','G_noyau','F_noyau_apical','F_peri_basal','G_peri','F_peri_apical']

    for m in measurements:
        for r in regions:
            m[temps][r]=[]
    for r in regions:
        times[temps][r]=[]

    dic_col={}
    for col_name in sh.row_values(rowx=0):
        dic_col[col_name]=sh.col_values(sh.row_values(rowx=0).index(col_name),start_rowx=1)
    channel=dic_col["Ch"]
    col={}
    col[0]=dic_col['Area']
    col[1]=dic_col["Mean"]
    col[2]=dic_col["RawIntDen"]
    col[3]=dic_col["Slice"]
    label=sh.col_values(1,start_rowx=1)
    
    dic_channel={}
    dic_channel['F']='Far_Red'
    dic_channel['G']='rhodamine'
    

    for i in range(0,len(channel)-6,6):
        if channel[i:i+9]==[1.0,2.0,1.0]*3:
            for j in range(len(measurements)):
                m=measurements[j]
                for r in regions:
##                    print(m)
##                    print(measurements.index(m))
##                    test=input("continue ?(y/n)")
##                    if test=="n":
##                        break
                    m[temps][r].append(float(col[j][i+regions.index(r)]))
            image=label[i].split(':')[0]
            with open('//'.join(file.split("//")[:-1])+"//"+image[:-4]+".txt",'r') as ouvert:
                lignes=ouvert.read().split("\n")
                
                for l in range(len(lignes)):
                    if 'Move Channel' in lignes[l]:
                        if 'Far_Red' in lignes[l] or "rhodamin" in lignes[l]:
    
                            gain[temps][lignes[l].split('- ')[-1]].append(float(lignes[l+1].split('- ')[-1]))
                            exposure[temps][lignes[l].split('- ')[-1]].append(float(lignes[l+4].split('- ')[-1]))
 
    for m in measurements:
        for r in regions:
            if m is mean or m is intden:
                m[temps][r]=np.array(m[temps][r])/np.array(exposure[temps][dic_channel[r.split('_')[0]]])
            else:
                m[temps][r]=np.array(m[temps][r])

  
    
    
    

    
    mean[temps]['G_peri/G_noyau']=mean[temps]['G_peri']/mean[temps]['G_noyau']



    
# Cette fonction sert à importer toutes les expériences menées d'un coup en faisant appel aux fonctions New_Results()   
def Import():
    
    New_Results('Et30-0',disque+'//Etirement//2014-01-17//Et30-000//Results2.xls')
    New_Results('Et30-10',disque+'//Etirement//2014-01-17//Et30-010//Results.xls')
    New_Results('Et30-20',disque+'//Etirement//2014-01-17//Et30-020//Results.xls')
    New_Results('Et30-30',disque+'//Etirement//2014-01-20//Et30-030min//Results.xls')
    New_Results('Et30-45',disque+'//Etirement//2014-01-22//Et30-045min//Results.xls')
    New_Results('Et30-120',disque+'//Etirement//2014-01-22//Et30-120min//Results.xls')
    dic_exp_label['Et30-']='MRTF-A GFP 01-2014'
    
    New_Results('Et10-0',disque+'//Etirement//2014-04-23//Et10-000//Results.xls')
    New_Results('Et10-20',disque+'//Etirement//2014-04-23//Et10-020//Results.xls')
    New_Results('Et10-40',disque+'//Etirement//2014-04-24//Et10-040//Results.xls')
    New_Results('Et10-60',disque+'//Etirement//2014-04-24//Et10-060//Results.xls')
    New_Results('Et10-10',disque+'//Etirement//2014-04-25//Et10-010//Results.xls')
    New_Results('Et10-120',disque+'//Etirement//2014-04-25//Et10-120//Results.xls')
    dic_exp_label['Et10-']='MRTF-A GFP fin 04-2014'
    
    New_Results2('Et10-0',disque+'//Etirement//2014-04-23//Et10-000//Results_sup.xls')
    New_Results2('Et10-20',disque+'//Etirement//2014-04-23//Et10-020//Results_sup.xls')
    New_Results2('Et10-40',disque+'//Etirement//2014-04-24//Et10-040//Results_sup.xls')
    New_Results2('Et10-60',disque+'//Etirement//2014-04-24//Et10-060//Results_sup.xls')
    New_Results2('Et10-10',disque+'//Etirement//2014-04-25//Et10-010//Results_sup.xls')
    New_Results3('Et10-120',disque+'//Etirement//2014-04-25//Et10-120//Results_sup.xls')
    

    New_Results4('Et10-2-0',disque+'//Etirement//2014-04-02//Et10-000//Results.xls')
    New_Results4('Et10-2-60',disque+'//Etirement//2014-04-03//Et10-060//Results.xls')
    New_Results4('Et10-2-10',disque+'//Etirement//2014-04-02//Et10-010//Results.xls')
    New_Results4('Et10-2-20',disque+'//Etirement//2014-04-02//Et10-020//Results.xls')
    New_Results4('Et10-2-30',disque+'//Etirement//2014-04-03//Et10-030//Results.xls')
    New_Results4('Et10-2-120',disque+'//Etirement//2014-04-03//Et10-120//Results.xls')
    dic_exp_label['Et10-2-']='MRTF-A GFP début 04-2014'

    New_Results('Et10-3-20',disque+'//Etirement//2013-11-21//Et10-20min//Results.xls')
    New_Results('Et10-3-10',disque+'//Etirement//2013-11-19//Et10-10min//Results.xls')
    New_Results('Et10-3-60',disque+'//Etirement//2013-11-22//et10-60min//Results.xls')
    New_Results('Et10-3-85',disque+'//Etirement//2013-11-27//Et10-85//Results.xls')
    dic_exp_label['Et10-3-']='MRTF-A GFP 11-2013'

    New_Results('Et30-2-10',disque+'//Etirement//2013-11-08//et30-10min//Results.xls')
    New_Results('Et30-2-20',disque+'//Etirement//2013-11-07//Et30 - 20min//Results.xls')
    New_Results('Et30-2-45',disque+'//Etirement//2013-11-13//Et30-45min//Results.xls')
    New_Results('Et30-2-120',disque+'//Etirement//2013-10-29//30 - 120min//Results3.xls')
    dic_exp_label['Et30-2-']='MRTF-A GFP 10-2013'

    New_Results('Et30-3-0',disque+'//Etirement//2013-12-04//Et30-000//Results.xls')
    New_Results('Et30-3-10',disque+'//Etirement//2013-12-05//Et30-010//Results.xls')
    New_Results('Et30-3-20',disque+'//Etirement//2013-12-06//Et30-020//Results.xls')
    New_Results('Et30-3-45',disque+'//Etirement//2013-12-12//Et30-045//Results.xls')
    New_Results('Et30-3-85',disque+'//Etirement//2013-12-13//Et30-085//Results.xls')
    dic_exp_label['Et30-3-']='MRTF-A GFP 12/2013'

    New_Results4('Et10-4-0',disque+'//Etirement//2014-06-18//Et10-000//Results.xls')
    New_Results4('Et10-4-10',disque+'//Etirement//2014-06-18//Et10-010//Results.xls')
    New_Results4('Et10-4-20',disque+'//Etirement//2014-06-18//Et10-020//Results.xls')
    New_Results4('Et10-4-40',disque+'//Etirement//2014-06-18//Et10-040//Results.xls')
    New_Results4('Et10-4-60',disque+'//Etirement//2014-06-18//Et10-060//Results2.xls')
    New_Results4('Et10-4-120',disque+'//Etirement//2014-06-18//Et10-120//Results.xls')
    dic_exp_label['Et10-4-']='MRTF-A endogène 06/2014'

    New_Results4('Et30-4-0',disque+'//Etirement//2014-06-19//Tableau0\'.xls')
    New_Results4('Et30-4-10',disque+'//Etirement//2014-06-19//Tableau10\'.xls')
    New_Results4('Et30-4-20',disque+'//Etirement//2014-06-19//Tableau20\'.xls')
    New_Results4('Et30-4-40',disque+'//Etirement//2014-06-19//Tableau40\'.xls')
    New_Results4('Et30-4-60',disque+'//Etirement//2014-06-19//Tableau60\'.xls')
    New_Results4('Et30-4-120',disque+'//Etirement//2014-06-19//Tableau120\'.xls')
    dic_exp_label['Et30-4-']='MRTF-A endogène 06/2014'

    New_Results4('Et0-temoin',disque+'//Etirement//2014-11-14//temoin fixees ds le puit 2//Results.xls')
    New_Results4('Et0-montee-0',disque+'//Etirement//2014-11-14//temoin fixee immediatement apres montage//Results.xls')
    New_Results4('Et0-montee-60',disque+'//Etirement//2014-11-14//temoin fixee apres 1h de montage//Results.xls')
    New_Results4('Et0-temoin-2-',disque+'//Etirement//2014-11-24//temoin fixee dans le puit//Results.xls')
    New_Results4('Et0-montee-2-60',disque+'//Etirement//2014-11-24//temoin montee et fixee apres 1h//Results.xls')

    New_Results4('Et0-temoin-3-',disque+'//Etirement//2014-11-26//Et0-temoin ds le puit//set2//Results.xls')
    New_Results4('Et10-20-5',disque+'//Etirement//2014-11-26//Et10-20min-fixee en etirement//Results.xls')
    
# Cette fonction sert à compter et tracer les répartitions CHN et les histogrames de MRTF-A ratio, F/G ratio et G_peri/G_noyau pour trois expériences
# dont les réféfences sont listées dans liste_ord
# Seuil1 est le seuil de MRTF-A ratio en-dessous duquel la cellule est considérée comme nucléaire
# Seuil2 celui au-dessus duquel elle est considérée comme cytoplasmique
def Comptage(liste_ord,seuil1,seuil2):

    print(liste_ord)
    data_C=np.zeros(len(liste_ord))
    data_H=np.zeros(len(liste_ord))
    data_N=np.zeros(len(liste_ord))
    data_Total=np.zeros(len(liste_ord))
    print(data_C)
    color_list=['red','orange','green','blue','purple','black']
    
    
    for key in liste_ord:
        print(key)
        condition1=(mean[key]['MRTFA_ratio']<seuil1)
        condition2=(mean[key]['MRTFA_ratio']>seuil1)*(mean[key]['MRTFA_ratio']<seuil2)
        condition3=(mean[key]['MRTFA_ratio']>seuil2)
        data_C[liste_ord.index(key)]=condition3.sum()
        data_H[liste_ord.index(key)]=condition2.sum()
        data_N[liste_ord.index(key)]=condition1.sum()
        data_Total[liste_ord.index(key)]=condition1.sum()+condition2.sum()+condition3.sum()

    data_C/=data_Total
    data_H/=data_Total
    data_N/=data_Total

    data_FG=[]
    data_G=[]
    data_MRTFA=[]
    for key in liste_ord:
        data_FG.append(mean[key]['F_tot/G_tot'])
        data_G.append(mean[key]['G_noyau']/mean[key]['G_peri'])
        data_MRTFA.append(intden[key]['MRTFA_ratio'])
        
    

    ind=np.arange(data_Total.size)

    pl.subplot(4,3,1)
    pl.bar(ind[:6],data_C[:6],color='red')
    pl.bar(ind[:6],data_H[:6],color='green',bottom=data_C[:6])
    pl.bar(ind[:6],data_N[:6],color='blue',bottom=(data_H+data_C)[:6])
    pl.xticks(ind[:6]+0.4,liste_ord[:6])
    pl.title('Etirement 10 - 4 %')

    pl.subplot(4,3,2)
    pl.bar(ind[6:12],data_C[6:12],color='red')
    pl.bar(ind[6:12],data_H[6:12],color='green',bottom=data_C[6:12])
    pl.bar(ind[6:12],data_N[6:12],color='blue',bottom=(data_H+data_C)[6:12])
    pl.xticks(ind[6:12]+0.4,liste_ord[6:12])
    pl.title('Etirement 30 % -4 ')

    pl.subplot(4,3,3)
    pl.bar(ind[12:],data_C[12:],color='red')
    pl.bar(ind[12:],data_H[12:],color='green',bottom=data_C[12:])
    pl.bar(ind[12:],data_N[12:],color='blue',bottom=(data_H+data_C)[12:])
    pl.xticks(ind[12:]+0.4,liste_ord[12:])
    pl.title('Etirement 30 % - 4 ')

    pl.subplot(4,3,4)
    color_index=0
    for cur_data in data_MRTFA[:6]:
        pl.plot(np.sort(cur_data),
                np.arange(cur_data.size)/cur_data.size,
                color=color_list[color_index],
                label=liste_ord[color_index]+' min')
        color_index+=1
    pl.xlim((0,2))
    pl.ylabel('Ratio MRTFA_cyto/MRTFA_noyau')
    pl.legend(loc='lower right',fontsize='small')

    pl.subplot(4,3,5)
    color_index=0
    for cur_data in data_MRTFA[6:12]:
        pl.plot(np.sort(cur_data),
                np.arange(cur_data.size)/cur_data.size,
                color=color_list[color_index],
                label=liste_ord[color_index]+' min')
        color_index+=1
    pl.xlim((0,2))
    pl.ylabel('Ratio MRTFA_cyto/MRTFA_noyau')
    pl.legend(loc='lower right',fontsize='small')

    pl.subplot(4,3,6)
    color_index=0
    for cur_data in data_MRTFA[12:]:
        pl.plot(np.sort(cur_data),
                np.arange(cur_data.size)/cur_data.size,
                color=color_list[color_index],
                label=liste_ord[color_index]+' min')
        color_index+=1
    pl.xlim((0,2))
    pl.ylabel('Ratio MRTFA_cyto/MRTFA_noyau')
    pl.legend(loc='lower right',fontsize='small')
        

    pl.subplot(4,3,7)
    color_index=0
    for cur_data in data_FG[:6]:
        pl.plot(np.sort(cur_data),
                np.arange(cur_data.size)/cur_data.size,
                color=color_list[color_index],
                label=liste_ord[color_index]+' min')
        
        color_index+=1
    pl.xlim((0,8))
    pl.ylabel('Ratio F/G total')
    pl.legend(loc='lower right',fontsize='small')
   
    
    pl.subplot(4,3,8)
    color_index=0
    for cur_data in data_FG[6:12]:
        pl.plot(np.sort(cur_data),
                np.arange(cur_data.size)/cur_data.size,
                color=color_list[color_index],
                label=liste_ord[color_index]+' min')
        color_index+=1
    pl.xlim((0,8))
    pl.ylabel('Ratio F/G total')
    pl.legend(loc='lower right',fontsize='small')

    pl.subplot(4,3,9)
    color_index=0
    for cur_data in data_FG[12:]:
        pl.plot(np.sort(cur_data),
                np.arange(cur_data.size)/cur_data.size,
                color=color_list[color_index],
                label=liste_ord[color_index]+' min')
        color_index+=1
    pl.xlim((0,8))
    pl.ylabel('Ratio F/G total')
    pl.legend(loc='lower right',fontsize='small')

    pl.subplot(4,3,10)
    color_index=0
    for cur_data in data_G[:6]:
        pl.plot(np.sort(cur_data),
                np.arange(cur_data.size)/cur_data.size,
                color=color_list[color_index],
                label=liste_ord[color_index]+' min')
        color_index+=1
    pl.xlim((0,5))
    pl.ylabel('Ratio G_noyau/G_total')
    pl.legend(loc='lower right',fontsize='small')

    
    pl.subplot(4,3,11)
    color_index=0
    for cur_data in data_G[6:12]:
        pl.plot(np.sort(cur_data),
                np.arange(cur_data.size)/cur_data.size,
                color=color_list[color_index],
                label=liste_ord[color_index]+' min')
        color_index+=1
    pl.xlim((0,5))
    pl.ylabel('Ratio G_noyau/G_total')
    pl.legend(loc='lower right',fontsize='small')

    pl.subplot(4,3,12)
    color_index=0
    for cur_data in data_G[12:]:
        pl.plot(np.sort(cur_data),
                np.arange(cur_data.size)/cur_data.size,
                color=color_list[color_index],
                label=liste_ord[color_index]+' min')
        color_index+=1
    pl.xlim((0,5))
    pl.ylabel('Ratio G_noyau/G_total')
    pl.legend(loc='lower right',fontsize='small')

    pl.show()

    return data_C,data_H,data_N

#Hist_cum sert à tracer les histogrammes cumulés pour tous les temps d'une expérience, pour plusieurs expériences.
# Value string indique si l'on veut tracer les aires, les moyennes d'intensité par pixel ('mean'), ou les intensités totales cumulées
# Experiment_list contient la liste des références des expériences à tracer sans les temps, par exemple 'Et10-' ou 'Et30-4-'
# Parameter contient la région que l'on souhaite tracer (par exemple 'MRTF-A peri', 'F_tot'...)
def Hist_cum(value_string,experiment_list,parameter):
    color_list=['red','orange','lightgreen','darkgreen','blue','darkblue','pink','purple','black']
    time_list=[0,10,20,30,40,45,60,85,120] #contient tous les temps possibles
    value=dic_value[value_string] # Appel du dictionnaire principal 
    i=0
    # On parcourt la liste de toutes les expériences à tracer
    for liste in experiment_list:
        pl.subplot(len(experiment_list),1,i+1) # On crée un subplot par expérience
        pl.title(liste+' - '+value_string+' - '+parameter)
        
        for time in time_list:
            key=liste+str(time)
            table=value.get(key,{}) # l'usage de value.get permet de ne pas obtenir une erreur si la clé n'est pas référencée dans le dictionnaire
            # Ici c'est nécessaire car toutes les expériences ne contiennent pas tous les temps
            # On veut donc obtenir un dictionnaire vide si jamais une référence n'existe pas
            
            
            pl.plot(np.sort(table.get(parameter,np.array([0]))),
                    np.arange(table.get(parameter,np.array([0])).size)/table.get(parameter,np.array([0])).size,
                    color=color_list[time_list.index(time)],
                    label=str(time)+' min')
        pl.legend(loc='lower right')
        i+=1

    pl.show()
            
# Cette fonction sert à comparer les données d'un tabeau en séparant les données en fonction du numéro de slice sur laquelle elles sont été prises
def Comparaison_experimentateur(value,key,parameter):
	pl.plot(np.sort(value[key][parameter][sl[key][parameter]<11]),
                np.arange(value[key][parameter][sl[key][parameter]<11].size)/value[key][parameter][sl[key][parameter]<11].size,
                'ro')
	pl.plot(np.sort(value[key][parameter][sl[key][parameter]>10]),
                np.arange(value[key][parameter][sl[key][parameter]>10].size)/value[key][parameter][sl[key][parameter]>10].size
                ,'bo')
	

        
def BoxPlotsColors(data,color):
    # Generate some data from five different probability distributions,
    # each with different characteristics. We want to play with how an IID
    # bootstrap resample of the data preserves the distributional
    # properties of the original sample, and a boxplot is one visual tool
    # to make this assessment
    numDists = len(data)
    
    fig, ax1 = plt.subplots(figsize=(10,6))
    fig.canvas.set_window_title('F/G intensity ratio')
    plt.subplots_adjust(left=0.075, right=0.95, top=0.9, bottom=0.25)

    bp = plt.boxplot(data, notch=0, sym='+', vert=1, whis=1.5)
    plt.setp(bp['boxes'], color='black')
    plt.setp(bp['whiskers'], color='black')
    plt.setp(bp['fliers'], color='red', marker='+')

    # Add a horizontal grid to the plot, but make it very light in color
    # so we can use it for reading data values but not be distracting
    ax1.yaxis.grid(True, linestyle='-', which='major', color='lightgrey',
                  alpha=0.5)

    # Hide these grid behind plot objects
    ax1.set_axisbelow(True)
    ax1.set_title('Normalized F/G actin intensity ratio for 30% Strain')
    ax1.set_xlabel('Time in minutes')
    ax1.set_ylabel('Normalized F/G actin intensity')

    # Now fill the boxes with desired colors
    boxColors = color
    numBoxes = numDists
    medians = range(numBoxes)
    for i in range(numBoxes):
      box = bp['boxes'][i]
      boxX = []
      boxY = []
      for j in range(5):
          boxX.append(box.get_xdata()[j])
          boxY.append(box.get_ydata()[j])
      boxCoords = np.vstack((np.array(boxX),np.array(boxY)))
      boxCoords=np.transpose(boxCoords)
      # Alternate between Dark Khaki and Royal Blue
      k=i%(len(color))
      boxPolygon = Polygon(boxCoords, facecolor=boxColors[k])
      ax1.add_patch(boxPolygon)
      # Now draw the median lines back over what we just filled in
      med = bp['medians'][i]
      medianX = []
      medianY = []
      for j in range(2):
          medianX.append(med.get_xdata()[j])
          medianY.append(med.get_ydata()[j])
          plt.plot(medianX, medianY, 'k')
          #medians[i] = medianY[0]
      # Finally, overplot the sample averages, with horizontal alignment
      # in the center of each box
      plt.plot([np.average(med.get_xdata())], [np.average(data[i])],
               color='w', marker='*', markeredgecolor='k')
            

# Export permet de créer des tab-delimited text qui contiennent toutes les données récoltées et extraites durant Import()         
def Export():
    liste_value=['aire','mean','intden','slice']
    values=[aire,mean,intden,sl]
    for value in values:
        value_str=liste_value[values.index(value)]
        for time in value.keys():
            # Ici pour chaque temps dans chaque expérience, on va créer un nouveau fichier et l'ouvrir pour écrire dedans
            # L'utilisation de la syntaxe with open(path) as file permet de fermer le fichier même si le script plante en cours d'exécution
            with open(disque+'//Etirement//'+str(value_str)+'_'+str(time)+'.txt','a') as file:
                print(disque+'//Etirement//'+str(value_str)+'_'+str(time)+'.txt')

                # On commence par écrire l'intitulé de chaque colonne
                for region in regions:
                    file.write(str(region)+'\t')
                    
                file.write('\n')

                # On peut ensuite remplir le tableau ligne par ligne
                for i in range(1,value[time][region].size):
                    for region in regions:
                        
                        file.write(str(value[time][region][i])+'\t')
                    file.write('\n')


def Medianes(value_string,experiment_list,parameter_list):
    time_list=[0,10,20,30,40,45,60,85,120] #contient tous les temps possibles
    value=dic_value[value_string] # Appel du dictionnaire principal
    color_list=['lightblue','blue','purple','black','pink','red','orange','yellow']
    i=0
    FG_tot_medianes=[]
    FG_tot_quartiles=[]
    MRTFA_ratio_medianes=[]
    MRTFA_ratio_quartiles=[]
    temps_liste=[]
    # On parcourt la liste de toutes les expériences à tracer
    for parameter in parameter_list:
        #pl.subplot(len(parameter_list),1,i+1) # On crée un subplot par paramètre
        pl.title(value_string+' - '+parameter)

        for liste in experiment_list:    
            medianes=[]
            quartiles=[]
            temps=[]
            for time in time_list:
                key=liste+str(time)
                table=value.get(key,{}) # l'usage de value.get permet de ne pas obtenir une erreur si la clé n'est pas référencée dans le dictionnaire
                # Ici c'est nécessaire car toutes les expériences ne contiennent pas tous les temps
                # On veut donc obtenir un dictionnaire vide si jamais une référence n'existe pas
                mediane=np.median(table.get(parameter,np.array([0])))
                quartile=np.percentile(table.get(parameter,np.array([0])),25)
                if mediane:
                    medianes.append(mediane)
                    temps.append(time)
                    quartiles.append(quartile)
            #pl.errorbar(temps,medianes,yerr=np.array(medianes)-np.array(quartiles),color=color_list[experiment_list.index(liste)],label=str(liste))
            pl.plot(temps,np.array(medianes),color=color_list[experiment_list.index(liste)],label=str(liste))
            pl.plot(temps,np.array(medianes),'o',color=color_list[experiment_list.index(liste)],label=str(liste))

            pl.legend(loc='lower right')
            if parameter=='F/G_tot' and len(medianes)!=0:
                FG_tot_medianes.append(medianes)
                FG_tot_quartiles.append(quartile)
                temps_liste.append(temps)
                
                
            if parameter=='MRTFA_ratio'and len(medianes)!=0:
                MRTFA_ratio_medianes.append(medianes)
                MRTFA_ratio_quartiles.append(quartile)
    
    

        pl.show()
    if 'F/G_tot' in parameter_list and 'MRTFA_ratio' in parameter_list:
        fig,ax1=pl.subplots()
        ax2=ax1.twinx()
        lines=[]
        labels=[]
        for liste in experiment_list:
            #pl.errorbar(FG_tot_medianes[experiment_list.index(liste)],
            #            MRTFA_ratio_medianes[experiment_list.index(liste)],
            #            xerr=np.array(FG_tot_medianes[experiment_list.index(liste)])-np.array(FG_tot_quartiles[experiment_list.index(liste)]),
            #            yerr=np.array(MRTFA_ratio_medianes[experiment_list.index(liste)])-np.array(MRTFA_ratio_quartiles[experiment_list.index(liste)]),
            #            color=color_list[experiment_list.index(liste)],label=str(liste))
            
            l1=ax1.plot(temps_liste[experiment_list.index(liste)],FG_tot_medianes[experiment_list.index(liste)],color=color_list[experiment_list.index(liste)],label=str(liste))
            
            l2=ax2.plot(temps_liste[experiment_list.index(liste)],MRTFA_ratio_medianes[experiment_list.index(liste)],'--',color=color_list[experiment_list.index(liste)],label=str(liste))
            lines=lines+l1+l2
        labels=[l.get_label() for l in lines]
            
        ax=fig.add_subplot(111)
        ax.legend(lines,labels)
        pl.show()

def Comparaison(value_string,experiment_list,parameter_list,seuil1,seuil2):
    time_list=[0,10,20,30,40,45,60,85,120] #contient tous les temps possibles
    value=dic_value[value_string] # Appel du dictionnaire principal
    color_list=['red','orange','green','darkgreen','lightblue','blue','purple','black']
    nb_line=len(parameter_list)
    nb_col=len(experiment_list)
    i=1

    for experiment in experiment_list:
        data_C=[]
        data_H=[]
        data_N=[]
        data_Total=[]
        temps=[]

        for time in time_list:
            table=value.get(experiment+str(time),{}) # l'usage de value.get permet de ne pas obtenir une erreur si la clé n'est pas référencée dans le dictionnaire
            # Ici c'est nécessaire car toutes les expériences ne contiennent pas tous les temps
            # On veut donc obtenir un dictionnaire vide si jamais une référence n'existe pas
            if table.get('MRTFA_ratio',np.array([])).size:        
                condition1=(table['MRTFA_ratio']<seuil1)
                condition2=(table['MRTFA_ratio']>seuil1)*(table['MRTFA_ratio']<seuil2)
                condition3=(table['MRTFA_ratio']>seuil2)
                data_C.append(condition3.sum())
                data_H.append(condition2.sum())
                data_N.append(condition1.sum())
                data_Total.append(condition1.sum()+condition2.sum()+condition3.sum())
                temps.append(time)
            
        data_C=np.array(data_C)
        data_H=np.array(data_H)
        data_N=np.array(data_N)
        data_Total=np.array(data_Total)
        print(data_C)
        print(data_H)
        print(data_N)
        data_C=data_C/data_Total
        data_H=data_H/data_Total
        data_N=data_N/data_Total
        print(data_C)
        

        
        pl.subplot(nb_line,nb_col,i)
        
        pl.plot(temps,data_C,color='red',label='Cytoplasmic MRTF-A')
        pl.plot(temps,data_C,'o',color='red')
        pl.plot(temps,data_H,color='green',label='Homogeneous MRTF-A')
        pl.plot(temps,data_H,'o',color='green')
        pl.plot(temps,data_N,color='blue',label='Nuclear MRTF-A')
        pl.plot(temps,data_N,'o',color='blue')
        pl.title(experiment)
        
        
        
        

        i+=1
    
    
    
    for parameter in ['F_tot/G_tot']:
        
        for experiment in experiment_list:
            pl.subplot(nb_line,nb_col,i)
            pl.xlabel('Time from the beginning of stretching, in minutes')
            pl.ylabel('Cytoplasmic/Nuclear MRTF-A ratio and F-actin/G-actin ratio')
            
            medianes=[]
            quartiles=[]
            temps=[]
            for time in time_list:
                key=experiment+str(time)
                table=value.get(key,{}) # l'usage de value.get permet de ne pas obtenir une erreur si la clé n'est pas référencée dans le dictionnaire
                # Ici c'est nécessaire car toutes les expériences ne contiennent pas tous les temps
                # On veut donc obtenir un dictionnaire vide si jamais une référence n'existe pas
                mediane=np.median(table.get(parameter,np.array([0])))
                quartile=np.percentile(table.get(parameter,np.array([0])),25)
                if mediane:
                    medianes.append(mediane)
                    temps.append(time)
                    quartiles.append(quartile)
            #pl.errorbar(temps,medianes,yerr=np.array(medianes)-np.array(quartiles),color=color_list[experiment_list.index(experiment)],label=str(experiment))
            
            pl.plot(temps,medianes,color=color_list[experiment_list.index(experiment)+1],label='F/G ratio')
            pl.plot(temps,medianes,'o',color=color_list[experiment_list.index(experiment)+1])
            
                

            
            
            i=i+1
        
        pl.legend()
    pl.show()
        
def Comparaison_live(etirement,experiment_list,seuil1,seuil2):


    

    liste_date=['2013-06-26 14:00','2013-06-26 16:29','2013-06-25','2013-06-25','2013-06-28 14:00','2013-07-02 13:45','2013-07-02 16:00','2013-07-04 15:55','2013-07-04 13:37','2013-07-09 10:38','2013-07-09 12:43','2013-07-10 10:39','2013-07-10 12:45','2013-07-12 10:28','2013-07-12 12:40','lamelle1 13:00','lamelle1 15:00','2013-09-13 12:55','2013-09-13 15:05','2013-09-17 13:55','2013-09-17 16:00','2013-09-18 13:49','2013-09-18 16:00']
    time_list=[0,10,20,30,40,45,60,85,120] #contient tous les temps possibles
    result=cur.execute("SELECT Experiments.date FROM Experiments")
    for r in result:
        liste_date.append(r[0])

    data_C=[]
    data_H=[]
    data_N=[]
    
    for m in time_list:
        c_tab=[]
        h_tab=[]
        n_tab=[]
        d_tab=[]
        total_tab=[]
        for date in liste_date:
                
            
            colonnes="Cellules.etat0,Cellules.temps0"
            for j in range(1,7):
                colonnes=colonnes+",Cellules.etat"+str(j)+","+"Cellules.temps"+str(j)
            colonnes=colonnes+",Cellules.etatf,Cellules.tempsf,Cellules.Cell_ID"

            if m==0:
                
                result=cur.execute("SELECT "+"Experiments.init_a0_c,Experiments.init_a0_h,Experiments.init_a0_n"+" FROM Experiments WHERE Experiments.etirement=10 "+" AND Experiments.date='"+date+"'")
                for r in result:
                    
                    
                    if r[1]:
                        c_tab.append(int(r[0]))
                        h_tab.append(int(r[1]))
                        n_tab.append(int(r[2]))
                        total_tab.append(r[0]+r[1]+r[2])
                print(c_tab)
            


            


            #print("SELECT "+self.colonnes+self.selection1.selection.get()+" AND Experiments.date='"+date+"'")
            else:
                dic=[]
                dic_trans=[]
                for minute in range(140,-1,-1):
                    dic.append({})
                    dic_trans.append({})

                result=cur.execute("SELECT "+colonnes+" FROM Experiments,Zones,Cellules WHERE Cellules.Zone_ID=Zones.Zone_ID AND Zones.Exp_ID=Experiments.Exp_ID  AND Experiments.etirement="
                                   +str(etirement)
                                   +" AND Cellules.Actine_MCherry=0"+" AND Experiments.date='"+date+"'")
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
                            #self.dic[minute][r[14-n]]=self.dic[minute].get(r[14-n],0)+1
                            if n<14 and n>0:
                                dic[minute][r[12-n]+r[14-n]]=dic[minute].get(r[12-n]+r[14-n],0)+1
                                if r[14-n]!=r[12-n] and int(r[15-n])==minute:
                                    #print(n)
                                    dic_trans[minute][r[12-n]+r[14-n]]=dic_trans[minute].get(r[12-n]+r[14-n],0)+1
                                    
                            else :
                                dic[minute][r[14-n]]=dic[minute].get(r[14-n],0)+1
    ##            print(self.dic[m].get('c',0))
                if dic[m].get('c',0)!=0:
    ##                print(dic[m].get('c',0))
    ##                print(dic[m].get('hc',0))
    ##                print(dic[m].get('nc',0))
    ##                print(dic[m].get('h',0))
    ##                print(dic[m].get('ch',0))
    ##                print(dic[m].get('nh',0))
    ##                print(dic[m].get('n',0))
    ##                print(dic[m].get('hn',0))
    ##                print(dic[m].get('cn',0))
    ##                print(dic[m].get('d',0))
                    
                    c_tab.append(dic[m].get('c',0)+dic[m].get('hc',0)+dic[m].get('nc',0))
                    h_tab.append(dic[m].get('h',0)+dic[m].get('ch',0)+dic[m].get('nh',0))
                    n_tab.append(dic[m].get('n',0)+dic[m].get('hn',0)+dic[m].get('cn',0))
                    d_tab.append(dic[m].get('d',0)+dic[m].get('cd',0)+dic[m].get('hd',0)+dic[m].get('nd',0))
                    total=0
                    
                    for key in dic[m].keys():
    ##                    print(key)
                        total=dic[m].get(key,0)+total
    ##                    print(total)
                    total_tab.append(total)
                  
                   

        

            
        c_moy=0
        h_moy=0
        n_moy=0
        d_moy=0
        c_err=0
        h_err=0
        n_err=0
        total=0

        total=sum(total_tab)

        if len(c_tab)*len(h_tab)*len(n_tab)*len(total_tab)!=0:
            
            
            c_moy=sum(c_tab)/(total)

            c_err=sum((np.array(c_tab)/np.array(total_tab)-c_moy)**2)
            c_err=((1/(len(c_tab)-1)*c_err)**(1/2))/(len(c_tab)**1/2)

            h_moy=sum(h_tab)/(total)

            h_err=sum((np.array(h_tab)/np.array(total_tab)-h_moy)**2)
            h_err=((1/(len(h_tab)-1)*h_err)**(1/2))/(len(h_tab)**1/2)

            n_moy=sum(n_tab)/(total)

            n_err=sum((np.array(n_tab)/np.array(total_tab)-n_moy)**2)
            n_err=((1/(len(n_tab)-1)*n_err)**(1/2))/(len(n_tab)**1/2)
            


            print("m="+str(m))
            print("C="+str(c_moy*100)[:5])
            print("err_C="+str(c_err*100)[:5])
            print("H="+str(h_moy*100)[:5])
            print("err_H="+str(h_err*100)[:5])
            print("N="+str(n_moy*100)[:5])
            print("err_N="+str(n_err*100)[:5])
            print("D="+str(d_moy*100)[:5])
            print(c_moy+h_moy+n_moy+d_moy)
            print(len(c_tab))

            data_C.append(c_moy)
            data_H.append(h_moy)
            data_N.append(n_moy)
            
            
        else:
            print("Toutes les valeurs sont nulles")
        
                
  
    print(data_C)
    print(data_H)
    print(data_N)

    fig,ax1=pl.subplots()
    ax1.bar(np.array(time_list),data_C,color='pink',width=4)
    ax1.bar(np.array(time_list),data_H,color='lightgreen',bottom=data_C,width=4)
    ax1.bar(np.array(time_list),data_N,color='lightblue',bottom=(np.array(data_H)+np.array(data_C)),width=4)
    ax1.set_xlabel('time (minutes)')
    ax1.set_ylabel('Proportion in Live')
    pl.title('Comparaison des expériences en Live et Fixées Etirement='+str(etirement)+'%')
        
        
    
    value=dic_value['mean'] # Appel du dictionnaire principal
    color_list=['red','green','blue','black']

    
    
    nb_col=len(experiment_list)
    i=1
    ax2=ax1.twinx()
    ax2.set_ylabel('MRTFA_ratio in fixed experiments')
    for experiment in experiment_list:
        data_C=np.zeros(len(time_list))
        data_H=np.zeros(len(time_list))
        data_N=np.zeros(len(time_list))
        data_Total=np.ones(len(time_list))
        medianes=[]
        temps=[]
        quartiles=[]

        for time in time_list:
            table=value.get(experiment+str(time),{}) # l'usage de value.get permet de ne pas obtenir une erreur si la clé n'est pas référencée dans le dictionnaire
            # Ici c'est nécessaire car toutes les expériences ne contiennent pas tous les temps
            # On veut donc obtenir un dictionnaire vide si jamais une référence n'existe pas
            if table.get('MRTFA_ratio',np.array([])).size:        
                condition1=(table['MRTFA_ratio']<seuil1)
                condition2=(table['MRTFA_ratio']>seuil1)*(table['MRTFA_ratio']<seuil2)
                condition3=(table['MRTFA_ratio']>seuil2)
                data_C[time_list.index(time)]=condition3.sum()
                data_H[time_list.index(time)]=condition2.sum()
                data_N[time_list.index(time)]=condition1.sum()
                data_Total[time_list.index(time)]=condition1.sum()+condition2.sum()+condition3.sum()
                mediane=np.median(table.get('MRTFA_ratio',np.array([0])))
                quartile=np.percentile(table.get('MRTFA_ratio',np.array([0])),25)
                if mediane:
                    medianes.append(mediane)
                    temps.append(time)
                    quartiles.append(quartile)

        data_C/=data_Total
        data_H/=data_Total
        data_N/=data_Total

##        pl.subplot(len(experiment_list)+1,1,1)
##        pl.bar(time_list,data_C,color='red',width=4)
##        pl.bar(time_list,data_H,color='green',bottom=data_C,width=4)
##        pl.bar(time_list,data_N,color='blue',bottom=(np.array(data_H)+np.array(data_C)),width=4)
##        pl.title(experiment)
##        print(data_Total)
        

        #ax2.errorbar(temps,medianes,yerr=np.array(medianes)-np.array(quartiles),color=color_list[experiment_list.index(experiment)],label=str(experiment))
        ax2.plot(temps,medianes,color=color_list[experiment_list.index(experiment)],label=dic_exp_label[experiment])
        ax2.plot(temps,medianes,'o',color=color_list[experiment_list.index(experiment)])
        ax2.set_ylim(0.5,1.5)
        
    pl.legend()
        
def Medianes2(value_string,experiment_list):
    parameter_list=['MRTFA_ratio','F_tot/G_tot']
    time_list=[0,10,20,30,40,45,60,85,120] #contient tous les temps possibles
    value=dic_value[value_string] # Appel du dictionnaire principal
    color_list=['lightblue','blue','purple','black','pink','red','orange','yellow']
    i=0
    FG_tot_medianes=[]
    FG_tot_quartiles=[]
    MRTFA_ratio_medianes=[]
    MRTFA_ratio_quartiles=[]
    temps_liste=[]
    fig,ax1=pl.subplots()
    ax2=ax1.twinx()
    # On parcourt la liste de toutes les expériences à tracer
    for parameter in parameter_list:
        #pl.subplot(len(parameter_list),1,i+1) # On crée un subplot par paramètre
        
        line_list=[]
        for liste in experiment_list:    
            medianes=[]
            quartiles=[]
            temps=[]
            
            for time in time_list:
                key=liste+str(time)
                table=value.get(key,{}) # l'usage de value.get permet de ne pas obtenir une erreur si la clé n'est pas référencée dans le dictionnaire
                # Ici c'est nécessaire car toutes les expériences ne contiennent pas tous les temps
                # On veut donc obtenir un dictionnaire vide si jamais une référence n'existe pas
                mediane=np.median(table.get(parameter,np.array([0])))
                quartile=np.percentile(table.get(parameter,np.array([0])),25)
                if mediane:
                    medianes.append(mediane)
                    temps.append(time)
                    quartiles.append(quartile)
            print(temps)
            if parameter_list.index(parameter)==0:
                line_list+=(ax1.plot(temps,medianes,color=color_list[experiment_list.index(liste)],label=str(liste)))
            elif parameter_list.index(parameter)==1:
                
                line_list+=(ax2.plot(temps,medianes,color=color_list[experiment_list.index(liste)+4],label=str(liste)))
                
                
            #pl.errorbar(temps,medianes,yerr=np.array(medianes)-np.array(quartiles),color=color_list[experiment_list.index(liste)],label=str(liste))
##            pl.plot(temps,np.array(medianes),color=color_list[experiment_list.index(liste)],label=str(liste))
##            pl.plot(temps,np.array(medianes),'o',color=color_list[experiment_list.index(liste)],label=str(liste))

    ax1.set_xlabel("Time from the beginning of stretching in minutes")
    ax1.set_ylabel("Cytoplasmic/Nuclear MRTFA fluorescence ratio")
    ax2.set_ylabel("F-actin/G-actin fluorescence ratio")
    print(line_list)
    labels=[l.get_label() for l in line_list]
    ax=fig.add_subplot(111)
    ax.legend(line_list,labels)
    ax1.set_title("30\% stretching experiments")
    pl.show()
          

temoins=['Et0-temoin','Et0-temoin-2-','Et0-temoin-3-','Et0-montee-0','Et0-montee-60','Et0-montee-2-60','Et10-20-5']
colors=['pink','red','orange','green','lightblue','blue','black']
def plot_temoins(parameters):
	for parameter in parameters:
		pl.subplot(len(parameters),1,parameters.index(parameter)+1)
		pl.title(parameter)
		for exp in temoins:
			pl.plot(np.sort(mean[exp][parameter]),
				np.arange(mean[exp][parameter].size)/mean[exp][parameter].size,
				color=colors[temoins.index(exp)],
				label=exp)
		pl.legend()

		

        

        
        
        

   
        
    

    


                    
