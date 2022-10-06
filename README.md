# Itou - La communauté de l'inclusion

## Poetry

### Lancer le serveur local

#### Configuration environnement

```bash
$ cp .env.template .env
```

Installation des dependances avec Poetry
```bash
$ poetry install
```

#### Lancement

Pour utiliser Poetry avec les commandes du fichier `Makefile`, ajoutez les variables d'environnement :

* `USE_POETRY` à la valeur 1
* `DJANGO_SETTINGS_MODULE` pour activer les settings de prod (`config.settings.base`) ou de dev (`config.settings.dev`)


```bash
$ make server
```


### Ajout de dépendance

Ajout d'une dépendance :

```bash
poetry add django-anymail
```

Ajout d'une dépendance de développement :

```bash
poetry add --group dev poethepoet
```

### Mise à jour des dépendances

```bash
poetry update
poetry lock
```

### Générer les fichiers `requirements`

```bash
poetry run poe export
poetry run poe export_dev
```

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

## Docker


### Lancer le serveur local

```bash
$ cp .env.template .env
```

Pour Docker, mettre : `POSTGRESQL_ADDON_HOST=postgres`.

```bash
$ docker-compose up -d
```

Visitez la page d'accueil du projet : http://localhost:8000.

Si le port 8000 ne vous convient pas, vous pouvez définir la variable `DJANGO_PORT_ON_DOCKER_HOST` dans votre `.env` pour mettre le port que vous souhaitez.

### Déboguer pas à pas

Le débogueur démarre par défaut avec `debugpy` dans le conteneur Django sur le port 5678 (que vous pouvez changer avec la variable d'environnement `DJANGO_DEBUGPY_PORT`).
Il vous reste juste à configurer votre IDE pour qu'il s'y attache. Dans VSCode, il suffit de créer le fichier `launch.json` dans le répertoire `.vscode` comme suit :

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Attacher",
            "type": "python",
            "request": "attach",
            "connect": {
                "host": "127.0.0.1",
                "port": 5678
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}",
                    "remoteRoot": "/app"
                }
            ],
            "django": true
        }
    ]
}
```

Vous pourrez dès lors placer des points d'arrêt dans le code en survolant le numéro de ligne dans la colonne à gauche et de lancer le débogueur (qui ne fera que s'attacher au serveur de deboguage qui tourne dans votre conteneur).
