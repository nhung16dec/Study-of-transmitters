import os
import pandas as pd

# Changer le répertoire de travail
os.chdir('C:/Users/trann/Documents/IUT/sem 2/sae/2.6/donnee')

# Ouvrir le fichier de données brut contenant des informations sur L, B, énergie, etc. des émetteurs dans notre partie du ciel
df = pd.read_csv("donnee_brut.csv", sep=";")

# Filtrer par les colonnes importantes
noms = ['Class', 'Gal l', 'Gal b', 'Energy Flux']
extrait = df.filter(items=noms)

# Convertir la colonne 'Class' en minuscules
extrait['Class'] = extrait['Class'].str.lower()

# Vu que le type de 'Energy Flux' est une chaîne de caractères, le changer en numérique
extrait['Energy Flux'] = extrait['Energy Flux'].astype(float)

# Filtrer selon la classe
classes_emetteurs = ['psr', 'agn', 'fsrq', 'bll', 'bcu', 'unk', 'snr']
condition = extrait["Class"].isin(classes_emetteurs)
extrait = extrait[condition]

# Choisir les plus grandes valeurs de photons pour chaque type d'émetteur
BLZ = ['fsrq', 'bll', 'bcu']

def nombre_choisir(group):
    if group.name in BLZ:
        return group.nlargest(2, 'Energy Flux')
    else:
        return group.nlargest(3, 'Energy Flux')

list_emetteurs = extrait.groupby('Class').apply(nombre_choisir).reset_index(drop=True)

# Ajouter la colonne 'NB WEEK' correspondant avec chaque émetteur
def nombre_semaine(type):  # Fonction pour obtenir le nombre de semaines correspondant au type d'émetteur
    if type['Class'] in ['agn', 'unk']:
        return 30
    elif type['Class'] == 'psr':
        return 5
    else:
        return 10

list_emetteurs['NB WEEK'] = list_emetteurs.apply(nombre_semaine, axis=1)

# Enregistrer dans un fichier CSV
list_emetteurs.to_csv('coor_18emetteurs.csv', sep=';', index=False)
print(list_emetteurs)
