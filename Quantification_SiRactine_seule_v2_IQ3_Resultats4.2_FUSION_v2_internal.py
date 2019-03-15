from os import getcwd,chdir,listdir,mkdir,makedirs
from shutil import copyfile
import xlrd
import numpy as np
import matplotlib.pyplot as pl
import random


#savepath="//Users//lorraine//Documents//SaveThese//"
class Experiment(object):
   def __init__(self,folder,time,ch):
      chdir(folder)
      file_list=listdir()
      self.zones={}
      #print(savepath+folder.split("//")[6]+"//"+folder.split("//")[7])
      #makedirs(savepath+"//".join(folder.split("//")[6:]))
      for file in file_list:
         if '.xls' in file:
            self.zones[file[1:3]]=Zone(file,time,ch)
            #copyfile(folder+file,savepath+"//".join(folder.split("//")[6:])+file)
         elif ".txt" in file:
            #copyfile(folder+file,savepath+"//".join(folder.split("//")[6:])+file)             
            

      self.dic_cell={}
      for key in self.zones.keys():
         zone=self.zones[key]
         for cell in zone.cells:
            self.dic_cell['z'+zone.file[1:3]+'c'+str(zone.cells.index(cell))]=cell
      

class Zone(object):
   def __init__(self,file,time,ch):
      self.file=file
      self.time=time
      workbook=xlrd.open_workbook(file)
      for sheetname in workbook.sheet_names():
         sh=workbook.sheet_by_name(sheetname)
         self.dic_col={}
         for col_name in sh.row_values(rowx=0):
            self.dic_col[col_name]=sh.col_values(sh.row_values(rowx=0).index(col_name),start_rowx=1)

         self.cells=[]
         self.st_slices=[0]
         s=self.dic_col['Slice']
         #print(s)
         
         for i in range(len(self.dic_col['Slice'])-1):
            if s[i+1]-s[i]<0:
               #print(s[i+1])
               #print(s[i])
               #print(i+1)
               self.st_slices.append(i+1)
         self.st_slices.append(len(s))
         #print(self.st_slices)
         print(file)

         for i in range(len(self.st_slices)-1):
            self.cells.append(Cellule(self.time,self.dic_col,self.st_slices[i],self.st_slices[i+1],ch))
         

         
class Cellule(object):
   def __init__(self,time,dic_col,starting_slice,ending_slice,ch):
      self.time=int(time[:2])*60+int(time[3:])
      self.dic_col=dic_col
      self.starting_slice=starting_slice
      self.ending_slice=ending_slice
      self.ch=ch
      self.dic_parametre={}
      self.time_list=[]
      for cle in ['Area','Minor','Major','Angle','Mean','RawIntDen']:
         self.dic_parametre[cle]={}
      self.geometrie=['Area','Minor','Major','Angle']
      self.couleur=['Mean','RawIntDen']
      if ch==1:
         self.regions=['tc']
      else:
         self.regions=['tc','nc','pc']
      self.exposure={}
      for region in self.regions:
         for cle in self.geometrie:
            self.dic_parametre[cle][region]=[]
            
      if self.ch==1:
         self.couleurs=['tc_v']
         self.exposure["Far_Red"]=[]
         self.sequence=[1.0]*len(self.regions)
      if self.ch==2:
         self.couleurs=['tc_r','tc_v','nc_r','nc_v','pc_r','pc_v']
         self.exposure['GFP']=[]
         self.exposure['Far_Red']=[]
         self.sequence=[1.0,2.0]*len(self.regions)
      if self.ch==0:
         self.couleurs=['tc_v','nc_v','pc_v']
         self.exposure['GFP']=[]
         self.sequence=[1.0]*len(self.couleurs)
      for cle in self.couleur:
         for region in self.couleurs:
            self.dic_parametre[cle][region]=[]
               
      label=dic_col["Label"]
      self.label=[]
      check_region=0
      
      for i in range(starting_slice,ending_slice,max(self.ch,1)):
         check=False
##         print(i)
         
         if i+len(self.regions)*max(self.ch,1)-check_region*max(self.ch,1)<=ending_slice :
            if dic_col['Ch'][i:i+len(self.regions)*max(self.ch,1)-check_region*max(self.ch,1)]==self.sequence[check_region*max(self.ch,1):]:
               check=True
            else:
               check=False
         else:
            check=False

##         print(check)
         if check:
            if check_region==0:
               raw_time=label[i].split('_')[-1].split('.')[0].split(' ')[0]
               #print(raw_time)
               #print(len(label[i].split('_')[-1].split(' ')))
               if len(label[i].split('_')[-1].split('.')[0].split(' '))>1:
                  AMPM=label[i].split('_')[-1].split('.')[0].split(' ')[1][:2]
               else:
                  AMPM="AM"
               
               if AMPM=='PM':
                  conv_time=(float(raw_time[:-4])+12)*60+float(raw_time[-4:-2])
               elif AMPM=='AM':
                  conv_time=(float(raw_time[:-4]))*60+float(raw_time[-4:-2])
               else:
                  print("Problème, AMPM="+AMPM)
                  break
               self.time_list.append((conv_time-self.time)%720)
               self.label.append(label[i])

               image=label[i].split(':')[1]
               image=image.split("_")[0]+"_"+image.split("_")[1]+"_"+image.split("_")[-1]
               with open(image[:-4]+".txt",'r') as ouvert:
                  lignes=ouvert.read().split('\n')
                  for l in range(len(lignes)):
                     if 'Move Channel' in lignes[l]:
                        #print(lignes[l])
                        if 'Far_Red' in lignes[l] and self.ch!=0:
                           #print(lignes[l+4])
                           self.exposure[lignes[l].split('- ')[-1]].append(float(lignes[l+4].split('- ')[-1]))

                        elif 'Far_Red' in lignes[l] and self.ch==2:
                           self.exposure[lignes[l].split('- ')[-1]].append(float(lignes[l+4].split('- ')[-1]))

                        elif "GFP" in lignes[l] and self.ch==0:
                           
                           self.exposure[lignes[l].split('- ')[-1]].append(float(lignes[l+4].split('- ')[-1]))

##            print(check_region)
            if check_region<len(self.regions):
               for cle in self.geometrie:
##                  print(cle)
##                  print(self.regions[check_region])
##                  print(dic_col[cle][i])
##                  print(self.dic_parametre[cle][self.regions[check_region]])
                  self.dic_parametre[cle][self.regions[check_region]].append(float(dic_col[cle][i]))
##                  print(self.dic_parametre[cle][self.regions[check_region]])
               for cle in self.couleur:
##                  print(cle)
                  if self.ch==1:
                     self.dic_parametre[cle][self.regions[check_region]+'_v'].append(float(dic_col[cle][i]))
                  if self.ch==2:
                     self.dic_parametre[cle][self.regions[check_region]+'_r'].append(float(dic_col[cle][i]))
                     self.dic_parametre[cle][self.regions[check_region]+'_v'].append(float(dic_col[cle][i+1]))
##                  print(self.dic_parametre[cle][self.regions[check_region]+'_v'])
                  if self.ch==0:
                     self.dic_parametre[cle][self.regions[check_region]+'_v'].append(float(dic_col[cle][i]))
               check_region+=1
            else:
##               print("cycle terminé")
##               print(check_region)
               check_region=0
               check=False
##               print(i)
##               print(i+len(self.regions)*self.ch-check_region*self.ch)
##               print(ending_slice)
               if i+len(self.regions)*max(self.ch,1)-check_region*max(self.ch,1)<=ending_slice+1 :
                  if dic_col['Ch'][i:i+len(self.regions)*max(self.ch,1)-check_region*max(self.ch,1)]==self.sequence[check_region*max(self.ch,1):]:
                     check=True
                  else:
                     check=False
               else:
                  check=False
