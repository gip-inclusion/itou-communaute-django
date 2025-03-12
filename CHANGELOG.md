# Journal des modifications

## [2.22.0](https://github.com/gip-inclusion/itou-communaute-django/compare/v2.21.0...v2.22.0) (2025-03-12)


### Features

* anonymisation des données 30j après la notification ([#916](https://github.com/gip-inclusion/itou-communaute-django/issues/916)) ([7ecd326](https://github.com/gip-inclusion/itou-communaute-django/commit/7ecd326c4fbe84e5d455fb172dd25e8c67ab9e85))
* envoi des messages pour les utilisateurs non vus depuis plus de 23 mois ([#912](https://github.com/gip-inclusion/itou-communaute-django/issues/912)) ([00acb65](https://github.com/gip-inclusion/itou-communaute-django/commit/00acb65ca2630f05e945978e52de86273f624231))
* extension des droits des utilisateurs de l'équipe - edition, deplacement et verrouillage des sujets ([#917](https://github.com/gip-inclusion/itou-communaute-django/issues/917)) ([7ef0c62](https://github.com/gip-inclusion/itou-communaute-django/commit/7ef0c627d3ae6f87fc5e5505e177d95340f33640))
* faciliter la moderation des `Post` pour les utilisateurs `staff` ([#928](https://github.com/gip-inclusion/itou-communaute-django/issues/928)) ([bcc3563](https://github.com/gip-inclusion/itou-communaute-django/commit/bcc35639b0429530f02b44364ee75ec7bcb29ce9))
* modifier la catégorie d'une fiche pratique par les utilisateurs `staff` ([#925](https://github.com/gip-inclusion/itou-communaute-django/issues/925)) ([457f914](https://github.com/gip-inclusion/itou-communaute-django/commit/457f914234da392ea7876b350f8be2efe8be181c))
* reactivation de la collecte des stats ([#930](https://github.com/gip-inclusion/itou-communaute-django/issues/930)) ([48b5cec](https://github.com/gip-inclusion/itou-communaute-django/commit/48b5cec5cdf2f9184c34ac9b467f495cc414044c))


### Bug Fixes

* desactivation de la collecte automatique des statistiques depuis matomo ([#919](https://github.com/gip-inclusion/itou-communaute-django/issues/919)) ([ed2fb75](https://github.com/gip-inclusion/itou-communaute-django/commit/ed2fb75c146a735d56abe95fe0a1d0fbee41dba4))
* encodage de la description des fiches pratiques sur la homepage ([#926](https://github.com/gip-inclusion/itou-communaute-django/issues/926)) ([5c94684](https://github.com/gip-inclusion/itou-communaute-django/commit/5c94684fd0b8de917f19c6cd5dfcd7c898682149))
* mise à jour de la date d'envoi de la notification "vous-nous-manquez" ([#922](https://github.com/gip-inclusion/itou-communaute-django/issues/922)) ([50d7200](https://github.com/gip-inclusion/itou-communaute-django/commit/50d72001b94a2c13d1cd16cff2dfd0f680c3f3d1))
* mise en pause des notifications "vous nous manquez" ([#920](https://github.com/gip-inclusion/itou-communaute-django/issues/920)) ([30941a3](https://github.com/gip-inclusion/itou-communaute-django/commit/30941a391478efcee2fb26b91f512ce2ee8b354a))

## [2.21.0](https://github.com/gip-inclusion/itou-communaute-django/compare/v2.20.0...v2.21.0) (2025-02-13)


### Features

* creation de la table de suivi RGPD ([#892](https://github.com/gip-inclusion/itou-communaute-django/issues/892)) ([dfc378a](https://github.com/gip-inclusion/itou-communaute-django/commit/dfc378aabedc284b79e4167004cb0edef37afdfa))
* enregistrer le dernier evenement connu pour une adresse mail ([#894](https://github.com/gip-inclusion/itou-communaute-django/issues/894)) ([9aa316c](https://github.com/gip-inclusion/itou-communaute-django/commit/9aa316c456567066d575699900a8406607bb1a99))
* extension des droits des utilisateurs de l'équipe - Documentation et Partenaires ([#914](https://github.com/gip-inclusion/itou-communaute-django/issues/914)) ([95bea05](https://github.com/gip-inclusion/itou-communaute-django/commit/95bea05477d311f9860c7f93f7c6acfc09c8688b))
* extension des droits des utilisateurs de l'équipe ([#913](https://github.com/gip-inclusion/itou-communaute-django/issues/913)) ([d5add12](https://github.com/gip-inclusion/itou-communaute-django/commit/d5add12f5a254ca898c14aeedf92a989fcfbec56))
* hydrater la table du dernier évènement connu pour un email à partir des évènements passés ([#896](https://github.com/gip-inclusion/itou-communaute-django/issues/896)) ([28c4cb2](https://github.com/gip-inclusion/itou-communaute-django/commit/28c4cb2f770a1c50ed842084b3ff41606a79aa95))
* masquer le filtre sur les reponses certifiees ([a648647](https://github.com/gip-inclusion/itou-communaute-django/commit/a648647ec0e2e35709ac52fe3a405b12d5f12a51))
* masquer le filtre sur les reponses certifiees ([#908](https://github.com/gip-inclusion/itou-communaute-django/issues/908)) ([84e9a42](https://github.com/gip-inclusion/itou-communaute-django/commit/84e9a424bcc5f7a167e898103ba3d28f9505c078))
* **notification:** enregistrer les retours sur les notifs mails ([#891](https://github.com/gip-inclusion/itou-communaute-django/issues/891)) ([ec67205](https://github.com/gip-inclusion/itou-communaute-django/commit/ec672052e0aec008ca3edee65942aaf3d62d2555))
* remplacer un nom de domaine expiré dans les données utilisateurs ([#907](https://github.com/gip-inclusion/itou-communaute-django/issues/907)) ([fb886e1](https://github.com/gip-inclusion/itou-communaute-django/commit/fb886e1465ce9c7b70131a38b9008c40f77d37b9))
* **search:** ajout de liens de recherche vers le site des emplois ([#879](https://github.com/gip-inclusion/itou-communaute-django/issues/879)) ([c6ac2a3](https://github.com/gip-inclusion/itou-communaute-django/commit/c6ac2a370288d9f19a04ae809167c84ea9c162e5))
* supprimer les traces d'envoi d'emails de plus de 90 jours ([#902](https://github.com/gip-inclusion/itou-communaute-django/issues/902)) ([8abf9ef](https://github.com/gip-inclusion/itou-communaute-django/commit/8abf9ef9e44755394c9a82a9d0c3a1e8f0c7434c))


### Bug Fixes

* suppression de type dans `EmailLastSeen` ([#905](https://github.com/gip-inclusion/itou-communaute-django/issues/905)) ([a21b502](https://github.com/gip-inclusion/itou-communaute-django/commit/a21b502169bb6e7222570f946cdb4c98b8d8102d))
* televersement des fichiers en erreur ([#899](https://github.com/gip-inclusion/itou-communaute-django/issues/899)) ([d9951e1](https://github.com/gip-inclusion/itou-communaute-django/commit/d9951e1d1b0b3abb432607c593c95447bf03fa4c))

## [2.20.0](https://github.com/gip-inclusion/itou-communaute-django/compare/v2.19.0...v2.20.0) (2025-01-13)


### Features

* mise en place du nom de domaine communaute.inclusion.gouv.fr ([#876](https://github.com/gip-inclusion/itou-communaute-django/issues/876)) ([6cc5958](https://github.com/gip-inclusion/itou-communaute-django/commit/6cc59587241fa03fff2626dc9ee39c5a028ec64a))
* **stats:** reactivation de la collecte automatique des stats ([#871](https://github.com/gip-inclusion/itou-communaute-django/issues/871)) ([65dc548](https://github.com/gip-inclusion/itou-communaute-django/commit/65dc548097b94e19435d811b27ff542362c21ff3))


### Bug Fixes

* 🦇 désactiver la suppression en masse des `Post` depuis l'admin django ([#861](https://github.com/gip-inclusion/itou-communaute-django/issues/861)) ([e094434](https://github.com/gip-inclusion/itou-communaute-django/commit/e094434de685e0fc6e59a81aef6b54110cdd1cbd))

## [2.19.0](https://github.com/gip-inclusion/itou-communaute-django/compare/v2.18.0...v2.19.0) (2024-12-16)


### Features

* amélioration bouton pro_connect ([#847](https://github.com/gip-inclusion/itou-communaute-django/issues/847)) ([09397af](https://github.com/gip-inclusion/itou-communaute-django/commit/09397afbb5064420bc67ac5f403b3619e73ee752))
* harmonisation des liens de connexion ([#844](https://github.com/gip-inclusion/itou-communaute-django/issues/844)) ([fb50472](https://github.com/gip-inclusion/itou-communaute-django/commit/fb504725a2136baeae01b704f3490c777c76b4c3))
* **home:** afficher les questions en attente de réponse sur la page d'accueil ([#830](https://github.com/gip-inclusion/itou-communaute-django/issues/830)) ([300a7bd](https://github.com/gip-inclusion/itou-communaute-django/commit/300a7bd6fc288c13e293eddba562489c2e8c6ce7))
* mise à jour de la politique de confidentialité ([#845](https://github.com/gip-inclusion/itou-communaute-django/issues/845)) ([fa5d0d4](https://github.com/gip-inclusion/itou-communaute-django/commit/fa5d0d4a63fc41a758013369f1e411a1c9a1818a))
* **notification:** informer les abonnés des nouvelles questions dans un forum ([#835](https://github.com/gip-inclusion/itou-communaute-django/issues/835)) ([432fec2](https://github.com/gip-inclusion/itou-communaute-django/commit/432fec2a4ed49855c89f1c9af08ca65798f8e236))
* POC, autoconnection les emplois vers la commu via Pro Connect ([#851](https://github.com/gip-inclusion/itou-communaute-django/issues/851)) ([56e3163](https://github.com/gip-inclusion/itou-communaute-django/commit/56e31638f024664cb568ae9fdf6e3825bd2f5599))
* renommage des upvotes ([#842](https://github.com/gip-inclusion/itou-communaute-django/issues/842)) ([4491d8d](https://github.com/gip-inclusion/itou-communaute-django/commit/4491d8d61ff41670b8e7887c53b5ed325604746a))


### Bug Fixes

* hydratation du parametre `next` dans l'url proconnect:authorize ([#850](https://github.com/gip-inclusion/itou-communaute-django/issues/850)) ([3486f6e](https://github.com/gip-inclusion/itou-communaute-django/commit/3486f6e55fabc4248cbf559eb87e80173535f457))
* **stats:** desactivation de la collecte des stats automatique ([#859](https://github.com/gip-inclusion/itou-communaute-django/issues/859)) ([5bf3aea](https://github.com/gip-inclusion/itou-communaute-django/commit/5bf3aea0c50d50d9e8300d08e0e0e4b691f2a3bf))

## [2.18.0](https://github.com/gip-inclusion/itou-communaute-django/compare/v2.17.0...v2.18.0) (2024-12-02)


### Features

* mise à jour de la politique de confidentialité ([#824](https://github.com/gip-inclusion/itou-communaute-django/issues/824)) ([6cfed1a](https://github.com/gip-inclusion/itou-communaute-django/commit/6cfed1af26b5d5a9a9b7fb4f5e5a5855b9c985dc))
* mise à jour UI des ecrans de connexion ([#825](https://github.com/gip-inclusion/itou-communaute-django/issues/825)) ([8f1e4f8](https://github.com/gip-inclusion/itou-communaute-django/commit/8f1e4f82bc31527e2be8bfb94c4b5d4c2c1c0f36))
* simplifier la collecte des destinataires des questions en attente ([#833](https://github.com/gip-inclusion/itou-communaute-django/issues/833)) ([22eb8ca](https://github.com/gip-inclusion/itou-communaute-django/commit/22eb8caf6694b385cec5161683b2cf218681e524))
* **stats:** suppression de la page cachée ([#828](https://github.com/gip-inclusion/itou-communaute-django/issues/828)) ([92bf7d8](https://github.com/gip-inclusion/itou-communaute-django/commit/92bf7d8ecad6e275137ed5d1bac7a8af2e870594))


### Bug Fixes

* anonymiser les urls de profil des utilisateurs ([#832](https://github.com/gip-inclusion/itou-communaute-django/issues/832)) ([6f03e8f](https://github.com/gip-inclusion/itou-communaute-django/commit/6f03e8f663f9a79fbac8a0858bb0ed0f6ddc0e01))
* **log:** patch [#810](https://github.com/gip-inclusion/itou-communaute-django/issues/810) ([#822](https://github.com/gip-inclusion/itou-communaute-django/issues/822)) ([436c6a4](https://github.com/gip-inclusion/itou-communaute-django/commit/436c6a4b633120cb43fc2094f384caa4edb59e7b))
* retarder la collecte des statistiques matomo ([#826](https://github.com/gip-inclusion/itou-communaute-django/issues/826)) ([dfca7e8](https://github.com/gip-inclusion/itou-communaute-django/commit/dfca7e850e242652179e84f84fdbace2fcb7d4fc))
* **stats:** ajout des liens vers les forums dans la page de statistique des fiches pratiques ([#827](https://github.com/gip-inclusion/itou-communaute-django/issues/827)) ([63e2220](https://github.com/gip-inclusion/itou-communaute-django/commit/63e2220d0374eed6c1d6d515c51cc3293ee7f83e))

## [2.17.0](https://github.com/gip-inclusion/itou-communaute-django/compare/v2.16.0...v2.17.0) (2024-11-14)


### Features

* ajout d'une balise youtube dans le markdown ([#810](https://github.com/gip-inclusion/itou-communaute-django/issues/810)) ([adbff17](https://github.com/gip-inclusion/itou-communaute-django/commit/adbff17e176a1c750d3ac354a8f9f94c129a7ebc))
* **forum_conversation:** suppression du triage avant de pouvoir poser une question ([#818](https://github.com/gip-inclusion/itou-communaute-django/issues/818)) ([f1b64c6](https://github.com/gip-inclusion/itou-communaute-django/commit/f1b64c695c62de0cfd150868f4eee09dc061ae8a))
* **stats:** ajout de la colonne categorie dans les stats des fiches pratiques ([#812](https://github.com/gip-inclusion/itou-communaute-django/issues/812)) ([c072b5f](https://github.com/gip-inclusion/itou-communaute-django/commit/c072b5fe831ed4634b1ee350c8d75d717244a482))
* **user:** authentification via un lien magique envoyé par email ([#804](https://github.com/gip-inclusion/itou-communaute-django/issues/804)) ([64e04a3](https://github.com/gip-inclusion/itou-communaute-django/commit/64e04a3486a3b31a2885090e2120c2a9f3e128a1))
* **user:** basculer l'authentification vers ProConnect ([#731](https://github.com/gip-inclusion/itou-communaute-django/issues/731)) ([5429fce](https://github.com/gip-inclusion/itou-communaute-django/commit/5429fce488095dda582d954427285a6f11850991))


### Bug Fixes

* **attachment:** affichage des liens vers les fichiers des messages ([#806](https://github.com/gip-inclusion/itou-communaute-django/issues/806)) ([7c34605](https://github.com/gip-inclusion/itou-communaute-django/commit/7c3460554f799af337c3d25ad76e9d403366a55c))
* **metabase:** deplanification d'une tâche résiduelle ([#808](https://github.com/gip-inclusion/itou-communaute-django/issues/808)) ([692a274](https://github.com/gip-inclusion/itou-communaute-django/commit/692a274e9968539ed3d791d18ca4f53949245556))

## [2.16.0](https://github.com/gip-inclusion/itou-communaute-django/compare/v2.15.0...v2.16.0) (2024-10-09)


### Features

* **stats:** page de statistique des fiches pratiques ([#796](https://github.com/gip-inclusion/itou-communaute-django/issues/796)) ([41237f1](https://github.com/gip-inclusion/itou-communaute-django/commit/41237f191db3229ad01f10dd858558f0a7615647))
* suppression du sondage pour mieux connaitre les utilisateurs de la communauté ([#797](https://github.com/gip-inclusion/itou-communaute-django/issues/797)) ([c830f0a](https://github.com/gip-inclusion/itou-communaute-django/commit/c830f0aeccc6b65eb863ea0997232824e6c94933))


### Bug Fixes

* filtrage des questions en utilisant les étiquettes ([#794](https://github.com/gip-inclusion/itou-communaute-django/issues/794)) ([d03847e](https://github.com/gip-inclusion/itou-communaute-django/commit/d03847e77ac9312aea66f64b850218f69f028f10))
* filtrage des questions en utilisant les étiquettes (part 2) ([#799](https://github.com/gip-inclusion/itou-communaute-django/issues/799)) ([660df15](https://github.com/gip-inclusion/itou-communaute-django/commit/660df155b49626f88e69d71ee9298942b136b7db))

## [2.15.0](https://github.com/gip-inclusion/itou-communaute-django/compare/v2.14.0...v2.15.0) (2024-10-07)


### Features

* ajout d'un sondage pour mieux connaitre les utilisateurs de la communauté ([#781](https://github.com/gip-inclusion/itou-communaute-django/issues/781)) ([171bdde](https://github.com/gip-inclusion/itou-communaute-django/commit/171bddea8cef354c539eb014c30ebb1c3aa8040c))
* page parking ([#788](https://github.com/gip-inclusion/itou-communaute-django/issues/788)) ([732bd5c](https://github.com/gip-inclusion/itou-communaute-django/commit/732bd5c214b27cdb20e4560a24e74398291fe116))
* **partner:** ajout des pages de creation / mise à jour depuis la page "nos partenaires" ([#780](https://github.com/gip-inclusion/itou-communaute-django/issues/780)) ([4001074](https://github.com/gip-inclusion/itou-communaute-django/commit/40010747aa85d87ee8c02d35d2c4af6c1f818bb1))

## [2.14.0](https://github.com/gip-inclusion/itou-communaute-django/compare/v2.13.0...v2.14.0) (2024-09-23)


### Features

* **forum:** retrait de la notion de `kind` sur `Forum` ([#769](https://github.com/gip-inclusion/itou-communaute-django/issues/769)) ([e0daecb](https://github.com/gip-inclusion/itou-communaute-django/commit/e0daecbe728c54af2f604b9adce79c302266a563))
* refonte homepage pour mise en valeur recherche et Call To Actions ([#776](https://github.com/gip-inclusion/itou-communaute-django/issues/776)) ([4550cf9](https://github.com/gip-inclusion/itou-communaute-django/commit/4550cf9d289aaae11cd094a68bd4257f3337ad00))
* **stats:** ajout d'un lien vers la page de stats hebdos ([#774](https://github.com/gip-inclusion/itou-communaute-django/issues/774)) ([028814a](https://github.com/gip-inclusion/itou-communaute-django/commit/028814aedf54bd6ab093b64040da5c79df77bef7))


### Bug Fixes

* mise à jour des urls de statistiques ([#772](https://github.com/gip-inclusion/itou-communaute-django/issues/772)) ([6cd6ec3](https://github.com/gip-inclusion/itou-communaute-django/commit/6cd6ec3c72120882843c80580bf3ed17b8bec6ea))

## [2.13.0](https://github.com/gip-inclusion/itou-communaute-django/compare/v2.12.0...v2.13.0) (2024-09-05)


### Features

* **event:** amélioration de l'admin ([#753](https://github.com/gip-inclusion/itou-communaute-django/issues/753)) ([ca56d83](https://github.com/gip-inclusion/itou-communaute-django/commit/ca56d83be47fcf8c628c19fd141ecf73a4adeadc))
* **forum:** retrait des communautés privées ([#768](https://github.com/gip-inclusion/itou-communaute-django/issues/768)) ([1c120e3](https://github.com/gip-inclusion/itou-communaute-django/commit/1c120e3b4b4dfe0323c52aae39bc5f2931157f98))
* **partner:** ajout des pages partenaires ([#757](https://github.com/gip-inclusion/itou-communaute-django/issues/757)) ([33fd1c6](https://github.com/gip-inclusion/itou-communaute-django/commit/33fd1c6dc578c5b781571385b72c6b6a7b9d1329))
* **partner:** améliorations post déploiement ([#763](https://github.com/gip-inclusion/itou-communaute-django/issues/763)) ([09a865f](https://github.com/gip-inclusion/itou-communaute-django/commit/09a865faebb2d38817a9c46db717ba4c8588aafc))
* **partner:** lien avec les fiches pratiques ([#761](https://github.com/gip-inclusion/itou-communaute-django/issues/761)) ([60bb2ee](https://github.com/gip-inclusion/itou-communaute-django/commit/60bb2eeacd0f13de209ff6fe34a58b1a9979969d))
* **partner:** referencer les fiches partenaires dans sitemap.xml ([#759](https://github.com/gip-inclusion/itou-communaute-django/issues/759)) ([91bea96](https://github.com/gip-inclusion/itou-communaute-django/commit/91bea9659ffe94a265b74ed62786a214047f6e03))
* **tags:** afficher les filtres sur les tags ([#752](https://github.com/gip-inclusion/itou-communaute-django/issues/752)) ([7a10488](https://github.com/gip-inclusion/itou-communaute-django/commit/7a10488313296da6b3748539a2fde4587eec979c))
* **tags:** afficher les Tags dans la liste des fiches pratiques d'une categorie ([#751](https://github.com/gip-inclusion/itou-communaute-django/issues/751)) ([ed005b7](https://github.com/gip-inclusion/itou-communaute-django/commit/ed005b7fab89810255f793f627b39442ce77b119))
* **tags:** ajouter des étiquettes à un forum ([#746](https://github.com/gip-inclusion/itou-communaute-django/issues/746)) ([7f435bb](https://github.com/gip-inclusion/itou-communaute-django/commit/7f435bb71c8ac56eff38798c0d26deca4a99f607))
* **tags:** ajouter une étiquette inexistante à un sujet ([#744](https://github.com/gip-inclusion/itou-communaute-django/issues/744)) ([b82ea73](https://github.com/gip-inclusion/itou-communaute-django/commit/b82ea73bac3523ec615ebef5e97970bf4f81ae02))
* **tags:** filtrer les `forum` enfants à partir des tags ([#750](https://github.com/gip-inclusion/itou-communaute-django/issues/750)) ([eb6683a](https://github.com/gip-inclusion/itou-communaute-django/commit/eb6683a9b12751fbc522d06bfab45ef7a10b4b90))


### Bug Fixes

* **forum_conversation:** Résolution des erreurs de tests sur les contenus des messages ([#754](https://github.com/gip-inclusion/itou-communaute-django/issues/754)) ([8e0f35d](https://github.com/gip-inclusion/itou-communaute-django/commit/8e0f35de60f908cb07cb63698aac036800765dd4))
* **partner:** mise en forme des logos de la vue en liste ([#764](https://github.com/gip-inclusion/itou-communaute-django/issues/764)) ([7a84319](https://github.com/gip-inclusion/itou-communaute-django/commit/7a843198c6c2d6ea73448c75428d18cbbb6751b2))
* **post:** simplification du sujet des `Post` ([#748](https://github.com/gip-inclusion/itou-communaute-django/issues/748)) ([3c2a5a0](https://github.com/gip-inclusion/itou-communaute-django/commit/3c2a5a0aecedc0cf6ce113f675fea0b5a7d57d05))

## [2.12.0](https://github.com/gip-inclusion/itou-communaute-django/compare/v2.11.0...v2.12.0) (2024-08-07)


### Features

* **documentation:** rendre la certification optionnelle ([#741](https://github.com/gip-inclusion/itou-communaute-django/issues/741)) ([6141112](https://github.com/gip-inclusion/itou-communaute-django/commit/61411127ba4c2bf76dccf825f7ed468260cd5fc4))
* **footer:** mise à jour des liens sociaux ([#730](https://github.com/gip-inclusion/itou-communaute-django/issues/730)) ([f19602e](https://github.com/gip-inclusion/itou-communaute-django/commit/f19602e425fd9938f11e6ac43d8aaa440557548e))
* **forum:** attr accept définit sur forms.ImageField ([#734](https://github.com/gip-inclusion/itou-communaute-django/issues/734)) ([0e8b8c9](https://github.com/gip-inclusion/itou-communaute-django/commit/0e8b8c926367d763ab74208485deb68940993f33))
* **forum:** fin de l'AB test sur la notation des forums ([#708](https://github.com/gip-inclusion/itou-communaute-django/issues/708)) ([6705ead](https://github.com/gip-inclusion/itou-communaute-django/commit/6705eada794a8aedcdb8baf1bbacfca595427edc))
* **forum:** utiliser l'image du forum dans la vignette opengraph ([#725](https://github.com/gip-inclusion/itou-communaute-django/issues/725)) ([cc137c1](https://github.com/gip-inclusion/itou-communaute-django/commit/cc137c1ce0f141189a2ebd85a6f5bf13199112da))
* mise à jour entête, pied de page et menu ([#739](https://github.com/gip-inclusion/itou-communaute-django/issues/739)) ([4493267](https://github.com/gip-inclusion/itou-communaute-django/commit/4493267ec9f3919acb91c31db18f78c7c4ac074f))
* **notification:** passage des notifications en lues ([#712](https://github.com/gip-inclusion/itou-communaute-django/issues/712)) ([a1a6b73](https://github.com/gip-inclusion/itou-communaute-django/commit/a1a6b73a5e992806663f850a2aa835bf7c95c0aa))
* **seo:** mise à jour de l'image OpenGraph ([#720](https://github.com/gip-inclusion/itou-communaute-django/issues/720)) ([f37521c](https://github.com/gip-inclusion/itou-communaute-django/commit/f37521c27ccffccee9ebe86d5b654f95b38f45c8))


### Bug Fixes

* **forum:** balise `article` et dimension des images ([#737](https://github.com/gip-inclusion/itou-communaute-django/issues/737)) ([b1ed91f](https://github.com/gip-inclusion/itou-communaute-django/commit/b1ed91f00ca5a09e529ccb40f4d023f5e197fff0))
* mise à jour de la public key sentry pour l'envoi des logs ([#732](https://github.com/gip-inclusion/itou-communaute-django/issues/732)) ([616c0aa](https://github.com/gip-inclusion/itou-communaute-django/commit/616c0aa41422077a22486c33731f2b750ebe9694))
* **upvotes:** largeur du bouton s'abonner dynamique ([#743](https://github.com/gip-inclusion/itou-communaute-django/issues/743)) ([32cb339](https://github.com/gip-inclusion/itou-communaute-django/commit/32cb339bf5c93b549628f3d485f8830f1fa81b51))
* **upvote:** supprimer un parametrage ambigue ([#742](https://github.com/gip-inclusion/itou-communaute-django/issues/742)) ([168df13](https://github.com/gip-inclusion/itou-communaute-django/commit/168df1352f32090509133173fee3bcafe7a608db))

## [2.11.0](https://github.com/gip-inclusion/itou-communaute-django/compare/v2.10.0...v2.11.0) (2024-07-03)


### Features

* **admin:** améliorer le filtrage des stats de forum ([#699](https://github.com/gip-inclusion/itou-communaute-django/issues/699)) ([cd0d301](https://github.com/gip-inclusion/itou-communaute-django/commit/cd0d301d4b48492eddcbd790411abfd4dcdb6329))
* **admin:** filtrage des stats de forum, ajout tri ([#701](https://github.com/gip-inclusion/itou-communaute-django/issues/701)) ([1da74df](https://github.com/gip-inclusion/itou-communaute-django/commit/1da74df303eea1dd1ebbadab91ff410f86eaa6b3))
* **forum_conversation:** filtrer les questions dans l'espace d'echanges - stats de suivi ([#700](https://github.com/gip-inclusion/itou-communaute-django/issues/700)) ([bac6e55](https://github.com/gip-inclusion/itou-communaute-django/commit/bac6e5576e9455bc49415139317de302dbf10e1f))
* **forum_conversation:** filtrer les questions dans l'espace d'échanges ([#681](https://github.com/gip-inclusion/itou-communaute-django/issues/681)) ([48cdd07](https://github.com/gip-inclusion/itou-communaute-django/commit/48cdd078c03bd0b7b1a2a5c002517ffada06dbbb))
* **forum:** Activation de l'AB Test Notation des forums ([#686](https://github.com/gip-inclusion/itou-communaute-django/issues/686)) ([c5699d4](https://github.com/gip-inclusion/itou-communaute-django/commit/c5699d4af4594207e01b39d0c1c8729da3ad052d))
* **forum:** collecter les notations des fiches pratiques ([#677](https://github.com/gip-inclusion/itou-communaute-django/issues/677)) ([4c39290](https://github.com/gip-inclusion/itou-communaute-django/commit/4c392904873ca7f6ef8c98ee0f389ad438516add))
* **home:** MVP zone editoriale sur la page d'accueil ([#703](https://github.com/gip-inclusion/itou-communaute-django/issues/703)) ([5e3f759](https://github.com/gip-inclusion/itou-communaute-django/commit/5e3f75913eb7b1cf2eb57d0b27a4412695bf6604))
* **home:** petites améliorations ([#689](https://github.com/gip-inclusion/itou-communaute-django/issues/689)) ([7471451](https://github.com/gip-inclusion/itou-communaute-django/commit/7471451b5e9de2bc0ca4884a62dcab94cf5f921a))
* **notification:** nouveau système des notifications messages ([#697](https://github.com/gip-inclusion/itou-communaute-django/issues/697)) ([f2eedd4](https://github.com/gip-inclusion/itou-communaute-django/commit/f2eedd4debc383fe857330db9827ed04d694f8a1))
* **stats:** collecter les stats d'activité hebdo des forums de la documentation ([#691](https://github.com/gip-inclusion/itou-communaute-django/issues/691)) ([ab513a8](https://github.com/gip-inclusion/itou-communaute-django/commit/ab513a8398a8cfa4df899e45de1945326372d0bd))
* **stats:** page hebdo partenaires fiches pratiques ([#695](https://github.com/gip-inclusion/itou-communaute-django/issues/695)) ([f7f26b8](https://github.com/gip-inclusion/itou-communaute-django/commit/f7f26b8816486f426899b52ebd0a54bda85a8c28))


### Bug Fixes

* **cron.json:** erreur copier-coller sur send_notifications_daily.sh ([#705](https://github.com/gip-inclusion/itou-communaute-django/issues/705)) ([32f59ed](https://github.com/gip-inclusion/itou-communaute-django/commit/32f59ed0a71a217393aded9febbea04f1d59e5ee))
* **forum:** ab test forum rating ([#687](https://github.com/gip-inclusion/itou-communaute-django/issues/687)) ([f0e9c2b](https://github.com/gip-inclusion/itou-communaute-django/commit/f0e9c2b4bf2145e438d94fea8db6f86073250541))
* **forum:** ab test forum rating ([#688](https://github.com/gip-inclusion/itou-communaute-django/issues/688)) ([d3027e4](https://github.com/gip-inclusion/itou-communaute-django/commit/d3027e41315afd0a7f912a4c323fca5da7e4d5b6))
* **notification:** mettre à jour le sent_at pour éviter les notifications duplicates ([#707](https://github.com/gip-inclusion/itou-communaute-django/issues/707)) ([fca7f29](https://github.com/gip-inclusion/itou-communaute-django/commit/fca7f2911e37ec05f89035ca007dc51e211d2a84))
* **stats:** derniere date collectée des stats matomo ([#684](https://github.com/gip-inclusion/itou-communaute-django/issues/684)) ([015e08b](https://github.com/gip-inclusion/itou-communaute-django/commit/015e08b9fc4fbc3f8f8e286f7c344746f13a3d4e))
* **stats:** gel du temps dans les tests de la vue `StatistiquesPageView` ([#702](https://github.com/gip-inclusion/itou-communaute-django/issues/702)) ([df66524](https://github.com/gip-inclusion/itou-communaute-django/commit/df66524a7477ec59838a80b9bfbca745fdb6db84))

## [2.10.0](https://github.com/gip-inclusion/itou-communaute-django/compare/v2.9.2...v2.10.0) (2024-06-13)


### Features

* **admin:** ajoute PostInline à TopicAdmin ([#657](https://github.com/gip-inclusion/itou-communaute-django/issues/657)) ([6f3049a](https://github.com/gip-inclusion/itou-communaute-django/commit/6f3049a3154e0076fc6f563e03639b3c25a3352a))
* ajout du chemin de fer dans l'espace d'échanges et la documentation ([#649](https://github.com/gip-inclusion/itou-communaute-django/issues/649)) ([7cc5d14](https://github.com/gip-inclusion/itou-communaute-django/commit/7cc5d14dc853e85f00d583fad697cab8acd2b063))
* **forum_conversation/admin:** CertifiedPost verbose_name et traduction ([#666](https://github.com/gip-inclusion/itou-communaute-django/issues/666)) ([e9b0da6](https://github.com/gip-inclusion/itou-communaute-django/commit/e9b0da622ed671f23966b525672c0d4920637ce5))
* **forum_conversation/tests.py:** test explicite pour la seconde page ([#669](https://github.com/gip-inclusion/itou-communaute-django/issues/669)) ([5bea4f1](https://github.com/gip-inclusion/itou-communaute-django/commit/5bea4f1087e87ec3628b75cefd45974dffa8a6d5))
* **forum_conversation:** remettre les annonces dans la liste des messages par défaut ([#662](https://github.com/gip-inclusion/itou-communaute-django/issues/662)) ([bb341cb](https://github.com/gip-inclusion/itou-communaute-django/commit/bb341cbb45bcc43009667cbce24a7d1c80ef2b24))
* **forum_moderation:** enregistrement des messages bloquées ([#659](https://github.com/gip-inclusion/itou-communaute-django/issues/659)) ([7318b5d](https://github.com/gip-inclusion/itou-communaute-django/commit/7318b5d5947fc2920374c58d2c04931324ffe5bf))
* **forum:** harmoniser la liste des topics ([#665](https://github.com/gip-inclusion/itou-communaute-django/issues/665)) ([6f8bf3c](https://github.com/gip-inclusion/itou-communaute-django/commit/6f8bf3c248feecc29c8f8734931afbad207e66e2))
* **stats:** afficher les stats quotidiennes des Diagnostics Parcours IAE ([#660](https://github.com/gip-inclusion/itou-communaute-django/issues/660)) ([5c74c56](https://github.com/gip-inclusion/itou-communaute-django/commit/5c74c5601c134f0f8adaa07c1f758dde3fa1b887))
* **stats:** ajout de la vue historique des visiteurs mensuels ([#656](https://github.com/gip-inclusion/itou-communaute-django/issues/656)) ([804be3c](https://github.com/gip-inclusion/itou-communaute-django/commit/804be3c38b961147f4904b4cbb229a901eaf3379))
* **stats:** collecter le nombre de diag parcours iae réalisés quotidiennement ([#658](https://github.com/gip-inclusion/itou-communaute-django/issues/658)) ([7205a2b](https://github.com/gip-inclusion/itou-communaute-django/commit/7205a2b89b1896280627724e0f9eece5f94c08e1))


### Bug Fixes

* **documentation:** améliorer l'affichage des bannières des fiches pratiques ([#653](https://github.com/gip-inclusion/itou-communaute-django/issues/653)) ([3b539d2](https://github.com/gip-inclusion/itou-communaute-django/commit/3b539d2b660fa58b49235162419ede461d43843f))
* **forum_conversation:** page 1 forcée dans les liens tags ([#668](https://github.com/gip-inclusion/itou-communaute-django/issues/668)) ([a150ab2](https://github.com/gip-inclusion/itou-communaute-django/commit/a150ab2b153bac1830908d03ec0c712db3244c4f))
* **forum_moderation:** motif de blocage illisible dans l'admin ([#672](https://github.com/gip-inclusion/itou-communaute-django/issues/672)) ([5480394](https://github.com/gip-inclusion/itou-communaute-django/commit/5480394f466b458344ea2911273c9a0b595cda6f))
* **quality:** formatage des balises `script` dans le gabarit `base.html` ([#651](https://github.com/gip-inclusion/itou-communaute-django/issues/651)) ([0be3c8b](https://github.com/gip-inclusion/itou-communaute-django/commit/0be3c8b4f5b9126af245a36a53b7bd8cb8479711))
* **stats:** corrections mineures ([#661](https://github.com/gip-inclusion/itou-communaute-django/issues/661)) ([d3ae4fd](https://github.com/gip-inclusion/itou-communaute-django/commit/d3ae4fd027310d96077809a43957c8a2d7a79eed))

## [2.9.2](https://github.com/gip-inclusion/itou-communaute-django/compare/v2.9.1...v2.9.2) (2024-05-30)


### Bug Fixes

* Diag parcours IAE - masquer la carte des fiches pratiques liées lorsqu'elle est vide ([#650](https://github.com/gip-inclusion/itou-communaute-django/issues/650)) ([d309e47](https://github.com/gip-inclusion/itou-communaute-django/commit/d309e4772e8403110bd815cf0ee52404dfc8b687))
* Mise à jour de l'action `release-please` ([#645](https://github.com/gip-inclusion/itou-communaute-django/issues/645)) ([725fcd6](https://github.com/gip-inclusion/itou-communaute-django/commit/725fcd696016f286d4574d4ba38d22e1b2d2a2cd))
* mise à jour du gabarit de PR ([#647](https://github.com/gip-inclusion/itou-communaute-django/issues/647)) ([fc10c9e](https://github.com/gip-inclusion/itou-communaute-django/commit/fc10c9e9eafb07de6c9d550f99570d046519b0db))

## 2.9.1 (2024-05-29)


### Features

*  chore: Bump @babel/traverse from 7.20.5 to 7.24.5 in /lacommunaute/static/machina ([3c2b35c](https://github.com/gip-inclusion/itou-communaute-django/commit/3c2b35c3327ef84a6844f9d028229c1b54cf5afa))
* chore: initialisation de l'action github release-please (#642) ([b497c13](https://github.com/gip-inclusion/itou-communaute-django/commit/b497c13a25ab3ac0f15d07cc6e45c513788fb940))


## v2.9 - 2024-05-28

- feat(documentation): mise à jour de la bannière d'un forum (#637)
- feat(documentation): formulaire d'évaluation des fiches pratiques (#636)
- feat(documentation): Afficher l'image du forum comme bannière (#632)
- feat(UI): Mise à jour de l'entête (#634)
- feat(UI): Mise a jour du theme et adaptation du DOM du menu #burgerNav (#638)
- feat(tags): rendre les tags clickables (#623)
- feat(tags): inclure la gestion des tags dans le filtrage des sujets (recent, sans reponse, certifié) (#615)
- feat(poster): désambiguer la mention du forum, de celle des tags (#620)
- chore: correction de la configuration docker-compose (#639)
- chore: mise à jour des dépendances (#622 #629 #641)
- chore: ajout de minio comme bucket S3 (dev & test) (#633)
- chore: mise à jour du Readme (#630)

## v2.8 - 2024-05-02

- [DOCUMENTATION] mettre à jour les fiches en ligne (#604)
- [DOCUMENTATION] ajouter des vidéos YT dans les fiches pratiques (#597)
- [DOCUMENTATION] création de la premiere fiche de la catégorie (fix) (#595)
- [DOCUMENTATION] rendre le formulaire de creation des fiches pratiques plus explicite (#594)
- [DOCUMENTATION] creer les catégories et les fiches pratiques sans passer par l'admin (#593)
- [HOMEPAGE] Suppression des élements inutiles (#592)
- [TECH] chore: mise à jour des dépendances (#608)
- [TECH] ci: auto assignation des PR (#607)
- [TECH] ci: PR semantique (#606)
- [TECH] test: chargement des données automatique en environnement de validation (#605)

## v2.7 - 2024-04-08

- [PROFILE] afficher le lien vers le profil linkedin (#582)
- [PROFILE] experimentation mon stage CIP - complements (#568)
- [PROFILE] experimentation mon stage CIP (#567)
- [PROFILE] afficher les contributeurs authentifiés les plus actifs sur les 30 derniers jours (#558)
- [FORUM] suppression des liens d'invitations dans des forums privés (#574)
- [FORUM] remove call for contributors banner (#571)
- [POST] proteger les underscores dans les urls (#581)
- [MODERATION] bloquer les messages de spams (#561)
- [DSP] suggestions de services geolocalisés (#570)
- [DSP] permettre à tous les utilisateurs connectés d'utiliser l'outil (#569)
- [DSP] ajout des articles associés (#564)
- [DSP] typo (#562)
- [DSP] Améliorer l'onboarding (#560)
- [HOMEPAGE] retrait du fil des actualités (#573)
- [HOMEPAGE] afficher les évènements à venir (#566)
- [HOMEPAGE] retire la banniere "les 2 font la paire" (#563)
- [STATS] suppression des utilisateurs actifs quotidiens (#578)
- [METABASE] suppression de l'app  (#580)
- [TECH] Mise à jour des dépendances - avril 2024 (#572 #579)
- [TECH] Corrections mineures : design et test fragile (#565)
- [TECH] Maj du theme itou vers la v1.4.4 (#575)
- [TECH] Remove text/css from stylesheet links and style (#557)

## v2.6 - 2024-02-14

- [MODERATION] remaniement de la gestion des emails et domaines bloqués (#553)
- [MODERATION] desapprobation d'un post avec email dejà bounced (#551)
- [MODERATION] automatiser la detection des scams (#548)
- [MODERATION] ajouter les emails modérés dans les BouncedEmail (+bug fix) (#541)
- [MODERATION] activation de la moderation queue (#540)
- [DOCUMENTATION] ajout de l'appel à contributeurs (#542)
- [HOMEPAGE] fin AB Test, ajout bouton outlined vers la documentation (#539)
- [HOMEPAGE] reactivation du lien vers le calendrier (#537)
- [HOMEPAGE] reactivation de la bannière les 2 font la paires (#536)
- [HOMEPAGE] mettre en avant l'evenement inclusion-demain (#506)
- [HOMEPAGE] AB test fréquentation de la page documentation (#505)
- [HOMEPAGE] AB test fréquentation de la page documentation (#499 & #500)
- [HOMEPAGE] bannière inclusion-demain (#496)
- [HOMEPAGE] isoler la bannière de promotion dans un gabarit spécifique (#495)
- [HOMEPAGE] delai d'affichage popup (#494)
- [HOMEPAGE] afficher les dates/heures de creation sur la page d'accueil (#481 & #484)
- [STATS] afficher l'indicateur d'impact sans limite de durée (#538)
- [STATS] afficher les visiteurs mensuels (#517)
- [STATS] ajout du nombre d'utilisateurs retours dans l'extraction matomo (#483)
- [TOPIC] Correction bug à la màj d’un topic par son auteur anonyme (#552)
- [TOPIC] ajout d'un lien vers le forum (#544)
- [DPS] Recommandations (#512)
- [RECHERCHE] suggerer de poser la question si les résultats ne conviennent pas (#504)
- [PAGES] Mise à jour de la page 404 (#515 & #516)
- [PAGES] suppression de la page contact (#545)
- [TECH] fixes and improvements (#547, #535 à #528, #525 à #518, #514, #510 à #507, #498, #497, #493 à #485, #482, #480, #478, #477)

## v2.5 - 2023-12-19

- [HOME] Ajout de raccourcis (#465)
- [HOME] Mise a jour du contenu de la déclaration d'accessibilité (#466)
- [HOME] Bannière "les 2 font la paires" (#462)
- [CONVERSATION] Correction de la mise en forme des icones et photo thumbnail (#472)
- [DOCUMENTATION] Poser une question en haut de doc (#464)
- [LIKES] Suppression de la fonctionnalité (#475)
- [EVENEMENT] Correction du titre de la page de détail (#468)
- [STATS] Ajout du tag manager matomo (#470)
- [PILOTAGE] Extraction des données Post (part 2) (#471)
- [PILOTAGE] Extraction des données Forum (part 1) (#469)
- [SETTINGS] Update vscode settings (#474)
- [SETTINGS] Update dependencies (#460 & #467 & #473)
- [SETTINGS] Test deploiement automatique après bascule du repo (#463)
- [SETTINGS] Ajout commentaire RCLONE dans le fichier Makefile(#459)

## v2.4 - 2023-10-31
- [NPS] délai avant affichage sur la homepage à 10secondes (#456)
- [NPS] ajout sous les résultats de recherche (#454)
- [FORUM] Espace d'échanges - correction typo (#442)
- [STATS] nommage des formulaires de recherche (#432)
- [SEARCH] limiter l'indexation aux contenus publics (#451)
- [INCLUSION_CONNECT] adapter l'authentification à la nouvelle version d'IC (#447)
- [INCLUSION_CONNECT] mise à jour des urls (#444)
- [EVENEMENT] patch #1 - mois sans evenement (#437)
- [EVENEMENT] restaurer les evenements sans javascript (#433)
- [TECH] montée en version pg 15 (#449)
- [TECH] Mise à jour des dépendances (#441)
- [TECH] fiabilisation d'un test (#436)
- [TECH] qualité - reindexation des gabarits (#434)
- [TECH] adaptation du scripts de rechargement des sauvegardes de DB suite à la mise à jour de itou-backups (#429)
- [CONTENT_SECURITY_POLICIES] - patches (#430, #427, #425, #423)
- README: update (#428)

sans v2.3

## v2.2 - 2023-09-25
- [STATS] un entonnoir adaptatif (#418)
- [CONVERSATION] masquer le bouton "voir les 999 reponses" (fix) (#417)
- [CONVERSATION] gérer les fichiers manquants (#411, #410, #409)
- [SEO] dédoublonner les ID (#408)
- [INCLUSION CONNECT] gérer les redirections après authentification (#413)
- [NOTIFICATION] mise à jour de la planification de `send_notifs_when_following_replies.sh` (#403)
- Nettoyage des dépendances de developpement (#416)
- HTMX - mise à jour - version 1.9.5 (#415)
- mise à jour des dependances (#405)

## v2.1 - 2023-09-08
- [PAGES] mise à jour des pages de mentions  (#397)
- [RECHERCHE] fix - le fichier d'index est absent lors de certains tests (#394)
- [RECHERCHE] barre de recherche dans le header (#391)
- [STATISTIQUES] août 2023 (#390)
- [SEO] ajout de balises nofollow (#387)
- [SEO] suppression de l'aide MD (#385)
- [TOPICS] filtrer les sujets à partir des étiquettes - part 1 (#384)
- [DOCUMENTATION] titre des liens vers les autres fiches du thème (#378)
- [DOCUMENTATION] déposer des images publiques (#388)
- [MODERATION] mise à jour de la vue de suppression d'un `Topic` (#371)
- [NOTIFICATION] correction de l'url d'accès aux questions non répondues dans l'email de notification (#370)
- [SETTINGS] ajout de la compression des données (#380)
- [SETTINGS] peupler les recettes jetables automatiquement (#399)
- [SETTINGS] mise à jour des dépendances (#372)

## v2.0 - 2023-07-26
- [HOME] Rearrangement de la structure de site (V2) (#341)
- [HOME] tri des dernières questions (#353)
- [HOME] tri des actualités (#363)
- [SEARCH] limiter la recherche aux échanges ou aux discussions, au choix (#367)
- [UPVOTE] liste des sauvegardes d'un utilisateur (#365)
- [UPVOTE] sauvegarder un forum (#362)
- [UPVOTE] convertir la clé étrangère Post en clé étrangère générique (#354)
- [UPVOTE] préparation : déplacement du modèle CertifiedPost  (#356)
- [FORUM] mise à jour du lien vers l'aide des emplois (#358)
- [FORUM] partager la documentation sur les réseaux sociaux (#350)
- [NOTIFICATION] filtre sur les questions non répondues (#347)
- [STATS] exporter l'activité du site pour entrainer le modèle de clustering non supervisé (#345)
- [STATS] stats mensuelles Juin 2023 (#343)
- [TECH] gestion des citations dans le markdown (#346)
- [TECH] mise à jour des dépendances (#368)
- [TECH]Mise à jour des Linters et du format d'export des requirements (#342)

## v1.13 - 2023-06-26
- [NOTIFICATION] informer les utilisateurs des nouvelles réponses à leur question (#331)
- [NOTIFICATION] appel à l'api d'onboarding (#322)
- [FORUM_MEMBER] sécuriser l'accès aux profils (#329)
- [FORUM] simplification de la base de code (#327)
- [FORUM] Supprimer la vue ModeratorEngagementView (#314)
- [FORUM] Limiter l'affichage des questions non répondues aux thématiques publiques (#305)
- [SEO] boost (#325 & #324)
- [SEO] - Maj du theme itou vers la v0.7.1 et du footer (#312)
- [SEARCH] rollback - stockage index localement et reconstruction lors du déploiement (#321)
- [SEARCH] correction du endpoint S3 pour le stockage de l'index (#320)
- [SEARCH] stocker l'index du moteur de recherche dans un bucket permanent (#318)
- [SEARCH] moteur de recherche - robustification d'un test (#316)
- [SEARCH] mise en place du moteur d'indexation (#309)
- [FIX] Gestion des versions de fichiers statiques (#315)
- [FIX] date de modification des Forum dans le fichier sitemap (#310)
- [FIX] rendre la factory des évènements résiliente (#307)

## v1.12 - 2023-06-12
- [FIX] : ne pas afficher les forums de type catégorie dans la liste des forums visibles (#302)
- [FIX] stats quotidiennes (#301)
- [FIX] correction de la date dans le test de la liste des evenements (#300)
- [STATS] stats mensuelles Mai 2023 (#299)
- [SEO] Ajout des fichiers Robots.txt et Sitemap.xml (#297)
- [SEO] Fiches Techniques - prototype (#296)
- [HOME] Bannière pour la redirection vers le support des emplois (#294)
- [HOME] Aligner la page d'accueil avec l'audience cible (#291)
- [TOPIC] Liste des Questions/Réponses avec filtres sur la page d'accueil (#289)

## v1.11 - 2023-05-30
- [Page d'accueil] dynamiser le chargement de la liste des communautes (#285)
- [rollback WWW] finalisation (#283)
- [Topic] créer et afficher des "actualités" - améliorations (#281)
- [Page d'accueil] bouton Poser une Question (#276)
- Simplifier le header (#273)
- build(deps): bump requests from 2.30.0 to 2.31.0 (#270)
- [FIX] Correction de l’erreur de pluriel dans le compteur de sujets et de messages (#272)
- [FIX] Ne pas envoyer de notification si aucune question en attente (#265)
- [FIX] Suppression du champ `target_audience` de `Forum` (#263)
- [FIX] Tags : corrections et optimisations (#262)

## v1.10 - 2023-05-15
- [Notification] sujets non réponds, planification quotidienne des experts volontaires (#259)
- [FIX] rétablir le lien d'édition dans la vue de détail d'un sujet (#254)
- [Landing Pages] maj header, footer et ajout d'images statiques (#251)
- [STATS] stats mensuelles avril 2023 (#250)
- [rollback WWW] forum_conversation & forum_poll apps (#247)
- [rollback WWW] forum app (#245)
- [rollback WWW] forum_upvote app (#243)
- [rollback WWW] forum_member app (#241)
- [rollback WWW] inclusion_connect app (#239)
- [rollback WWW] event app (#237)
- [rollback WWW] pages app (#235)

## v1.9 - 2023.05.02
- [FIX] affichage de l'avatar dans la liste des questions en attente (#227)
- [FIX] rendre le markdown et les url cliquables compatibles (#226)
- [TAGS] etape 0 - ajout des Tags sur les Topics (#225)
- Ajout d'un tag matomo sur la liste des questions en attente (#224)
- Liste des dernières réponses certifiées (#223)

## v1.8 - 2023.04.11
- Désambigüer les actions dans matomo lors de la creation d'un sujet (#221)
- [STATS] : calculer le taux de réponses inférieures à 48h sur le mois (#217)
- [STATS] : calculer les délais de réponses sur un mois (#216)
- [STATS] : compter les evenements (#215)
- FIX: ajout du contexte des questions en attente sur la homepage (#214)
- [STATS]Statistiques mensuelles : mars 2023 (#213)
- Notification par email des questions en attentes de réponse (#212)
- [STATS] automatiser la collecte des stats mensuelles (fixes) (#211)
- Afficher les questions en attentes de réponse (#210)
- [STATS] automatiser la collecte des stats mensuelles (#209)
- [STATS] Mise à jour des statistiques quotidiennes (#208)
- Ajout du lien "voir plus" sur les réponses certifiées (#207)

## v1.7 - 2023.03.27
- Mise à jour de l'affichage du nom de l'auteur d'un post (#203)
- FIX : Ne pas ajouter un poster non authentifié à la liste des likers d'un Sujet (#202)
- Gérer les landing pages sur le site (#201)
- Ajouter l'auteur d'un sujet dans la liste des "likers" du sujet (#200)
- Notification : ajout *par lot* des nouveaux utilisateurs dans la sequence d'onboarding  (#199)
- Gérer la redirection lors de l'authentification pour créer un nouvel évènement (#198)
- Afficher le bouton d'ajout d'évènement pour tous les visiteurs (#197)
- Evaluer la performance des notification de première réponse (#196)
- Notification : ajout des nouveaux utilisateurs dans la sequence d'onboarding (#195)
- Notification : rationnalisation du code (#194)

## v1.6 - 2023.03.20
- Mise à jour des dépendances (#192)
- CRON : automatisation des notifications sur la première reponse (#191)
- Mise à jour de la configuration des recettes jetables (#190)
- Abonnement - suppression du code mort (#189)
- CRON : mise en place de la collecte automatique des stats quotidiennes matomo (#188)
- Maj du theme itou vers la v0.6.1 (#187)
- Certifier une réponse (#186)
- Montrer le popup Tally maximum une fois toutes les deux semaines (#185)
- Automatisation de la collecte des stats quotidiennes (#184)
- Rendre le groupe des membres d'un `forum` optionnel  (#183)
- Nettoyage des Formulaires de creation/mise à jour des Topic & Post (#182)
- Renommages des Likes et des UpVotes (#180)
- Mise en place des notifications par email lors de la première réponse à un sujet (#178)
- Stats : mise à jour de février 2023 (#177)
- update dependencies (#176)
- Mise à jour des règles d'affichage du formulaire de NPS (#175)
- Suppression de la page "funnel" par `forum` (#174)
- Filtrer les questions sans réponses (#173)
- Correction de l'affichage du nombre de sujets et de réponses (#172)
- Enregistrer les stats Matomo en base de données (#171)
- Mise à jour de sécurité (#170)
- Remplacement de l'attibut title sur balises de liens  (#167)
- Page de création de nouvelles communautés publiques avec les bonnes permissions (#166)
- Authentification Inclusion Connect multi-domain (#165)
- Admin - gestion des groupes (#164)
- Compter les Sujets et les Réponses sans limite de profondeur dans les sous communautés (#163)
- Afficher les likes pour les annonces dans le fil d'actualités d'une communauté (#162)

## v1.5 - 2023.02.08
- Page contact - Ajout d'un formulaire Tally de Contact (#160)
- Page 404 suite au changement de nom de domaine (#159)
- Mise en place de l'app Redirection (#158)
- Mise à jour de la page Statistiques avec les données matomo (#156)
- Ajustement des espacements entre le titre, la description et le bouton "voir les sous-commnautés" (#155)
- Mise à jour de sécurité (#154)
- Mise à jour du theme itou vers la v0.5.8 (#153)
- Mise à jour des dépendances et la configuration de pre-commit (#152)
- Mise à jour du bouton de connection (#151)
- Ajout du calendrier des évènements (#150)

## v1.4 - 2023.01.30
- Mise à jour des dépendances (#149)
- Désactivation du bouton “Répondre” dans le fil des `topics` quand le formulaire est ouvert (#148)
- Optimisation des requêtes de la vue d'un `Forum` (fil d'actualités d'une communauté) (#147)
- Afficher la liste des communautés sur la page d'accueil (#146)

## v1.3 - 2023.01.23
- [DEV] restauration en local de la dernière sauvegarde de prod (#145)
- [WP] Mise à jour des liens dans le header et le footer (#144)
- Mise à jour des dépendances (#143)
- Nouveau design de la liste des communautés (#142)
- Réduction de largeur de colonne du post-content (#141)

## v1.2 - 2023.01.16
- Corrections Stats - ordonner les périodes pour les graphes (#139 et #140)
- Suppression des apps `machina` non utilisées et refactoring des apps `forum` et `forum_member` (#138)
- Suppression de la vue de tous les membres du Forum (#137)
- Ajout/Mise à jour des actions Engagement envoyées à Matomo (#136)
- Mise à jour des graphiques de statistiques (#135)
- Mise à jour du theme itou vers la v0.5.7 (#134)

## v1.1 - 2023.01.09
- Mise à jour des dépendances (#133)
- Settings: retrait du hook `poetry-lock` de precommit (#132)
- Correction de la mise en forme de l'avatar topic-thumbnail (#131)
- Nettoyage des tests automatiques (#130)
- Rediriger vers le bon endroit dans la bonne page après l'authentification IC (#129)
- Afficher le nombre de votes par défaut avant de participer à un sondage (#128)
- Convertir automatiquement les url dans les descriptions des communautés et dans les posts (#127)
- Afficher les réponses aux annonces dans le fil d'actualités (#126)
- Integration Continue : Generation du Journal des Changements (#125)
- Traduction de Likes, Post, Engagement et Funnel (#124)
- Afficher le jour et l'heure de publication d'un post en temps relatif (#123)
- Rediriger l'utilisateur vers sa page de profil après la mise à jour de son profil (#122)
