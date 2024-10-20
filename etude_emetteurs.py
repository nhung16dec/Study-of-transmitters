import os
os.chdir("C:/Users/trann/Documents/IUT/sem 2/sae/2.6/work")
import pandas as pd
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.table import vstack as vstack_tables
from gammapy.data import EventList
from gammapy.datasets import MapDataset
from gammapy.irf import PSFMap, EDispKernelMap
from gammapy.maps import Map, MapAxis, WcsGeom
from gammapy.modeling.models import (
    PowerLawSpectralModel,
    PointSpatialModel,
    SkyModel,
    TemplateSpatialModel,
    PowerLawNormSpectralModel,
    Models,
    create_fermi_isotropic_diffuse_model,
)
from gammapy.modeling import Fit
import matplotlib.pyplot as plt


#Ouvrir le fichier csv pour lire des L,B,numéro de semaine observé
list_emetteurs.to_csv('coor_18emetteurs.csv',sep=';',index=False)


def datelisible_vers_MET(chaine):
    from astropy.time import Time
    t=Time([chaine])
    t0=Time(['2001-01-01T00:00:00.0'])
    delta=t-t0
    return delta.sec[0]
def MET_vers_datelisible(MET):
    import datetime
    debutMET=datetime.datetime(2001,1,1,0,0,0)
    stamp_debutMET=debutMET.timestamp()
    stamp=stamp_debutMET+MET
    date=datetime.datetime.fromtimestamp(stamp)
    return date.isoformat()
# Parcourir des fichiers fits
# Données initiales
week_debut = 10
#Parcourir les emetteurs de période 1 à période 3
for period in range(1,4):
    path_period = "lat_photon_weekly_w" + str(((period - 1) * 2))
#Parcourir des 18 emetteurs et prendre les coordonnées, le numéro des semaines observés de l'émmetteur
    for nb_emet in range(len(list_emetteurs)):
        nom_emet="period_"+str(period)+"_"+str(nb_emet+1)+"_"+list_emetteurs['Class'][nb_emet]
        L_cible = list_emetteurs['Gal l'][nb_emet]
        B_cible = list_emetteurs['Gal b'][nb_emet]
        print(nom_emet,L_cible,B_cible)
        nb_week=list_emetteurs['NB WEEK'][nb_emet]
        cadrage = 8
        week_fin=week_debut+nb_week
        #parcourir des semaines
        for i in range(week_debut,week_fin-1):
            path=path_period+str(i)+"_p305_v001.fits" #obtenir le chemin
            events="events"+str(i)
            print("Ici c'est les données de: ",nom_emet," de la semaine: ",str(i-week_debut+1),"/",nb_week) #pour savoir on est où
            events = EventList.read(path)

            # Filtrage des données

            # Convertir le temps

            DATEsource1=events.time[0].iso
            DATEsource2=events.time[-1].iso
            date_debut = datelisible_vers_MET(DATEsource1.replace(" ","T"))
            date_fin = datelisible_vers_MET(DATEsource2.replace(" ","T"))

            # Filtrage des données


            zenith_max_mask=events.table['ZENITH_ANGLE']<=100
            energy_min_mask=events.table['ENERGY']>=100
            energy_max_mask=events.table['ENERGY']<=300000

            #sens_de_detection_mask=events.table['CONVERSION_TYPE']==0
            time_min_mask=events.table['TIME']>=date_debut
            time_max_mask=events.table['TIME']<date_fin

            L_min_mask=events.table['L']>=L_cible-cadrage/2
            L_max_mask=events.table['L']<=L_cible+cadrage/2
            B_min_mask=events.table['B']>=B_cible-cadrage/2
            B_max_mask=events.table['B']<=B_cible+cadrage/2

            #theta_max_mask=events.table['THETA']<=50

            vecteur_filtre = zenith_max_mask&energy_min_mask&energy_max_mask&time_min_mask&time_max_mask&L_min_mask&L_max_mask&B_min_mask&B_max_mask#&theta_max_mask

            #print("Table avant:")
            #print(events)

            #print("\nDates de mesure:")
            #print("Début:",events.time[0].iso)
            #print("Fin:",events.time[-1].iso)

            events.table = events.table[vecteur_filtre]
            print("Table après:")
            print(events)
            #print("\nDates de mesure:")
            #print("Début:",events.time[0].iso)
            #print("Fin:",events.time[-1].iso)
            if i==week_debut:
                events_total=events
            else:
                if len(events.table)==0:
                    print("Il n'y a pas de donnée après avoir filtré")
                else:
                    events_new=events
                    events_total=EventList.from_stack([events_total,events_new])
            print("Table combinée:")
            print(events_total)

        table_finale=events_total.table[:][['ENERGY',  'L', 'B', 'THETA', 'PHI', 'ZENITH_ANGLE', 'EARTH_AZIMUTH_ANGLE', 'TIME', 'CONVERSION_TYPE']]
        df=table_finale.to_pandas()
        df['TIME']=df['TIME'].apply(MET_vers_datelisible)
        df['TIME']=pd.to_datetime(df['TIME'])
        #Constitue le fichier CSV sur disque: prend 10 à 15sec
        df.to_csv(nom_emet+'.csv',sep=";", index=False)#enregistrer des données filtrées au fichier csv
