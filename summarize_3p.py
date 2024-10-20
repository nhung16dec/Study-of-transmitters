import pandas as pd
import os
import glob
import math
# Chemin d'accès au répertoire contenant les fichiers
directory_path = "C:/Users/trann/Documents/IUT/sem 2/sae/2.6/donnee"
os.chdir(directory_path)
# Lire le fichier contenant les coordonnées des émetteurs
noms=[]
coor_emet = pd.read_csv('coor_18emetteurs.csv', sep=';')

for id_emet in range(len(coor_emet)):
    noms.append(str(id_emet+1)+"_"+coor_emet.iloc[id_emet,0])
coor_emet['nom']=noms

# Créer une liste des colonnes pour le DataFrame
columns = ['nom', 'moyenne', 'cL', 'cB', 'nombre', 'somme', 'min', 'q1', 'mediane', 'q3', 'max', 'ecart_type','marge','borne_sup','borne_inf']
for id_bilan in range(3):
    bilan = 'bilan_3p'+str(id_bilan*500)
    for nom in noms:
        fichiers_p = glob.glob(os.path.join(directory_path, '*'+nom+'.csv')) # Obtenir la liste des fichiers de "*nom" dans le répertoire
        for chemin_fichier in fichiers_p:
            data_p = pd.read_csv(chemin_fichier, sep=";")
            #pour concatener 3 périodes d'un émetteurs
            if chemin_fichier == fichiers_p[0]:
                data = data_p
            else:
                data = pd.concat([data,data_p],ignore_index=True)
        if id_bilan == 1:
            data = data[data['ENERGY'] < 500]
        elif id_bilan == 2:
            data = data[(data['ENERGY'] > 500) & (data['ENERGY'] < 1000)]
        nombre = len(data)
        moyenne = data['ENERGY'].mean()
        somme = data['ENERGY'].sum()
        min_energy = data['ENERGY'].min()
        q1 = data['ENERGY'].quantile(0.25)
        mediane = data['ENERGY'].median()

        q3 = data['ENERGY'].quantile(0.75)
        max_energy = data['ENERGY'].max()
        ecart_type = data['ENERGY'].std()
        #calculer intervalle de confiance
        niveau_confiance = 0.95
        from scipy.stats import norm
        niveau_confiance = 0.95
        z_alpha_sur_2 = norm.ppf(1-(1-niveau_confiance)/2)
        marge=z_alpha_sur_2 *ecart_type/math.sqrt(nombre)
        borne_sup = moyenne+marge
        borne_inf = moyenne-marge
        # Trouver cL et cB correspondant à 'nom'
        for j in range(len(coor_emet)):
            if coor_emet.iloc[j, 5] == nom:
                cL = coor_emet.iloc[j, 2]
                cB = coor_emet.iloc[j, 3]
        df1 = pd.DataFrame([{'nom': nom, 'moyenne': moyenne, 'cL': cL, 'cB': cB, 'nombre': nombre,'somme': somme, 'min': min_energy, 'q1': q1, 'mediane': mediane, 'q3': q3,'max': max_energy, 'ecart_type': ecart_type,'marge': marge,'borne_sup': borne_sup,'borne_inf': borne_inf}])
        if nom == noms[0]:
            df = df1
        else:
            df = pd.concat([df, df1], ignore_index=True)
    df.to_csv(bilan+".csv", sep=";", index=False)
"""