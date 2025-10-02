# Sujets à corriger à la reprise du projet

## État des dépendances

https://github.com/ellmetha/django-machina semble être en mode maintenance au
mieux, pas de nouveau développements. Ce projet est basé sur
https://github.com/django-mptt/django-mptt, qui n’est plus maintenu.

## Bucket S3

Voir la branche git `ff/minio` pour un peu de code brouillon qui illustre l’idée.

### Configuration continue

Appliquer la _management command_ `configure_bucket` via
`CC_PYTHON_MANAGE_TASKS` en prod systématiquement, en configurant la politique
d’accès à tous les buckets.

### Tests
Faire tourner les tests contre un bucket S3 dans une organisation séparée au
lieu de MinIO, pour être plus représentatif de l’environnement de production
(cf. `AWS_S3_CLIENT_CONFIG`).

Isoler les accès au bucket entre les tests (ex. fixture pytest
https://github.com/gip-inclusion/les-emplois/blob/0f6e2717302ee68bb96bc6bac96dadcb01059001/tests/conftest.py#L188-L228)