##               print(check)
               if check:
                  raw_time=label[i].split('_')[-1].split('.')[0].split(' ')[0]
                  if len(label[i].split('_')[-1].split(' '))>1:
                     AMPM=label[i].split('_')[-1].split(' ')[1][:2]
                  else:
                     AMPM="AM"
                     
                  if AMPM=='PM':
                     conv_time=(float(raw_time[:-4])+12)*60+float(raw_time[-4:-2])
                  elif AMPM=='AM':
                     conv_time=(float(raw_time[:-4]))*60+float(raw_time[-4:-2])
                  else:
                     print("Problème, AMPM="+AMPM)
                     break
                  self.time_list.append((conv_time-self.time)%720)
                  self.label.append(label[i])
   ##               print(self.time_list)
                  image=label[i].split(':')[1]
                  image=image.split("_")[0]+"_"+image.split("_")[1]+"_"+image.split("_")[-1]
                  with open(image[:-4]+".txt",'r') as ouvert:
                     lignes=ouvert.read().split('\n')
                     for l in range(len(lignes)):
                        if 'Move Channel' in lignes[l]:
                           if 'Far_Red' in lignes[l] and self.ch!=0:
                              self.exposure[lignes[l].split('- ')[-1]].append(float(lignes[l+4].split('- ')[-1]))
                           elif 'Far_Red' in lignes[l] and self.ch==2:
                              self.exposure[lignes[l].split('- ')[-1]].append(float(lignes[l+4].split('- ')[-1]))
                           elif "GFP" in lignes[l] and self.ch==0:
                              self.exposure[lignes[l].split('- ')[-1]].append(float(lignes[l+4].split('- ')[-1]))


                  
                  for cle in self.geometrie:
##                     print(cle)
                     self.dic_parametre[cle][self.regions[check_region]].append(float(dic_col[cle][i]))
##                     print(self.dic_parametre[cle][self.regions[check_region]])
                  for cle in self.couleur:
##                     print(cle)
                     if self.ch==1:
                        self.dic_parametre[cle][self.regions[check_region]+'_v'].append(float(dic_col[cle][i]))
                     if self.ch==2:
                        self.dic_parametre[cle][self.regions[check_region]+'_r'].append(float(dic_col[cle][i]))
                        self.dic_parametre[cle][self.regions[check_region]+'_v'].append(float(dic_col[cle][i+1]))
##                     print(self.dic_parametre[cle][self.regions[check_region]+'_v'])
                     elif self.ch==0:
                        self.dic_parametre[cle][self.regions[check_region]+'_v'].append(float(dic_col[cle][i]))
               check_region+=1
      for cle in self.couleur:
         for region in self.regions:
##            print(np.array(self.dic_parametre[cle][region+'_v']))
##            print(np.array(self.exposure['GFP']))
##            print(type(self.dic_parametre[cle][region+'_v'][0]))
##            print(type(self.exposure['GFP'][0]))
            if self.ch==1:
               self.dic_parametre[cle][region+'_v']=np.array(self.dic_parametre[cle][region+'_v'])/np.array(self.exposure['Far_Red'])
            if self.ch==2:
##               print(self.dic_parametre[cle][region+'_r'])
##               print(np.array(self.exposure['Far_Red']))
               self.dic_parametre[cle][region+'_r']=np.array(self.dic_parametre[cle][region+'_r'])/np.array(self.exposure['Far_Red'])
            elif self.ch==0:
               self.dic_parametre[cle][region+'_v']=np.array(self.dic_parametre[cle][region+'_v'])/np.array(self.exposure['GFP'])
               
      
                                        
                                           
               
##         test=input('continue')
##         if test!="y":
##            break
         

            
      #self.Actin_ratio=np.array(self.dic_parametre['Mean']['pc_v'])/np.array(self.dic_parametre['Mean']['nc_v'])

def get_times(chemin,temps_initial,ch=2):
    #temps initial est l'heure de début d'étirement en chaîne de caractères hh:mm:ss
    #Chemin est le répertoire dans lequel sont les fichiers images et les tableaux de données
    # fonction qui va récupérer les temps.
    chdir(chemin)
    liste_dir=listdir()
    temps_dic={}
    zone_prec=''
    
    temps=[]
    for fichier in liste_dir: # On parcourt l'intégralité des fichiers dans le dossier actif
        fichier_split=fichier.split("_")# contient sous forme de liste les morceaux de noms de fichiers séparés par "_"
        
        if len(fichier_split)>2:
            # On néglige tous les fichiers qui ne sont pas segmentés comme on l'attend
            if ".tif" in fichier_split[2]:
                #print(fichier_split[2])
                # Les fichiers de métadonnées ont des noms presque identiques, pour ne pas compter tout deux fois on ne prend que les images
                time_split=fichier_split[2].split("-")# La dernière partie du nom contient l'information de l'heure
                
                
                
                if fichier_split[1]!=zone_prec :                  
                    temps_dic[zone_prec]=temps
                    #print(zone_prec+'\t')
                    #print(temps_dic[zone_prec])
                    #print('\n')
                    zone_prec=fichier_split[1]
                    temps=[]
                time=int(time_split[0])*60+int(time_split[1])
                temps.append(time-(int(temps_initial[0:2])*60+int(temps_initial[3:5])))
    temps_dic[zone_prec]=temps
    dic_cell={}
    for fichier in liste_dir:
        if '.xls' in fichier:
           #print(fichier)
           dic_cell[fichier[:6]]=Cellule2(temps_dic['zone'+str(int(fichier[1:3]))],fichier[1:3],ch,fichier[4:6])
    return dic_cell

class Cellule2(object) : #Création de la classe cellule qui va contenir toutes les info sur les cellules à observer.
    
   def __init__(self,temps,zone,ch=2,cell='01'):


       self.temps=temps
       self.zone=zone
       self.cell=cell
       self.ch=2
       self.dic_parametre={}
       for cle in ['Area','Minor','Major','Angle','Mean','Median','RawIntDen']:
          self.dic_parametre[cle]={}
       
       self.geometrie=['Area','Minor','Major','Angle']
       self.couleur=['Mean','Median','RawIntDen']

       for cle in self.geometrie:
           for region in ['tc','nc','pc']:
               self.dic_parametre[cle][region]=np.zeros(len(self.temps))
       if ch==2:
           
           for cle in self.couleur:
               for region in ['tc_r','nc_r','tc_v','nc_v','pc_r','pc_v']:
                   self.dic_parametre[cle][region]=np.zeros(len(self.temps))
       elif ch==1:
           for cle in self.couleur:
               for region in ['tc_v','nc_v','pc_v']:
                   self.dic_parametre[cle][region]=np.zeros(len(self.temps))
       file='z'+str(zone)+'c'+str(cell)+'.xls'

       workbook=xlrd.open_workbook(file)
       for sheetname in workbook.sheet_names():
          sh=workbook.sheet_by_name(sheetname)
       dic_col={}

       for col_name in sh.row_values(rowx=0):
          dic_col[col_name]=sh.col_values(sh.row_values(rowx=0).index(col_name),start_rowx=1)
##          
##
##       dic_col['aire']=sh.col_values(1,start_rowx=1)
##       dic_col['moyenne']=sh.col_values(2,start_rowx=1)
##       dic_col['majeur']=sh.col_values(5,start_rowx=1)
##       dic_col['mineur']=sh.col_values(6,start_rowx=1)
##       dic_col['angle']=sh.col_values(7,start_rowx=1)
##       dic_col['intden']=sh.col_values(8,start_rowx=1)
##       dic_col['mediane']=sh.col_values(9,start_rowx=1)
       channel=dic_col['Ch']
       frames=dic_col['Slice']
       #print('zone '+str(zone)+' cell '+cell+'\n')
       

       for i in range(0,len(frames)-3,3):
         #print(i)
         if frames[i:i+3]!=[frames[i]]*3:
            #print(slices[i:i+6])
            print("Problème au frame "+str(int(frames[i]))+' ligne '+str(i))
         #if channel[i:i+2]!=[1.0,2.0]*6:
            #print("problème de channel ligne "+str(i))
                
       
       check_region=0
       if ch==2:
           
           for i in range(len(frames)-1):
