from astropy import units as u
from astropy.coordinates import SkyCoord
from gammapy.data import EventList
from gammapy.datasets import MapDataset
from astropy.table import vstack as vstack_tables
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
import pandas as pd
import os

# Changer le répertoire de travail, à changer ou à effacer
os.chdir("C:/Users/trann/Documents/IUT/sem 2/sae/2.6/work")

# Fonction pour convertir le temps en MET (Mission Elapsed Time)
def datelisible_vers_MET(chaine):
    from astropy.time import Time
    t = Time([chaine])
    t0 = Time(['2001-01-01T00:00:00.0'])
    delta = t - t0
    return delta.sec[0]

# Lire les coordonnées des émetteurs depuis un fichier CSV
list_emetteurs = pd.read_csv('coor_18emetteurs.csv', sep=';')

# Demander la période d'observation
period = int(input("Choisissez le numéro de période (1, 2 ou 3): "))
nom_period = "period_" + str(period)
week_debut = 10  # Car nos périodes commence par w010, w210, w410

# Définir le chemin d'accès en fonction de la période choisie
path_period = "lat_photon_weekly_w" + str((period - 1) * 2)  # pour obtenir le bout du nom de fichier
print(list_emetteurs)

# Filtrer la liste des émetteurs selon la classe demandée
class_demand = input("Choisissez la classe d'émetteur (agn, bcu...): ")
condition = list_emetteurs['Class'] == class_demand
list_emetteurs = list_emetteurs[condition].reset_index(drop=True)
print(list_emetteurs)

# Choisir un émetteur spécifique à partir de la liste filtrée
nb_emet = int(input("Choisissez l'émetteur que tu veux (0, 1 ou 2): "))
nom_emet = str(nb_emet + 1) + "_" + list_emetteurs['Class'][nb_emet]
L_cible = list_emetteurs['Gal l'][nb_emet]
B_cible = list_emetteurs['Gal b'][nb_emet]
print("On visualise le ", nom_emet, L_cible, B_cible)
nb_week = list_emetteurs['NB WEEK'][nb_emet]

nom_emet = "period_" + str(period) + "_" + str(nb_emet + 1) + "_" + list_emetteurs['Class'][nb_emet]
week_fin = week_debut + nb_week - 1

# Parcourir les fichiers FITS selon les coordonnées L et B et le numéro des semaines observées de l'émetteur
for i in range(week_debut, week_debut + nb_week):
    path = path_period + str(i) + "_p305_v001.fits"
    print("Exécute jusqu'à la semaine: ", str(i - week_debut + 1), "/", str(nb_week), "de l'émetteur: ", nom_emet)
    events = EventList.read(path)

    # Filtrer les données
    zenith_max_mask = events.table['ZENITH_ANGLE'] <= 100
    energy_min_mask = events.table['ENERGY'] >= 100
    energy_max_mask = events.table['ENERGY'] <= 300000
    events.table = events.table[zenith_max_mask & energy_min_mask & energy_max_mask]

    # Combiner les événements de plusieurs fichiers
    if i == week_debut:
        events_total = events
    else:
        events_new = events
        events_total = EventList.from_stack([events_total, events_new])

print(events_total)
print("Nom des colonnes:")
print(events_total.table.colnames)

print("\nDates de mesure:")
print("Début:", events_total.time[0].iso)
print("Fin:", events_total.time[-1].iso)

# Constituer le fichier CSV sur disque
# df.to_csv("exportation_lat_photon_weekly_w020_p305_v001.csv", sep=";", index=False)

# Pointer sur un émetteur
gc_pos = SkyCoord(L_cible, B_cible, unit="deg", frame="galactic")

# Créer un objet carte paramétré
counts = Map.create(
    skydir=gc_pos,
    map_type='wcs',
    proj="AIT",
    frame="galactic",
    width=(10, 10),  # Sur un émetteur
    binsz=0.1,
    dtype=float,
)

print("\nInfos carte:")
print(counts.geom)

# Remplissage des données de la carte avec les données du fichier FITS de events
counts.fill_events(events_total)

# Affichage de la carte brute logarithmique
plt.figure(0, figsize=(10, 5))
counts.plot(stretch="log", add_cbar=True)
plt.title(" ")
plt.xlabel(" ")
plt.ylabel(" ")
ax = plt.gca()
plt.text(0.5, 1.1, "Energies en MeV - échelle logarithmique",
horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
plt.gca().xaxis.set_ticklabels([])
plt.gca().yaxis.set_ticklabels([])
plt.text(0.5, -0.1, "Longitude galactique (degrés)", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
plt.text(-0.1, 0.5, "Latitude galactique (degrés)", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, rotation=90)
plt.show()

# Affichage de la carte adoucie linéaire
plt.figure(1, figsize=(10, 5))
counts.smooth(0.1 * u.deg, kernel="gauss").plot(stretch="linear", add_cbar=True)
plt.title(" ")
plt.xlabel(" ")
plt.ylabel(" ")
ax = plt.gca()
plt.text(0.5, 1.1, "Energies en MeV ADOUCIES - échelle linéaire", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
plt.gca().xaxis.set_ticklabels([])
plt.gca().yaxis.set_ticklabels([])
plt.text(0.5, -0.1, "Longitude galactique (degrés)", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
plt.text(-0.1, 0.5, "Latitude galactique (degrés)", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, rotation=90)
plt.show()

# Affichage de la carte adoucie logarithmique
plt.figure(2, figsize=(10, 5))
counts.smooth(0.1 * u.deg, kernel="gauss").plot(stretch="log", add_cbar=True)
plt.title(" ")
plt.xlabel(" ")
plt.ylabel(" ")
ax = plt.gca()
plt.text(0.5, 1.1, "Energies en MeV ADOUCIES - échelle logarithmique", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
plt.gca().xaxis.set_ticklabels([])
plt.gca().yaxis.set_ticklabels([])
plt.text(0.5, -0.1, "Longitude galactique (degrés)", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
plt.text(-0.1, 0.5, "Latitude galactique (degrés)", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, rotation=90)
plt.show()
