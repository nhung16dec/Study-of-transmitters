import pandas as pd
import os
import glob
import math
# Chemin d'accès au répertoire contenant les fichiers
directory_path = "C:/Users/trann/Documents/IUT/sem 2/sae/2.6/donnee"
os.chdir(directory_path)
# Lire le fichier contenant les coordonnées des émetteurs pour avoir le nom des émetteur
nom=[]
coor_emet = pd.read_csv('coor_18emmetteurs.csv', sep=';')
for id_emmet in range(len(coor_emet)):
    nom.append(str(id_emmet+1)+"_"+coor_emet.iloc[id_emmet,0])
coor_emet['nom']=nom

# Obtenir la liste des fichiers period_* dans le répertoire
fichiers = glob.glob(os.path.join(directory_path, 'period_*'))

# Créer une liste des colonnes pour le DataFrame
columns = ['nom', 'moyenne', 'cL', 'cB', 'nombre', 'somme', 'min', 'q1', 'mediane', 'q3', 'max', 'ecart_type','marge','borne_sup','borne_inf','temps','annee']

# Créer un nouveau DataFrame avec des colonnes qui sont fait
df = pd.DataFrame(columns=columns)

for id_bilan in range(3):
    bilan = 'bilan'+str(id_bilan*500)#pour obtenir le nom: bilan0,bilan500,bilan1000
    #boucle pour parcourir des fichiers avons fait avec le code etude_emetteur.py
    for chemin_fichier in fichiers:
        data = pd.read_csv(chemin_fichier, sep=";")
        if id_bilan == 1:#pour filtrer l'énergie
            data = data[data['ENERGY'] < 500]
        if id_bilan == 2:
            data = data[(data['ENERGY'] > 500) & (data['ENERGY'] < 1000)]

        repertoire, nom_fichier = os.path.split(chemin_fichier)
        nom = nom_fichier[9:-4]#pour obtenir le nom: 1_agn,..18_unk (9=period_*_;-4: =.csv)
        nombre = len(data)#compter le nombre de photon = lignes
        moyenne = data['ENERGY'].mean()
        somme = data['ENERGY'].sum()
        min_energy = data['ENERGY'].min()
        q1 = data['ENERGY'].quantile(0.25)
        mediane = data['ENERGY'].median()
        data['TIME']=pd.to_datetime(data['TIME'])
        temps=data['TIME'].median()
        annee=temps.year
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

        # Ajouter les données au DataFrame
        df1 = pd.DataFrame([{'nom': nom, 'moyenne': moyenne, 'cL': cL, 'cB': cB, 'nombre': nombre,'somme': somme, 'min': min_energy, 'q1': q1, 'mediane': mediane, 'q3': q3,'max': max_energy, 'ecart_type': ecart_type,'marge': marge,'borne_sup': borne_sup,'borne_inf': borne_inf,'temps': temps,'annee':annee}])
        # il y a la condition car nous voyons une erreur quand combiner deux fichier où l'un est nul
        if chemin_fichier == fichiers[0]:
            df = df1
        else:
            df = pd.concat([df, df1], ignore_index=True)

    # Écrire le DataFrame dans un fichier CSV
    df.to_csv(bilan+".csv", sep=";", index=False)
