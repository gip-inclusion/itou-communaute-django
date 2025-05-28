# La communauté de l'inclusion

## Initial dev setup

### Environnement virtuel

Installer l'environnement virtuel et les dépendances :

```bash
$ uv sync
```

## direnv

Nous conseillons d'installer le minuscule utilitaire `direnv` pour charger et
décharger automatiquement des variables d'environnement à l'entrée dans un
répertoire.

Une fois muni de cet outil (avec `apt`, `brew` ou autre, et sans oublier de
[mettre le hook](https://direnv.net/#basic-installation)) il suffit de créer un
fichier de variables d'environnement local:

```sh
cat <<EOF >.envrc
# Activate the virtual environment
source .venv/bin/activate
# Setting environment variables for the application
export DJANGO_DEBUG=True
export DJANGO_LOG_LEVEL=WARNING
export SQL_LOG_LEVEL=INFO
export DJANGO_SECRET_KEY=foobar
# For psql
export PGDATABASE=communaute
export PGHOST=localhost
export PGUSER=communaute
export PGPASSWORD=password
EOF
```

Une fois le fichier `.envrc` saisit, il suffit de l'autoriser dans `direnv`:

```sh
direnv allow
```

Et c’est bon, vos variables seront chargées à chaque entrée dans le dossier et
retirées en sortant.

```sh
psql  # connects directly to the communaute database
./manage.py xxxx  # any commands work immediately
```

Accéder à l'environnement virtuel :

```bash
$ source .venv/bin/activate
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

## Préparer l'environnement de données

```bash
$ python manage.py createcachetable
$ python manage.py migrate
$ python manage.py configure_bucket
$ python manage.py populate
```

### restaurer une base de données

* le client postgresql doit être installé sur la machine hôte
* le script `./scripts/scripts/import-latest-db-backup.sh` doit être exécuté


## Mises à jour

Ajouter d'une dépendance :

```bash
$ uv add django-anymail
```

Ajouter d'une dépendance de développement :

```bash
$ uv add --dev beautifulsoup4
```

Mettre à jour les dépendances :

```bash
$ uv lock
```

Mettre à jour son environnement virtuel :

```bash
$ uv sync
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

### Premier déploiement
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
- UV_PROJECT_ENVIRONMENT

### Variables d'environnement
Dans votre environnement de développement, l’utilisation de
direnv est recommandée.

En production, un fichier `.env` est généré au déploiement et chargé avec
l’utilitaire [`dotenv`](https://pypi.org/project/python-dotenv/). Cette
configuration est moins flexible que direnv, car les variables d’environnement
ne sont pas disponibles pour votre shell, ce qui empêche le chargement
automatique de l’environnement virtuel, ou de lancer `psql` sans spécifier les
arguments pour se connecter à la base de données.

### pour le déploiment des recettes jetables

Créer et lier les addons (différents de ceux de production ^^)

- postgresql
- cellar S3 storage
- configuration provider

Ajouter les secrets suivants dans le repo git

- CLEVER_REVIEW_APPS_CONFIGURATION_ADDON
- CLEVER_REVIEW_APPS_ORG
- CLEVER_REVIEW_APPS_S3_ADDON