##               print('i=')
##               print(i)
              if channel[i:i+2]==[1.0,2.0]:
                  if check_region==0:
                      region_geo='tc'
                      region_cou=['tc_r','tc_v']
                  
                  elif check_region==1:
                      region_geo='nc'
                      region_cou=['nc_r','nc_v']
                  elif check_region==2:
                      region_geo='pc'
                      region_cou=['pc_r','pc_v']
              #print(region_cou)        
                  for cle in self.geometrie:
                 #print('slices[i]-1')
                 #print(slices[i]-1)
                 #print(cle)
             
                 #print(dic_col[cle][i])
                     self.dic_parametre[cle][region_geo][frames[i]-1]=dic_col[cle][i]
                  for cle in self.couleur:
                     for couleur in region_cou:
                    #print('slices[i]-1')
                    #print(slices[i]-1)
                    #print(cle)
                
                    #print(dic_col[cle][i+region_cou.index(couleur)])
                        self.dic_parametre[cle][couleur][frames[i]-1]=dic_col[cle][i+region_cou.index(couleur)]

              elif channel[i:i+2]==[2.0,1.0]:
                  if frames[i]==frames[i+1]:
                      check_region+=1
                      if check_region>2:
                          check_region=0
                  else :
                      check_region=0
       elif ch==1:
          for i in range(len(frames)):
             
             if check_region==0:
                region_geo='tc'
                
             elif check_region==1:
                region_geo='nc'
                     
             elif check_region==2:
                region_geo='pc'
                     
                  
             for cle in self.geometrie:
                self.dic_parametre[cle][region_geo][frames[i]-1]=dic_col[cle][i]
             for cle in self.couleur:
                self.dic_parametre[cle][region_geo+'_v'][frames[i]-1]=dic_col[cle][i]
                   
             
                 
             check_region+=1
             if check_region>2:
                check_region=0
         
          for cle in self.geometrie:
              for region in ['tc','nc','pc']:
                  self.dic_parametre[cle][region]=np.array(self.dic_parametre[cle][region])
          for cle in self.couleur:
               for region in ['tc','nc','pc']:
                   self.dic_parametre[cle][region+'_v']=np.array(self.dic_parametre[cle][region+'_v'])
          
       self.MRTFA_ratio=np.array(self.dic_parametre['Mean']['pc_v'])/np.array(self.dic_parametre['Mean']['nc_v'])
       self.time_list=self.temps
  


         
def Moyenne_MRTFA_ratio_tri(dic_cell):
   final=[]
   for t in range(1,140):
      stock=[]
      for key in dic_cell.keys():
         cell=dic_cell[key]
         stock2=[]
         stock2_SiR=[]
         if cell.dic_parametre['Area']['tc'][-1]>cell.dic_parametre['Area']['tc'][0]/2:
            for time in cell.time_list:
               if time<(t+6) and time>(t-6):
                  stock2.append(cell.MRTFA_ratio[cell.time_list.index(time)])
                  stock2_SiR.append(cell.Sir_norm[cell.time_list.index(time)])
            if len(stock2):
               stock.append(stock2[stock2_SiR.index(max(stock2_SiR))])
         
      final.append(np.nanmean(stock))
   return final

def Moyenne_MRTFA_ratio_tri3(dic_cell):
   final=[]
   for t in range(1,140):
      stock=[]
      for key in dic_cell.keys():
         cell=dic_cell[key]
         stock2=[]
         stock2_SiR=[]
         if cell.dic_parametre['Area']['tc'][-1]>cell.dic_parametre['Area']['tc'][0]/2 and min(cell.time_list)<6:
            for time in cell.time_list:
               if time<(t+5) and time>(t-5):
                  stock2.append(cell.MRTFA_ratio[cell.time_list.index(time)])
                  stock2_SiR.append(cell.Sir_norm[cell.time_list.index(time)])
            if len(stock2):
               stock.append(stock2[stock2_SiR.index(max(stock2_SiR))])
         
      final.append(np.nanmean(stock))
   return final

def Moyenne_MRTFA_ratio(dic_cell):
   final=[]
   for t in range(1,140):
      stock=[]
      for key in dic_cell.keys():
         cell=dic_cell[key]
         if True:
            for time in cell.time_list:
               if time<(t+5) and time>(t-5):
                  stock.append(cell.MRTFA_ratio[cell.time_list.index(time)])
      final.append(np.nanmean(stock))
   return final
   
def Moyenne_MRTFA_ratio_tri2(dic_cell):
   final=[]
   for t in range(1,140):
      stock=[]
      for key in dic_cell.keys():
         cell=dic_cell[key]
         if cell.dic_parametre['Area']['tc'][-1]>700 or cell.dic_parametre['Major']['tc'][-1]/cell.dic_parametre['Minor']['tc'][-1]>2:
            for time in cell.time_list:
               if time<(t+5) and time>(t-5):
                  stock.append(cell.MRTFA_ratio[cell.time_list.index(time)])
      final.append(np.nanmean(stock))
   return final

def Mediane_MRTFA_ratio_tri(dic_cell):
   final=[]
   for t in range(1,140):
      stock=[]
      for key in dic_cell.keys():
         cell=dic_cell[key]
         if cell.dic_parametre['Area']['tc'][-1]>cell.dic_parametre['Area']['tc'][0]/2 :
            for time in cell.time_list:
               if time<(t+7) and time>(t-7):
                  stock.append(cell.MRTFA_ratio[cell.time_list.index(time)])
      final.append(np.median(stock))
   return final

def Ncell(dic_cell):
   final=[]
   MRTFA_ratio(dic_cell)
   for t in range(1,140):
      stock=[]
      for key in dic_cell.keys():
         cell=dic_cell[key]
         stock2=[]
         if cell.dic_parametre['Area']['tc'][-1]>cell.dic_parametre['Area']['tc'][0]/2:
            
            for time in cell.time_list:
               if time<(t+5) and time>(t-5):
                  stock2.append(cell.MRTFA_ratio[cell.time_list.index(time)])
            if len(stock2)>0:
               stock.append(max(stock2))
      final.append(len(stock))
   return final

def Moyenne(dic_cell,parametre,region):
   final=[]
   for t in range(1,140):
      stock=[]
      for key in dic_cell.keys():
         cell=dic_cell[key]
         for time in cell.time_list:
            if time<=(t+5) and time>=(t-5):
               stock.append(cell.dic_parametre[parametre][region][cell.time_list.index(time)])
      final.append(np.nanmean(stock))
   return final

def Moyenne_tri(dic_cell,parametre,region):
   final=[]
   for t in range(1,140):
      stock=[]
      for key in dic_cell.keys():
         cell=dic_cell[key]
         if cell.dic_parametre['Area']['tc'][-1]>cell.dic_parametre['Area']['tc'][0]/2:
            for time in cell.time_list:
               if time<=(t+6) and time>=(t-6):
                  stock.append(cell.dic_parametre[parametre][region][cell.time_list.index(time)])
      final.append(np.nanmean(stock))
   return final

def Mediane(dic_cell,parametre,region):
   final=[]
   for t in range(1,140):
      stock=[]
      for key in dic_cell.keys():
         cell=dic_cell[key]
         for time in cell.time_list:
            if time<(t+2) and time>(t-2):
               stock.append(cell.dic_parametre[parametre][region][cell.time_list.index(time)])
      final.append(np.median(stock))
   return final

def Moyenne_Sirnorm(dic_cell):
   final=[]
   for t in range(1,140):
      stock=[]
      for key in dic_cell.keys():
         cell=dic_cell[key]
         if cell.time_list[0]<40:
            for time in cell.time_list:
               if time<(t+7) and time>(t-7):
                  stock.append(cell.Sir_norm[cell.time_list.index(time)])
      final.append(np.nanmean(stock))
   return final

def Mediane_Sirnorm(dic_cell):
   final=[]
   for t in range(1,140):
      stock=[]
      for key in dic_cell.keys():
         cell=dic_cell[key]
         if cell.time_list[0]<40:
            for time in cell.time_list:
               if time<(t+7) and time>(t-7):
                  stock.append(cell.Sir_norm[cell.time_list.index(time)])
      final.append(np.median(stock))
   return final

