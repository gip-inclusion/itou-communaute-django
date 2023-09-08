# La communauté de l'inclusion

## Initial setup

Installer l'environnement virtuel et les dépendances :

```bash
$ poetry install
```

Creer les buckets S3 :

```bash
s3cmd mb s3://test-inclusion-public/
s3cmd setacl s3://test-inclusion-public/ --acl-public
s3cmd mb s3://test-inclusion-private/
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

Démarer la base de données

```bash
$ docker-compose up -d
```

Démarrer le service web

```bash
python manage.py runserver
```

## Peupler la base de données


```bash
python manage.py loaddata fixtures/validation_fixtures.json
```


## Mises à jour

Ajouter d'une dépendance :

```bash
poetry add django-anymail
```

Ajouter d'une dépendance de développement :

```bash
poetry add --group dev poethepoet
```

Mettre à jour des dépendances :

```bash
poetry update
poetry lock
```

Générer les fichiers `requirements`

```bash
poetry run poe export
poetry run poe export_dev
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

