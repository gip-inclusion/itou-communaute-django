# La communauté de l'inclusion

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

## Créer rapidement des forums privés dans le shell

### chargement des modèles

```
from django.contrib.auth.models import Group
from machina.core.db.models import get_model
from machina.core.loading import get_class
Forum = get_model("forum", "Forum")
ForumPermission = get_model("forum_permission","ForumPermission")
UserForumPermission = get_model("forum_permission","UserForumPermission")
GroupForumPermission = get_model("forum_permission","GroupForumPermission")
```

### creation du forum et des groupes
La variable `name` contient le nom du forum privé à créer.
```
name = 'nom du forum privé'
```

```
forum, _ = Forum.objects.get_or_create(name=name,type=0)
moderators, _ = Group.objects.get_or_create(name=f"{name} moderators")
members, _ = Group.objects.get_or_create(name=f"{name} members")
```

### ajouter les droits pour les utilisateurs anonymes
```
UserForumPermission.objects.bulk_create(
    [UserForumPermission(anonymous_user=True,authenticated_user=False,permission=permission,has_perm=False,forum=forum) for permission in ForumPermission.objects.all()
    ]
)
```

### ajouter les droits pour les utilisateurs authentifiés
```
UserForumPermission.objects.bulk_create(
    [UserForumPermission(anonymous_user=False,authenticated_user=True,permission=permission,has_perm=False,forum=forum) for permission in ForumPermission.objects.all()
    ]
)
```

### ajouter les permissions du groupe moderators
```
GroupForumPermission.objects.bulk_create(
    [GroupForumPermission(group=moderators,permission=permission,has_perm=True,forum=forum) for permission in ForumPermission.objects.all()

    ]
)
```

### ajouter les permissions du groupe members
```
declined = ['can_edit_posts', 'can_lock_topics', 'can_delete_posts', 'can_move_topics', 'can_approve_posts', 'can_reply_to_locked_topics', 'can_vote_in_polls', 'can_create_polls', 'can_post_stickies', 'can_post_announcements']
GroupForumPermission.objects.bulk_create(
    [GroupForumPermission(group=members,permission=permission,has_perm=False,forum=forum) for permission in ForumPermission.objects.filter(codename__in=declined)
    ]
)
GroupForumPermission.objects.bulk_create(
    [GroupForumPermission(group=members,permission=permission,has_perm=True,forum=forum) for permission in ForumPermission.objects.exclude(codename__in=declined)
    ]
)
```