def Moyenne_Sirnorm_tri(dic_cell):
   final=[]
   for t in range(1,140):
      stock=[]
      for key in dic_cell.keys():
         cell=dic_cell[key]
         stock2=[]
         if cell.dic_parametre['Area']['tc'][-1]>cell.dic_parametre['Area']['tc'][0]/2:
            for time in cell.time_list:
               if time<(t+6) and time>(t-6):
                  stock2.append(cell.Sir_norm[cell.time_list.index(time)])
            if len(stock2):
               stock.append(max(stock2))
      final.append(np.nanmean(stock))
   return final

def Moyenne_Aire_norm_tri(dic_cell):
   final=[]
   for t in range(1,140):
      stock=[]
      for key in dic_cell.keys():
         cell=dic_cell[key]
         stock2=[]
         stock2_SiR=[]
         if cell.dic_parametre['Area']['tc'][-1]>cell.dic_parametre['Area']['tc'][0]/2:
            for time in cell.time_list:
               if time<(t+6) and time>(t-6):
                  stock2.append(cell.Aire_norm[cell.time_list.index(time)])
                  stock2_SiR.append(cell.Sir_norm[cell.time_list.index(time)])
            if len(stock2):
               stock.append(stock2[stock2_SiR.index(max(stock2_SiR))])
         
      final.append(np.nanmean(stock))
   return final

def Moyenne_Sirnorm_tri3(dic_cell):
   final=[]
   for t in range(1,140):
      stock=[]
      for key in dic_cell.keys():
         cell=dic_cell[key]
         stock2=[]
         if cell.dic_parametre['Area']['tc'][-1]>cell.dic_parametre['Area']['tc'][0]/2 and min(cell.time_list)<6:
            for time in cell.time_list:
               if time<(t+5) and time>(t-5):
                  stock2.append(cell.Sir_norm[cell.time_list.index(time)])
            if len(stock2):
               stock.append(max(stock2))
      final.append(np.nanmean(stock))
   return final

def Moyenne_Sirnorm_tri2(dic_cell):
   final=[]
   for t in range(1,140):
      stock=[]
      for key in dic_cell.keys():
         cell=dic_cell[key]
         if cell.dic_parametre['Area']['tc'][-1]>700 or cell.dic_parametre['Major']['tc'][-1]/cell.dic_parametre['Minor']['tc'][-1]>2:
            for time in cell.time_list:
               if time<(t+7) and time>(t-7):
                  stock.append(cell.Sir_norm[cell.time_list.index(time)])
      final.append(np.nanmean(stock))
   return final


def Moyenne_Sirnorm_RawIntDen(dic_cell):
   final=[]
   for t in range(1,140):
      stock=[]
      for key in dic_cell.keys():
         cell=dic_cell[key]
         if True:
            for time in cell.time_list:
               if time<(t+5) and time>(t-5):
                  stock.append(cell.Sir_norm_RawIntDen[cell.time_list.index(time)])
      final.append(np.nanmean(stock))
   return final
def Sirnorm_ch1(dic_cell):
   for key in dic_cell.keys():
      cell=dic_cell[key]
      index=cell.time_list.index(min(cell.time_list))
      cell.Sir_norm=np.array(cell.dic_parametre['Mean']['tc_v'])/cell.dic_parametre['Mean']['tc_v'][index]
      
def MRTFA_norm_ch0(dic_cell):
   for key in dic_cell.keys():
      cell=dic_cell[key]
      index=cell.time_list.index(min(cell.time_list))
      cell.MRTFA_norm=np.array(cell.MRTFA_ratio/cell.MRTFA_ratio[index])

def Sirnorm_ch2(dic_cell):
   for key in dic_cell.keys():
      cell=dic_cell[key]
      index=cell.time_list.index(min(cell.time_list))
      cell.Sir_norm=np.array(cell.dic_parametre['Mean']['tc_r'])/cell.dic_parametre['Mean']['tc_r'][index]

def Sirnorm_ch2_v2(dic_cell):
   for key in dic_cell.keys():
      cell=dic_cell[key]
      SiR_init=[]
      for t in cell.time_list:
         if t<7:
            SiR_init.append((cell.dic_parametre['Mean']['tc_r'][cell.time_list.index(t)]))
      if len(SiR_init):
         SiR0=max(SiR_init)
      else:
         index=cell.time_list.index(min(cell.time_list))
         SiR0=cell.dic_parametre['Mean']['tc_r'][index]
      
      cell.Sir_norm=np.array(cell.dic_parametre['Mean']['tc_r'])/SiR0
      
def Airenorm_ch2(dic_cell):
   for key in dic_cell.keys():
      cell=dic_cell[key]
      SiR_init=[]
      for t in cell.time_list:
         if t<7:
            SiR_init.append((cell.dic_parametre['Aire']['tc'][cell.time_list.index(t)]))
      if len(SiR_init):
         SiR0=np.mean(SiR_init)
      else:
         index=cell.time_list.index(min(cell.time_list))
         SiR0=cell.dic_parametre['Aire']['tc'][index]
      
      cell.Aire_norm=np.array(cell.dic_parametre['Aire']['tc'])/SiR0      

def Sirnorm_ch2_bg(dic_cell):
   for key in dic_cell.keys():
      cell=dic_cell[key]
      index=cell.time_list.index(min(cell.time_list))
      cell.Sir_norm_bg=np.array(cell.Sir_bg)/cell.Sir_bg[index]


def Sirnorm_RawIntDen_ch1(dic_cell):
   for key in dic_cell.keys():
      cell=dic_cell[key]
      if len(cell.time_list):
          index=cell.time_list.index(min(cell.time_list))
          cell.Sir_norm_RawIntDen=cell.dic_parametre['RawIntDen']['tc_v']/cell.dic_parametre['RawIntDen']['tc_v'][index]
      
def Sirnorm_RawIntDen_ch2(dic_cell):
   for key in dic_cell.keys():
      cell=dic_cell[key]
      index=cell.time_list.index(min(cell.time_list))
      cell.Sir_norm_RawIntDen=cell.dic_parametre['RawIntDen']['tc_r']/cell.dic_parametre['RawIntDen']['tc_r'][index]
      
def MRTFA_ratio(dic_cell):
   for key in dic_cell.keys():
      cell=dic_cell[key]
      cell.MRTFA_ratio=np.array(cell.dic_parametre['RawIntDen']['nc_v'])/np.array(cell.dic_parametre['RawIntDen']['tc_v'])
      
def Classification(path):
   chdir(path)
   dic_entrantes={}
   dic_sortantes={}
   dic_autres={}
   liste_files=["Entrantes","Sortantes","Autres"]
   liste_dic=[dic_entrantes,dic_sortantes,dic_autres]
   for dic in liste_dic:
      with open(path+"//"+liste_files[liste_dic.index(dic)]+".txt",'r') as file:
         lines=file.read().split('\n')
         for line in lines:
            if "Et10_1" in line:
               dic[line]=Et10_1[line.split("_")[-1]]
            elif 'Et10_2' in line:
               dic[line]=Et10_2[line.split("_")[-1]]
            elif "Et10_3" in line:
               dic[line]=Et10_3.dic_cell[line.split("_")[-1]]
   return dic_entrantes,dic_sortantes,dic_autres
         
def erreur_Sirnorm(dic_cell):
   final=[]
   for t in range(1,140):
      stock=[]
      for key in dic_cell.keys():
         cell=dic_cell[key]
         if cell.dic_parametre['Area']['tc'][-1]>cell.dic_parametre['Area']['tc'][0]/2:
            for time in cell.time_list:
               if time<(t+6) and time>(t-6):
                  stock.append(cell.Sir_norm[cell.time_list.index(time)])
      final.append(np.std(stock)/(len(stock)**0.5))
   return final
         
def erreur_Sirnorm_Raw(dic_cell):
   final=[]
   for t in range(1,140):
      stock=[]
      for key in dic_cell.keys():
         cell=dic_cell[key]
         if True:
            for time in cell.time_list:
               if time<(t+6) and time>(t-6):
                  stock.append(cell.Sir_norm_RawIntDen[cell.time_list.index(time)])
      print(stock)
      final.append(np.std(stock)/(len(stock)**0.5))
   return final
      
