# La communauté de l'inclusion

## Initial dev setup

Installer l'environnement virtuel et les dépendances :

```bash
$ poetry install
```

Copier le fichier `.env.template` en `.env` et le modifier en fonction de vos besoins.

```bash
$ cp .env.template .env
```

Accéder à l'environnement virtuel :

```bash
$ poetry shell
```

## Démarrer les instances

Démarer la base de données et le bucket S3

```bash
$ docker-compose up -d
```

Démarrer le service web

```bash
$ python manage.py runserver_plus
```

NB : pour démarrer la stack complète sous docker-compose

```bash
$ docker-compose --profile django up
```

## Préparer l'environnement de données

```bash
$ python manage.py createcachetable
$ python manage.py migrate
$ python manage.py populate
$ python manage.py configure_bucket
```

NB : accéder au bash du conteneur `commu_django` pour exécuter ces commandes

```bash
$ docker exec -it commu_django bash
```

### restaurer une base de données

* le client postgresql doit être installé sur la machine hôte
* le script `./scripts/scripts/import-latest-db-backup.sh` doit être exécuté


## Mises à jour

Ajouter d'une dépendance :

```bash
$ poetry add django-anymail
```

Ajouter d'une dépendance de développement :

```bash
$ poetry add --group dev poethepoet
```

Mettre à jour des dépendances :

```bash
$ poetry update;poetry lock
```

Générer les fichiers `requirements`

```bash
$ poetry run poe export;poetry run poe export_dev
```

## Développement

### Déboguer pas à pas

Le débogueur démarre par défaut avec `debugpy`.

Il vous reste juste à configurer votre IDE pour qu'il s'y attache. Dans VSCode, il suffit de créer le fichier `launch.json` dans le répertoire `.vscode` comme suit :

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python Django with venv",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/manage.py",
            "args": [
                "runserver"
            ],
            "django": true,
            "justMyCode": true
        }
    ]
}

```

Vous pourrez dès lors placer des points d'arrêt dans le code en survolant le numéro de ligne dans la colonne à gauche et de lancer le débogueur (qui ne fera que s'attacher au serveur de deboguage qui tourne dans votre conteneur).

### Lancer les tests en distribué

```bash
pytest --numprocesses=logical --create-db
```

## Déploiement sur Clever Cloud

Ajouter les secrets suivants dans le repo git

- CLEVER_SECRET
- CLEVER_TOKEN

Créer et lier les addons

- postgresql
- cellar S3 storage
- configuration provider

Créer les variables d'environnement suivantes dans le configuration provider

- CC_PIP_REQUIREMENTS_FILE
- CC_PRE_BUILD_HOOK
- CC_PRE_RUN_HOOK
- CC_PYTHON_BACKEND
- CC_PYTHON_MANAGE_TASKS
- CC_PYTHON_MODULE
- CC_PYTHON_VERSION
- CC_UWSGI_DISABLE_FILE_WRAPPER
- DJANGO_SETTINGS_MODULE
- PORT
- PYTHONPATH
- STATIC_FILES_PATH
- STATIC_URL_PREFIX

### pour le déploiment des recettes jetables

Créer et lier les addons (différents de ceux de production ^^)

- postgresql
- cellar S3 storage
- configuration provider

Ajouter les secrets suivants dans le repo git

- CLEVER_REVIEW_APPS_CONFIGURATION_ADDON
- CLEVER_REVIEW_APPS_ORG
- CLEVER_REVIEW_APPS_S3_ADDON
