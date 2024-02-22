from django.db import models


class ActiveSearch(models.TextChoices):
    NO = "NO", "Je ne suis pas en recherche"
    Internship = "INTERNSHIP", "Je suis en recherche active de stage de CIP"
    Apprenticeship = "APPRENTICESHIP", "Je suis en recherche active d'apprentissage de CIP"


class Regions(models.TextChoices):
    RXX = "XX", "---------"
    R00 = "00", "France entière"
    R84 = "84", "Auvergne-Rhône-Alpes"
    R27 = "27", "Bourgogne-Franche-Comté"
    R53 = "53", "Bretagne"
    R24 = "24", "Centre-Val de Loire"
    R94 = "94", "Corse"
    R44 = "44", "Grand Est"
    R01 = "01", "Guadeloupe"
    R03 = "03", "Guyane"
    R32 = "32", "Hauts-de-France"
    R11 = "11", "Île-de-France"
    R04 = "04", "La Réunion"
    R02 = "02", "Martinique"
    R06 = "06", "Mayotte"
    R28 = "28", "Normandie"
    R75 = "75", "Nouvelle-Aquitaine"
    R76 = "76", "Occitanie"
    R52 = "52", "Pays de la Loire"
    R93 = "93", "Provence-Alpes-Côte d’Azur"