def erreur_MRTFA(dic_cell):
   final=[]
   for t in range(1,140):
      stock=[]
      for key in dic_cell.keys():
         cell=dic_cell[key]
         if True:
            for time in cell.time_list:
               if time<(t+5) and time>(t-5):
                  stock.append(cell.MRTFA_ratio[cell.time_list.index(time)])
      final.append(np.std(stock)/(len(stock)**0.5))
   return final
      

         
temoin10=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2015-12-15//C2C12 SiRactine et0//","13:25",2)
Et10_3=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2015-12-15//c2c12 SiRactine et10//","15:55",2)
MRTFA_ratio(Et10_3.dic_cell)
temoin30_2=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2016-01-28//Et0//","13:06",2)
del temoin30_2.dic_cell["z04c1"]
Et30_2=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2016-01-28//Et30//","15:12",2)
temoin30_1=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2016-01-21//et0//","13:55",1)
Et30_1=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2016-01-21//et30//","16:25",1)
#Et10_1=get_times("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//experiences dépouillées//2015-04-14//lamelle1//","14:23",2)
#Et10_2=get_times("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//experiences dépouillées//2015-04-14//lamelle2//","16:55",2)
temoin_rapide=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2016-02-04//et0 live Siractine//","11:24",1)
Et10_1_rapide=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2016-02-04//et10 live SiRactine//","13:31",1)
Et10_2_rapide=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2016-02-04//et10 live SiRactine 2//","14:30",1)
Et10_1bis_rapide=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2016-02-04//et10 live SiRactine - Copie//","13:31",1)
Et30_rapide=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2016-02-04//et30 live SiRactine//","12:06",1)
Et10_3_rapide=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2015-12-15//c2c12 SiRactine rapide//","15:10",1)

Et30_2_rapide=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2016-02-04//et30 live SiRactine 2//","12:49",1)

Et10_4=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2015-12-10//C2C12 SiRactine et10//","12:04",2)
del Et10_4.dic_cell["z06c1"]
for key in Et10_4.dic_cell.keys():
   cell=Et10_4.dic_cell[key]
   for time in cell.time_list:
      if time>719:
         cell.time_list[cell.time_list.index(time)]=time-720
temoin10_4=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2015-12-10//C2C12 SiRactine et0//","10:44",0)

#dic_Et10SiR={}
#for i in range(3):
#    exp=[Et10_1,Et10_2,Et10_4.dic_cell][i]
#    for key in exp.keys():
#        dic_Et10SiR[str(i)+"_"+key]=exp[key]

dic_Et0SiR={}
for i in range(3):
    exp=[temoin10,temoin10_4,temoin30_1,temoin30_2][i]
    for key in exp.dic_cell.keys():
        dic_Et0SiR[str(i)+"_"+key]=exp.dic_cell[key]

dic_Et10nano={}
Et10_nano1=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2013-09-13//apres//","15:01",0)
Et10_nano2=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2013-09-12//lamelle1//apres//","15:01",0)
Et10_nano3=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2013-09-17//apres//","16:00",0)
Et10_nano4=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2013-09-18//apres//","15:55",0)
for exp in [Et10_nano1,Et10_nano2,Et10_nano3,Et10_nano4]:
    i=[Et10_nano1,Et10_nano2,Et10_nano3,Et10_nano4].index(exp)
    for key in exp.dic_cell.keys():
        dic_Et10nano[str(i)+"_"+key]=exp.dic_cell[key]
        
Et0_nano2=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2013-07-12//lamelle1 non rincee//avant etirement//","10:28",0)
Et0_nano1=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement////2013-07-10//lamelle1 premontee non rincee//","10:39",0)
Et0_nano3=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2013-09-12//lamelle1//avant//","13:00",0)
Et0_nano4=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2013-09-17//avant//","13:55",0)
Et0_nano5=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2013-09-18//avant//","13:49",0)
dic_Et0nano={}
for exp in [Et0_nano1,Et0_nano2,Et0_nano3,Et0_nano4,Et0_nano5]:
    i=[Et0_nano1,Et0_nano2,Et0_nano3,Et0_nano4,Et0_nano5].index(exp)
    for key in exp.dic_cell.keys():
        dic_Et0nano[str(i)+"_"+key]=exp.dic_cell[key]
        
Et30_nano1=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2013-07-09//lamelle2 premontee non rincee//etirement 30//","12:43",0)
Et30_nano2=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2013-07-10//lamelle1 premontee non rincee//etirement 30//","12:45",0)
Et30_nano3=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2013-07-12//lamelle1 non rincee//apres etirement 30//","12:40",0)

dic_Et30nano={}
for i in range(3):
    exp=[Et30_nano1,Et30_nano2,Et30_nano3][i]
    for key in exp.dic_cell.keys():
        dic_Et30nano[str(i)+"_"+key]=exp.dic_cell[key]
#for key in Et30_nano3.dic_cell.keys():
#    cell=Et30_nano3.dic_cell[key]
#    
#    for label in cell.label:
#        for i in range(len(BG3["Label"])):
#            if label==BG3["Label"][i][3:]:
#                
#                cell.MRTFA_ratio_BG=(np.array(cell.dic_parametre['RawIntDen']['nc_v'])-np.array(cell.dic_parametre["Area"]["nc"])*float(BG3["Mean"][i]))/(np.array(cell.dic_parametre['RawIntDen']['tc_v'])-np.array(cell.dic_parametre["Area"]["tc"])*float(BG3["Mean"][i]))
MRTFA_ratio(dic_Et0nano)
MRTFA_ratio(dic_Et10nano)
MRTFA_ratio(dic_Et30nano)
#dic_e,dic_s,dic_a=Classification('C://Users//Lorraine')
#dic_tot={}
#for dic in dic_e,dic_s,dic_a:
#   for key in dic.keys():
#      dic_tot[key]=dic[key]
lipo1_et30=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2016-03-08//et30 lipo3000 1//","13:53",0)
lipo2_et30=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2016-03-08//et30 lipo3000 2//","16:35",0)
lipo1_et0=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2016-04-08//et0 sans SiR//","11:06",0)
lipo1_et10=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2016-04-08//et10 sans SiR2//","15:07",0)
lipo3_et0=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2016-04-12//et0//","10:56",0)
lipo3_et10=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2016-04-12//et10//","12:55",0)
lipo4_et0=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2016-04-19//Et0-2//","15:41",0)
del lipo4_et0.dic_cell["z09c2"]
lipo4_et10=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2016-04-19//Et10-2//","17:06",0)
Et30_SiR1=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2016-03-08//et30 SiRactine 1//","14:50",2)
Et30_SiR2=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2016-03-08//et30 SiRactine 2//","15:43",2)
Et0_SiR=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2016-03-08//et0 SiRactine//","17:13",2)
Et30_SiR3=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2016-03-15//Et30 SiRactine//","15:10",2)
Et30_SiR4=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2016-03-15//Et30 SiRactine 2//","16:56",2)
Et0_SiR2=Experiment("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement//2016-03-15//Et0 SiRactine 1//","14:10",2)

dic_temoin={}
dic_Et30={}
for exp in [Et30_SiR1,Et30_SiR2,Et30_SiR3]:
   i=[Et30_SiR1,Et30_SiR2,Et30_SiR3].index(exp)
   Sirnorm_ch2(exp.dic_cell)
   MRTFA_ratio(exp.dic_cell)
   for key in exp.dic_cell.keys():
      dic_Et30[str(i)+"_"+key]=exp.dic_cell[key]

for exp in [Et0_SiR,Et0_SiR2]:
   i=[Et0_SiR,Et0_SiR2].index(exp)
   Sirnorm_ch2(exp.dic_cell)
   MRTFA_ratio(exp.dic_cell)
   for key in exp.dic_cell.keys():
      dic_temoin[str(i)+"_"+key]=exp.dic_cell[key]





import sqlite3


