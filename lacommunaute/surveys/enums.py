# make enmu for survey choices

from django.db import models


class DSPWorkCapacity(models.IntegerChoices):
    LEVEL0 = 0, "Est dans l’incapacité immédiate d’occuper un poste de travail"
    LEVEL1 = 1, "A besoin d’un accompagnement avant de pouvoir occuper un poste de travail"
    LEVEL2 = 2, "Peut occuper un poste de travail dans des conditions aménagées"
    LEVEL3 = 3, "Peut occuper un poste de travail dans des conditions ordinaires"


class DSPLanguageSkills(models.IntegerChoices):
    LEVEL0 = 0, "Analphabète à illettré "
    LEVEL1 = 1, "Relève d’une formation FLE et/ou savoirs de base"
    LEVEL2 = 2, "Laborieuse à limitée"
    LEVEL3 = 3, "Bonne à parfaite"


class DSPHousing(models.IntegerChoices):
    LEVEL0 = 0, "Sans domicile fixe"
    LEVEL1 = 1, "Hébergement collectif de type CHRS ou CADA…"
    LEVEL2 = 2, "Hébergement hors structure sociale, logement insalubre, risque de perte de logement"
    LEVEL3 = 3, "Logement stable"


class DSPRightsAccess(models.IntegerChoices):
    LEVEL0 = 0, "Ne connait pas ses droits, en situation de non recours"
    LEVEL1 = 1, "Renoncement ou en rupture ou difficulté de renouvellement de droits"
    LEVEL2 = 2, "Connait ses droits et démarches en cours"
    LEVEL3 = 3, "Bénéficie des droits afférents à sa situation"


class DSPMobility(models.IntegerChoices):
    LEVEL0 = 0, "Ne sait pas se rendre seul à son lieu de travail"
    LEVEL1 = (
        1,
        (
            "Sait organiser son covoiturage et/ou possède un véhicule"
            " mais problème de mise en règle (assurance, contrôle technique…)"
        ),
    )
    LEVEL2 = 2, "Sait utiliser les transports en commun et/ou possède un véhicule 2 roues"
    LEVEL3 = 3, "Possède un véhicule et permis de conduire conformes et covoiturage possible"


class DSPResources(models.IntegerChoices):
    LEVEL0 = 0, "Situation de surendettement sans dépôt de dossier et/ou sans ressources"
    LEVEL1 = 1, "Surendettement avec dossier déposé et suivi"
    LEVEL2 = 2, "Besoins primaires assurés au jour le jour et/ou mesure de protection type curatelle"
    LEVEL3 = 3, "Sait gérer son budget ; avec capacité de financer par exemple un permis de conduire"


class DSPJudicial(models.IntegerChoices):
    LEVEL0 = 0, "Exécution de peine en cours "
    LEVEL1 = 1, "Suivi SPIP/PJJ après exécution de peine"
    LEVEL2 = 2, "Aucun suivi en cours"


class DSPAvailability(models.IntegerChoices):
    LEVEL0 = 0, "Faible voire difficile (garde d’enfant ; ascendant ; famille)"
    LEVEL1 = 1, "A organiser"
    LEVEL2 = 2, "Immédiate avec des contraintes horaires"
    LEVEL3 = 3, "Immédiate et sans contraintes horaires"
