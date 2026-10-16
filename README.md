# 🏴‍☠️ YggDex — L'Index & Moteur de Recherche Local Complet de YGG

[![Python Version](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Database](https://img.shields.io/badge/SQLite-FTS5-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![GitHub Pages](https://img.shields.io/badge/Web%20Demo-GitHub%20Pages-22c55e?style=for-the-badge&logo=github)](docs/index.html)
[![Release](https://img.shields.io/badge/Release-v1.0.0-f59e0b?style=for-the-badge)](release/RELEASE_NOTES.md)

**YggDex** est un moteur de recherche local hors-ligne, ultra-rapide et autonome, indexant l'intégralité de l'archive YGG (**1 218 387 torrents** et **1 125 385 jaquettes/affiches**).

Il intègre une interface moderne type Netflix / Plex avec affiches grand format, des liens magnets optimisés (avec trackers publics DHT/PeX), et une **intégration directe en 1 clic avec l'application [Torrent Studio](#-intégration-avec-torrent-studio)**.

---

## ⚡ Fonctionnalités Clés

- 🚀 **Performance FTS5 instantanée** : Recherche plein texte en **moins de 5 millisecondes**, insensible à la casse et **tolérante aux accents français** (*Amélie* = *amelie*).
- 🖼️ **1 125 385 jaquettes & affiches (92,4% de couverture)** : Présentation visuelle élégante pour les films, séries, animes, jeux vidéo, ebooks et albums musicaux.
- ⚡ **Intégration directe avec Torrent Studio** : Cliquez sur **« ⚡ Télécharger »** : si Torrent Studio n'est pas lancé, YggDex le démarre automatiquement en tâche de fond et lance immédiatement le téléchargement.
- 🧲 **Liens Magnets complets & Fichiers .torrent** :
  - **Copie Magnet** en un clic avec trackers fiables intégrés pour une découverte DHT maximale.
  - **Lien .torrent direct** via le cache mondial *iTorrents*.
- ⊞ **Double Mode d'Affichage** :
  - **Mode Affiches (Grille)** : Cartes avec posters grand format (ratio 2:3), badges de résolution et taille, zoom au survol.
  - **Mode Liste compacte** : Tableau condensé avec vignettes pour parcourir rapidement de grands volumes.
- 🎯 **Filtres Avancés** :
  - Par catégorie principale (Films, Séries, Jeux, Musique, Ebooks, Applications, Emulation, etc.) et sous-catégories.
  - Par résolution : `4K / 2160p`, `1080p`, `720p`, `MULTI / VF`, `VOSTFR`.
  - Par taille : `< 2 Go`, `2 à 10 Go`, `> 10 Go`.
  - Filtre exclusif *« 🖼 Avec jaquette »*.
- 🌐 **Version Web prête pour GitHub Pages** : Déployable directement sur GitHub Pages (`/docs`), avec passerelle automatique vers votre base locale si vous êtes sur votre PC.
- 📦 **100% Autonome (Zéro Dépendance)** : Fonctionne directement avec Python standard (aucun `npm`, aucun `pip install`).

---

## 🚀 Installation Rapide (Windows)

### Méthode 1 : Pack Complet Clé en Main (Recommandé)
1. Rendez-vous dans les **[Releases GitHub](../../releases)** et téléchargez **`YggDex_v1.0.0_Full_With_Database.zip`**.
2. Décompressez l'archive dans le dossier de votre choix (ex: `D:\YggDex`).
3. Double-cliquez sur **`installer.bat`** :
   - Vérifie votre installation Python.
   - Crée un raccourci **`🏴‍☠️ YggDex`** sur votre Bureau.
   - Lance le serveur et ouvre automatiquement votre navigateur sur **http://localhost:7777**.

---

## 💻 Lancement au quotidien

Double-cliquez sur le raccourci créé sur votre Bureau ou sur :
```bat
Lancer_YggDex.bat
```
L'interface s'ouvre directement sur **http://localhost:7777**.

---

## ⚡ Intégration avec Torrent Studio

Si vous possédez l'application **Torrent Studio** (placée par exemple dans `E:\App\All\Media\App\Torrent_Studio`) :

1. Sur n'importe quel torrent dans YggDex, cliquez sur le bouton doré **« ⚡ Télécharger »**.
2. YggDex vérifie si Torrent Studio est actif :
   - S'il est éteint, **il le démarre automatiquement en tâche de fond**.
   - Il transmet le torrent directement à l'API interne (`POST /api/torrents/add-magnet`).
3. Le téléchargement commence immédiatement dans votre dossier Downloads (`Downloads\`).
4. Le bouton passe en vert : **`✔ Dans Studio !`**.

> Un bouton **`⚡ Torrent Studio`** avec voyant d'état (🟢/⚪) est également présent en haut à droite pour accéder en 1 clic au tableau de bord de téléchargement (`http://127.0.0.1:5050`).

---

## 🌐 Déploiement sur GitHub Pages

Le dossier **`docs/`** contient une édition web spécialement optimisée pour être hébergée sur **GitHub Pages** :

1. Sur votre dépôt GitHub, allez dans **Settings** > **Pages**.
2. Sous **Build and deployment** :
   - **Source** : `Deploy from a branch`
   - **Branch** : `main` et dossier `/docs`
   - Cliquez sur **Save**.
3. Votre site sera instantanément accessible sur :
   `https://<votre-pseudo>.github.io/<nom-du-repo>/`

**Fonctionnement de la version Web :**
- Si votre serveur local `YggDex` est allumé sur votre machine : la page web GitHub Pages s'y connecte automatiquement et interroge l'intégralité des **1,21 million de torrents** avec le bouton *Télécharger dans Torrent Studio* !
- Si le serveur local est éteint : la page bascule gracieusement en mode **Démo Web** avec un dataset représentatif de ~250 torrents populaires.

---

## 🛠️ Structure du Projet

```
YggDex/
├── .gitignore               # Fichiers ignorés par Git (dont la base SQLite 950 Mo)
├── LICENSE                  # Licence MIT
├── README.md                # Documentation complète du projet
├── installer.bat            # Assistant d'installation et raccourci bureau
├── Lancer_YggDex.bat        # Lanceur rapide Windows (Port 7777)
├── server.py                # Serveur HTTP local multithreadé + Pont Torrent Studio
├── index.html               # Application Web locale avec affiches & filtres
├── ygg_torrents.db          # Base SQLite optimisée FTS5 (1,22M torrents & jaquettes)
├── docs/                    # Version autonome pour GitHub Pages
│   ├── index.html           # Interface Web avec passerelle localhost
│   └── demo_torrents.json   # Échantillon de démonstration autonome
└── scripts/
    └── creer_release.py     # Générateur d'archives ZIP de release et hashs SHA-256
```

---

## 📦 Comment publier sur GitHub ?

1. Initialisez le dépôt local :
   ```bash
   git init
   git add .
   git commit -m "feat: Initial commit YggDex v1.0.0"
   ```
2. Liez votre dépôt GitHub distant :
   ```bash
   git remote add origin https://github.com/<votre-pseudo>/YggDex.git
   git branch -M main
   git push -u origin main
   ```
   *(Note : Grâce au `.gitignore`, le fichier `ygg_torrents.db` ne sera pas envoyé dans le git, respectant la limite de 100 Mo de GitHub).*

3. Générez le package de release :
   ```bash
   python scripts/creer_release.py
   ```
4. Dans votre dépôt GitHub :
   - Allez dans **Releases** > **Draft a new release**.
   - Créez le tag `v1.0.0`.
   - Glissez-déposez le fichier **`release/YggDex_v1.0.0_Full_With_Database.zip`** (GitHub Releases autorise les fichiers jusqu'à 2 Go).
   - Collez le contenu de **`release/RELEASE_NOTES.md`** et publiez !
5. Activez GitHub Pages (**Settings > Pages > Branch: main, /docs**).

---

## 📜 Licence

Ce projet est sous licence [MIT](LICENSE).
Base de données et métadonnées indexées à des fins d'archivage et de recherche locale.