DB="//Volumes//DDLorraine//These//DocumentsLorraine//Etirement.sq3"
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
            for index_etat in range(8):
                etat=self.etats[index_etat]
                if etat is not None:
                    self.select_string+=" AND Cellules.etat"+str(index_etat)+"="+str(etat)

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
        self.data_total=np.zeros(141)
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

DBK="//Volumes//DDLorraine//These//DocumentsLorraine//Etirement - Copie - Kaori2.sq3"
connK=sqlite3.connect(DBK)
curK=connK.cursor()

class SelectionK(object):
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
            for index_etat in range(8):
                etat=self.etats[index_etat]
                if etat is not None:
                    self.select_string+=" AND Cellules.etat"+str(index_etat)+"="+str(etat)

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



        result=curK.execute("SELECT "+self.colonnes+self.select_string)
        #print("SELECT "+self.colonnes+self.select_string)
        
        for r in result:
            print(r)
            for minute in range(140,-1,-1):
                
                if minute<=((720+int(r[15]))%720) and minute>=((720+int(r[1]))%720):
                    n=0
                    
                    while n<14 and minute<((720+int(r[15-n]))%720):
                        n=n+2
                        #print(n)
                        while(r[15-n]==None):
                            n=n+2
                    
                    if n<14 and n>0:
                        self.dic[minute][r[12-n]+r[14-n]]=self.dic[minute].get(r[12-n]+r[14-n],0)+1
                        if r[14-n]!=r[12-n] and ((720+int(r[15-n]))%720)==minute:
                            #print(n)
                            self.dic_trans[minute][r[12-n]+r[14-n]]=self.dic_trans[minute].get(r[12-n]+r[14-n],0)+1
                            
                    else :
                        self.dic[minute][r[14-n]]=self.dic[minute].get(r[14-n],0)+1   
        self.data_total=np.zeros(141)
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


conn2=sqlite3.connect("//Volumes//DDLorraine//These//DocumentsLorraine//Etirement_Copie_Tiana.sq3")
cur2=conn2.cursor()
            
class Selection2(object):
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



        result=cur2.execute("SELECT "+self.colonnes+self.select_string)
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
        self.data_total=np.zeros(141)
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
Toutes=Selection(rincee=0,premontee=1,densite_max=25,AMC=0,date_max="2014-01-01")
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
        liste_ind=[C,H,N]
        for exp in experiment_list:
            if experiment_list.index(exp)==0:
                color="grey"
            else:
                color=liste_couleurs[etats_simple.index(etat)]
                pl.plot(np.arange(121),np.array(liste_ind[etats_simple.index(etat)])/np.array(total),label="Independant Observer",color="k")
            pl.errorbar(np.arange(141),
				exp.data[etat]/(exp.data["C"]+exp.data["H"]+exp.data["N"]),
                                erreurs(Liste_date(exp))[etat],    
				label=labels[experiment_list.index(exp)],
                                color=color,
                                linewidth=2,
                                marker=markers[experiment_list.index(exp)]
				)
            
            limites=[(0.25,0.85
  ),(0,0.6),(0,0.6)]
            localisation=['lower right','upper right','upper right']
            pl.xlim(5,105)
            pl.ylim(limites[etats_simple.index(etat)])
            pl.legend(loc=localisation[etats_simple.index(etat)])

def plot_simple_err_et10SiR(experiment_list,labels=[]):
	for etat in etats_simple:
		pl.subplot(3,1,etats_simple.index(etat)+1)
		pl.title(etat)
		for exp in experiment_list:
			pl.errorbar(np.arange(141),
				exp.data[etat]/(exp.data["C"]+exp.data["H"]+exp.data["N"]),
                                erreurs_et10SiR(Liste_date(exp),Liste_date2(Et10_SiR2))[etat],    
				label=labels[experiment_list.index(exp)],
                                color=liste_couleurs[etats_simple.index(etat)],
                                alpha=1/len(experiment_list)*(experiment_list.index(exp)+1),
                                marker=markers[experiment_list.index(exp)]
				)
		limites=[(0.25,0.85
  ),(0,0.6),(0,0.6)]
		localisation=['lower left','upper left','upper left']
		pl.xlim(3,100)
		pl.xticks([3,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100],["3","10","15","20","25","30","35","40","45","50","55","60","65","70","75","80","85","90","95","100"])  
		pl.ylim(limites[etats_simple.index(etat)])
		pl.legend(loc=localisation[etats_simple.index(etat)])
		
def plot_simple(experiment_list,labels=[]):
	for etat in etats_simple:
		pl.subplot(3,1,etats_simple.index(etat)+1)
		pl.title(etat)
		for exp in experiment_list:
			pl.plot(np.arange(141),
				exp.data[etat]/(exp.data["C"]+exp.data["H"]+exp.data["N"]),    
				label=labels[experiment_list.index(exp)],
                                color=liste_couleurs[etats_simple.index(etat)],
                                alpha=1/len(experiment_list)*(experiment_list.index(exp)+1),
                                marker=markers[experiment_list.index(exp)]
				)
		limites=[(0.25,0.85),(0,0.6),(0,0.6)]
		
		localisation=['upper right','upper right','upper right']
		pl.xlim(0,105)
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

def plot_transloc_cumul_all(experiment_list,labels):
   liste_trans=["ch","hn","cn","hc","nh","nc"]
   

   for exp in experiment_list:
      cumul=np.zeros(len(exp.data_total))
      for etat in liste_trans:
         cumul=cumul+exp.data_trans[etat]
      pl.plot(np.cumsum(cumul)/max(exp.data_total),label=labels[experiment_list.index(exp)])
   pl.legend(loc="upper left")

def plot_transloc_cumul(experiment_list,labels,direction):
   if direction=="e":
      liste_trans=["ch","hn","cn"]
      liste_start=['C','H']
   elif direction=="s":
      liste_trans=["hc","nh","nc"]
      liste_start=['H','N']
   else:
      liste_trans=[]

   for exp in experiment_list:
      cumul=np.zeros(len(exp.data_total))
      for etat in liste_trans:
         cumul=cumul+exp.data_trans[etat]
      pl.plot(np.cumsum(cumul)/max(exp.data[liste_start[0]]+exp.data[liste_start[1]]),label=labels[experiment_list.index(exp)])
   pl.legend(loc="upper left")


def plot_transloc_cumul2(experiment_list,labels,direction):
   if direction=="e":
      liste_trans=["ch","hn","cn"]
      liste_start=['C','H']
   elif direction=="s":
      liste_trans=["hc","nh","nc"]
      liste_start=['H','N']
   else:
      liste_trans=[]

   for exp in experiment_list:
      cumul=np.zeros(len(exp.data_total))
      for etat in liste_trans:
         cumul=cumul+exp.data_trans[etat]
      pl.plot(np.cumsum(cumul)/max(exp.data_total),label=labels[experiment_list.index(exp)])
   pl.legend(loc="upper left")   
   
      

def Liste_date(selection):
    result=cur.execute("SELECT DISTINCT Experiments.date  "+selection.select_string)
    liste_date=[]
    for r in result:
        liste_date.append(r[0])
    return liste_date
def Liste_date2(selection):
    result=cur2.execute("SELECT DISTINCT Experiments.date  "+selection.select_string)
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

def erreurs_et10SiR(liste_date,liste_date2):
	liste_exp=[]
	erreurs={}
	for date in liste_date:
		exp=Selection(liste_date=[date])
		liste_exp.append(exp)
	for date in liste_date2:
		exp=Selection2(liste_date=[date])
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
def p_values(liste_exp):
   pvalues=[]
   obs=[]
   for exp in liste_exp:
      obs.append([exp.data['c']+exp.data['h']+exp.data['n'],
              exp.data['ch']+exp.data['hn']+exp.data['cn'],
              exp.data['hc']+exp.data['nh']+exp.data['nc']])
   for i in range(len(exp.data_total)):
      print(i)
##      print(obs[0][0][i])
##      print(obs[1][0][i])
      if 0 in [obs[0][0][i],obs[0][1][i],obs[0][2][i]] or 0 in [obs[1][0][i],obs[1][1][i],obs[1][2][i]]:
         pvalues.append(np.nan)
      else:
   
         pvalues.append(chi2_contingency([[obs[0][0][i],obs[0][1][i],obs[0][2][i]],[obs[1][0][i],obs[1][1][i],obs[1][2][i]]],lambda_="log-likelihood")[1])
   return pvalues
      
def p_values_CHN(liste_exp):
   pvalues=[]
   obs=[]
   for exp in liste_exp:
      obs.append([exp.data['C'],
              exp.data['H'],
              exp.data['N']])
   for i in range(len(exp.data_total)):
      print(i)
##      print(obs[0][0][i])
##      print(obs[1][0][i])
      if 0 in [obs[0][0][i],obs[0][1][i],obs[0][2][i]] or 0 in [obs[1][0][i],obs[1][1][i],obs[1][2][i]]:
         pvalues.append(np.nan)
      else:
   
         pvalues.append(chi2_contingency([[obs[0][0][i],obs[0][1][i],obs[0][2][i]],[obs[1][0][i],obs[1][1][i],obs[1][2][i]]],lambda_="log-likelihood")[1])
   return pvalues         
         
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


def Substract_Background(exp,file):
   workbook=xlrd.open_workbook(file)
   for sheetname in workbook.sheet_names():
      sh=workbook.sheet_by_name(sheetname)
   dic_col={}
   for col_name in sh.row_values(rowx=0):
      dic_col[col_name]=sh.col_values(sh.row_values(rowx=0).index(col_name),start_rowx=1)

   for key in exp.dic_cell.keys():
      cell=exp.dic_cell[key]
      cell.Sir_bg=np.zeros(len(cell.dic_parametre['Mean']["tc_r"]))
      for label in dic_col["Label"]:
         if label in cell.label:
            cell.Sir_bg[cell.label.index(label)]=cell.dic_parametre['Mean']["tc_r"][cell.label.index(label)]/dic_col['Mean'][dic_col["Label"].index(label)]
   
Et30_rapide=Selection(liste_date=["2016-03-08 14:51","2016-03-08 15:43","2016-03-15 15:10"])
Et30_lent=Selection(liste_date=["2016-01-21 16:23","2016-01-28 15:10"])
Et30_rapide_sansSir=Selection(liste_date=["2016-03-08 13:52","2016-03-08 16:35","2016-03-15 16:02"])
Et0_lent=Selection(liste_date=["2016-01-28 13:05","2016-01-21 13:56","2015-12-15 12:53","2015-12-10 10:45"])
Et0_rapide=Selection(liste_date=["2016-03-08 17:13","2016-03-15 14:10"])
Et0_lent_sansSiR=Selection(liste_date=["2015-11-10 15:11"])

Et10_SiR=Selection(liste_date=["2015-12-10 12:04"])
Et10_SiR2=Selection2(liste_date=["2015-04-14 14:15","2015-04-14 16:55"])
for etat in etats_simple:
   Et10_SiR.data[etat]+=Et10_SiR2.data[etat]
for etat in etats_tous:
   Et10_SiR.data[etat]+=Et10_SiR2.data[etat]
for etat in translocations:
   Et10_SiR.data_trans[etat]+=Et10_SiR2.data_trans[etat]
   Et10_SiR.data_trans_lis[etat]+=Et10_SiR2.data_trans_lis[etat]
Et10_SiR.data_total+=Et10_SiR2.data_total

Et10_SansSiR=Selection(liste_date=["2016-04-19 17:01","2016-04-12 12:55","2016-04-08 15:06"],etirement=10)
temoin_SansSiR=Selection(liste_date=["2016-04-19 15:42","2016-04-12 10:55","2016-04-08 11:06","2016-01-21 13:56"])

def Create_dic(liste_exp):
   new_dic={}
   for exp in liste_exp:
      if type(exp)!=type({}):
         liste_exp[liste_exp.index(exp)]=exp.dic_cell
      for key in exp.keys():
         new_dic[str(liste_exp.index(exp))+"_"+key]=exp[key]
   return new_dic



def etat_initial(n,ci,hi,ni):
    #N nombre de cellules
    C=0
    H=0
    N=0
    for i in range(n):
        tirage=random.random()
        if tirage<=ci/(ci+hi+ni):
            C+=1
        elif tirage>=(ci+hi)/(ci+hi+ni):
            N+=1
        else:
            H+=1
    return C,H,N

def evolution(c,h,n,Toutes):
    data={}
    data['C']=np.zeros(115)
    data['H']=np.zeros(115)
    data['N']=np.zeros(115)
    data['C'][0]=c
    data['H'][0]=h
    data['N'][0]=n
    data_trans={}
    for etat in translocations:
        data_trans[etat]=np.zeros(115)

    data_trans_toutes=Toutes.data_trans
    data_total_toutes=Toutes.data
        
    
    for i in range(1,115):
        for cell in range(int(data['C'][i-1])):
            
            if data_total_toutes['C'][i+5]!=0:
                tirage=random.random()
                if tirage<=data_trans_toutes['ch'][i+5]/data_total_toutes['C'][i+5]:
                    data['H'][i]+=1
                    data_trans['ch'][i]+=1
                elif tirage>=1-data_trans_toutes['cn'][i+5]/data_total_toutes['C'][i+5]:
                    data['N'][i]+=1
                    data_trans['cn'][i]+=1
                else:
                    data['C'][i]+=1
            else:
                data['C'][i]+=1
            

        for cell in range(int(data['H'][i-1])):
            if data_total_toutes['N'][i+5]!=0:
                tirage=random.random()
                if tirage<=data_trans_toutes['hc'][i+5]/data_total_toutes['H'][i+5]:
                    data['C'][i]+=1
                    data_trans['hc'][i]+=1
                
                
                elif tirage>=1-data_trans_toutes['hn'][i+5]/data_total_toutes['H'][i+5]:
                    data['N'][i]+=1
                    data_trans['hn'][i]+=1
                else:
                    data['H'][i]+=1
            else:
                data['H'][i]+=1

        for cell in range(int(data['N'][i-1])):
            if data_total_toutes['N'][i+5]!=0:
                tirage=random.random()
                if tirage<=data_trans_toutes['nh'][i+5]/data_total_toutes['N'][i+5]:
                    data['H'][i]+=1
                    data_trans['nh'][i]+=1
                elif tirage>=1-data_trans_toutes['nc'][i+5]/data_total_toutes['N'][i+5]:
                    data['C'][i]+=1
                    data_trans['nc'][i]+=1
                else:
                    data['N'][i]+=1
            else:
                data['N'][i]+=1

    return data,data_trans

def evolution2(c,h,n,Toutes):
    #On fait varier le nombre de cellules au cours du temps, comme dans les expériences
    data={}
    data['C']=np.zeros(115)
    data['H']=np.zeros(115)
    data['N']=np.zeros(115)
    data['C'][0]=c
    data['H'][0]=h
    data['N'][0]=n
    data_trans={}
    for etat in translocations:
        data_trans[etat]=np.zeros(115)

    data_trans_toutes=Toutes.data_trans
    data_total_toutes=Toutes.data
        
    
    for i in range(1,115):
        
        for cell in range(int(data['C'][i-1])):
            
            if data_total_toutes['C'][i+5]!=0:
                tirage=random.random()
                if tirage<=data_trans_toutes['ch'][i+5]/data_total_toutes['C'][i+5]:
                    data['H'][i]+=1
                    data_trans['ch'][i]+=1
                elif tirage>=1-data_trans_toutes['cn'][i+5]/data_total_toutes['C'][i+5]:
                    data['N'][i]+=1
                    data_trans['cn'][i]+=1
                else:
                    data['C'][i]+=1
            else:
                data['C'][i]+=1
            

        for cell in range(int(data['H'][i-1])):
            if data_total_toutes['N'][i+5]!=0:
                tirage=random.random()
                if tirage<=data_trans_toutes['hc'][i+5]/data_total_toutes['H'][i+5]:
                    data['C'][i]+=1
                    data_trans['hc'][i]+=1
                
                
                elif tirage>=1-data_trans_toutes['hn'][i+5]/data_total_toutes['H'][i+5]:
                    data['N'][i]+=1
                    data_trans['hn'][i]+=1
                else:
                    data['H'][i]+=1
            else:
                data['H'][i]+=1

        for cell in range(int(data['N'][i-1])):
            if data_total_toutes['N'][i+5]!=0:
                tirage=random.random()
                if tirage<=data_trans_toutes['nh'][i+5]/data_total_toutes['N'][i+5]:
                    data['H'][i]+=1
                    data_trans['nh'][i]+=1
                elif tirage>=1-data_trans_toutes['nc'][i+5]/data_total_toutes['N'][i+5]:
                    data['C'][i]+=1
                    data_trans['nc'][i]+=1
                else:
                    data['N'][i]+=1
            else:
                data['N'][i]+=1
        if data['C'][i]+data['N'][i]+data['H'][i]<Toutes.data_total[i+5]:
            c_add,h_add,n_add=etat_initial(int(Toutes.data_total[i+5]-(data['C'][i]+data['N'][i]+data['H'][i])),data['C'][i],data['H'][i],data['N'][i])
            data['C'][i]+=c_add
            data['H'][i]+=h_add
            data['N'][i]+=n_add
        elif data['C'][i]+data['N'][i]+data['H'][i]>Toutes.data_total[i+5]:
            for j in range(int((data['C'][i]+data['N'][i]+data['H'][i])-Toutes.data_total[i+5])):
                tirage=random.random()
                if tirage<data['C'][i]/(data['C'][i]+data['N'][i]+data['H'][i]):
                    data['C'][i]-=1
                elif tirage>1-data['N'][i]/(data['C'][i]+data['N'][i]+data['H'][i]):
                    data['N'][i]-=1
                else:
                    data['H'][i]-=1
            


    return data,data_trans


def Simulation(Nombre,ci,hi,ni,Toutes):
    data_all={}
    data_trans_all={}
    for etat in etats_simple:
        data_all[etat]=[]
    for etat in translocations:
        data_trans_all[etat]=[]

    for i in range(Nombre):
        c,h,n=etat_initial(100,ci,hi,ni)
        data,data_trans=evolution(c,h,n,Toutes)
        for etat in etats_simple:
            data_all[etat].append(data[etat])
        for etat in translocations:
            data_trans_all[etat].append(data_trans[etat])

    return data_all,data_trans_all

def Simulation2(Nombre,ci,hi,ni,Toutes):
    data_all={}
    data_trans_all={}
    for etat in etats_simple:
        data_all[etat]=[]
    for etat in translocations:
        data_trans_all[etat]=[]

    for i in range(Nombre):
        c,h,n=etat_initial(100,ci,hi,ni)
        data,data_trans=evolution2(c,h,n,Toutes)
        for etat in etats_simple:
            data_all[etat].append(data[etat])
        for etat in translocations:
            data_trans_all[etat].append(data_trans[etat])

    return data_all,data_trans_all

def plot_CHN_IC(data_all,data_trans_all,liste_exp,labels,colors):
   for etat in etats_simple:
      pl.subplot(3,1,etats_simple.index(etat)+1)
      pl.errorbar(np.arange(len(np.median(data_all[etat],axis=0)))+5,
                  np.median(data_all[etat],axis=0)/(np.median(data_SiR['C'],axis=0)+np.median(data_SiR['H'],axis=0)+np.median(data_SiR['N'],axis=0)),
                  yerr=[np.median(data_all[etat],axis=0)/(np.median(data_SiR['C'],axis=0)+np.median(data_SiR['H'],axis=0)+np.median(data_SiR['N'],axis=0))
                        -np.percentile(data_all[etat],2.5,axis=0)/(np.median(data_SiR['C'],axis=0)+np.median(data_SiR['H'],axis=0)+np.median(data_SiR['N'],axis=0)),
                        np.percentile(data_all[etat],100-2.5,axis=0)/(np.median(data_SiR['C'],axis=0)+np.median(data_SiR['H'],axis=0)+np.median(data_SiR['N'],axis=0))
                        -np.median(data_all[etat],axis=0)/(np.median(data_SiR['C'],axis=0)+np.median(data_SiR['H'],axis=0)+np.median(data_SiR['N'],axis=0))],
                  color='k')
      for exp in liste_exp:
         pl.plot(exp.data[etat]/exp.data_total,
                 marker='o',
                 color=colors[liste_exp.index(exp)],
                 label=labels[liste_exp.index(exp)])
      pl.xlim(5,110)
      pl.legend()
   pl.show()

def plot_transloc_IC(data_all,data_trans,liste_exp,labels,colors,direction):
   if direction=="e":
      liste_etat=['ch','hn','cn']
   else:
      liste_etat=['hc','nh','nc']

   median=np.cumsum(data_trans[liste_etat[0]],axis=1)/100

   for etat in liste_etat[1:]:
      median+=np.cumsum(data_trans[etat],axis=1)/100

   pl.errorbar(np.arange(len(np.median(median,axis=0)))+5,
               np.median(median,axis=0),
               yerr=[np.median(median,axis=0)-np.percentile(median,2.5,axis=0),np.percentile(median,100-2.5,axis=0)-np.median(median,axis=0)],
               color='k')

   for exp in liste_exp:
      temp=np.zeros(len(exp.data_trans['ch']))
      for etat in liste_etat:
         temp+=np.cumsum(exp.data_trans[etat])
      pl.plot(np.arange(len(temp)),
              temp/max(exp.data_total),
              marker="o",
              color=colors[liste_exp.index(exp)],
              label=labels[liste_exp.index(exp)])
   pl.legend(loc="upper left")
   pl.show()

def Evt_par_cell(exp):
   count=[]
   for i in range(6):
      result=cur.execute("Select count() "+exp.select_string+" AND Cellules.etatf!='d' "+" AND Cellules.etat"+str(i)+"!='d'")
      for r in result:
         count.append(r[0])

   return np.array(count[:-1])-np.array(count[1:])

def Evt_par_cell2(exp):
   count=[]
   for i in range(6):
      result=cur2.execute("Select count() "+exp.select_string+" AND Cellules.etatf!='d' "+" AND Cellules.etat"+str(i)+"!='d'")
      for r in result:
         count.append(r[0])

   return np.array(count[:-1])-np.array(count[1:])
      
def Evt_par_cell_plus(exp,condition):
   count=[]
   for i in range(6):
      result=cur.execute("Select count() "+exp.select_string+" AND Cellules.etatf!='d' "+" AND Cellules.etat"+str(i)+"!='d' "+condition)
      for r in result:
         count.append(r[0])

   return np.array(count[:-1])-np.array(count[1:])   
      
      
N=[0,0,0,0]+[1]*6+[2,4,5,6,8,12,12,12,12,11]+[12]*6+[11,11,11,11]+[12]*16+[13,13]+[14]*9+[15]+[16]*12+[14]*5+[13]+[12]*6+[13,13]+[14]*5+[12]*32
H=[0,0,0,1,1,1,1,2,2,2,2,2,7,10,11,14,17,19,19,21,25,24,22,20,21,20,23,23,24,25,25,24,24,23,23,23,23,22,23,22,22,22,22,23,24,24,23,24,23,24,24,23,23,23,22,22,22,21,20,20,20,20,19,19,19,19,20,20,20,20,21,21,21,21,21,21,21,21]+[21]*4+[20,20]+[19]*3+[20,21]+[23]*6+[22]+[23]*3+[25,25]+[24]*10+[23,23]+[24]*7+[25]
C=[0,0,0,0,2,2,2,4,4,5,7,14,18,18,23,31,35,39,41,42,42,44,46,48,47,49,49,49,49,50,51,52,52,53,53,53,53,54,53,54,54,54,54,53,52,52,52,51,51,50,50,51,50,50,51,51,51,51,51,51,51,51,52,52,52,52,51,51,51,51,51,51,51,51,51,52,52,52,52,52,52,52,52,52,52,52,52,51,50,49,49,49,49,49,49,50,49,49,49,47,47,47]+[47]*11+[46]*7+[45]
  
