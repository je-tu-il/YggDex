# 🏴‍☠️ YggDex — L'Index & Moteur de Recherche Local Complet de YGG

[![Python Version](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Database](https://img.shields.io/badge/SQLite-FTS5-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Database Included](https://img.shields.io/badge/Base_de_Donn%C3%A9es-1.22M_Torrents_Incluse-10b981?style=for-the-badge&logo=databricks&logoColor=white)](#-la-base-de-données-est-elle-dans-le-dépôt-github-)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![GitHub Pages](https://img.shields.io/badge/Web%20Demo-GitHub%20Pages-22c55e?style=for-the-badge&logo=github)](https://je-tu-il.github.io/YggDex/)

**YggDex** est un moteur de recherche local hors-ligne, ultra-rapide et 100% autonome, indexant l'intégralité de l'archive YGG (**1 218 387 torrents** et **1 125 385 jaquettes/affiches**).

> 💡 **Tout est inclus directement dans le dépôt GitHub !**  
> Pas besoin de télécharger de « Release » externe : la base de données complète est découpée dans le dossier `database/` et s'extrait automatiquement au premier lancement.

---

## 📥 Clients & Téléchargeurs Torrent Recommandés

Pour télécharger les fichiers à partir des liens magnets ou `.torrent` fournis par YggDex, vous avez besoin d'un client BitTorrent :

| Client Torrent | Type | Description | Téléchargement / Accès |
| :--- | :--- | :--- | :--- |
| **qBittorrent** *(Recommandé)* | Open-Source & Gratuit | Sans pub, ultra-complet, support DHT/PeX optimal, gestionnaire de vitesse et lecteur séquentiel. | [👉 Télécharger qBittorrent](https://www.qbittorrent.org/download) |
| **Torrent Studio Web** | Client Web Dégradé | Version 100% web dans le navigateur via WebTorrent (torrent pré-sélectionné, suivi live du téléchargement). | [⚡ Accéder à Torrent Studio Web](https://je-tu-il.github.io/YggDex/studio.html) |
| **Torrent Studio Desktop** | Application Dédiée | Intégration directe en 1 clic avec YggDex (démarrage automatique en tâche de fond + envoi direct du magnet). | Déjà configuré si installé sur votre machine |
| **Transmission** | Minimaliste & Léger | Client épuré, très faible consommation de ressources RAM/CPU. | [👉 Télécharger Transmission](https://transmissionbt.com/download) |

---

## 💾 La Base de Données est-elle dans le Dépôt GitHub ?

**OUI, à 100% !** 

GitHub imposant une limite stricte de 100 Mo par fichier, la base SQLite complète (compressée à 268 Mo) a été découpée en 3 morceaux dans le dossier `database/` :
- `database/ygg_db.part01` (~95 Mo)
- `database/ygg_db.part02` (~95 Mo)
- `database/ygg_db.part03` (~78 Mo)

**Aucune manipulation manuelle n'est requise** :
Dès que vous lancez `installer.bat` ou `python server.py`, le script assemble et extrait automatiquement le fichier `ygg_torrents.db` (950 Mo décompressé) en **moins de 2 secondes** !

---

## ⚡ Fonctionnalités Clés

- 🚀 **Performance FTS5 instantanée** : Recherche plein texte en **moins de 5 millisecondes**, insensible à la casse et **tolérante aux accents français** (*Amélie* = *amelie*).
- 🖼️ **1 125 385 jaquettes & affiches (92,4% de couverture)** : Présentation visuelle élégante pour les films, séries, animes, jeux vidéo, ebooks et albums musicaux.
- ⚡ **Intégration directe avec Torrent Studio** : Cliquez sur **« ⚡ Télécharger »** : si Torrent Studio n'est pas lancé, YggDex le démarre automatiquement en tâche de fond et lance immédiatement le téléchargement via l'API locale.
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

## 🚀 Installation & Utilisation Rapide (Windows)

### 1. Cloner le projet
```bash
git clone https://github.com/je-tu-il/YggDex.git
cd YggDex
```

### 2. Lancer l'assistant d'installation
Double-cliquez sur **`installer.bat`** :
- Vérifie votre installation Python.
- Décompresse automatiquement la base de données depuis `database/`.
- Crée un raccourci **`🏴‍☠️ YggDex`** sur votre Bureau.
- Lance le serveur et ouvre automatiquement votre navigateur sur **http://localhost:7777**.

---

## 💻 Lancement au quotidien

Double-cliquez simplement sur le raccourci sur votre Bureau ou sur :
```bat
Lancer_YggDex.bat
```
L'interface s'ouvre instantanément sur **http://localhost:7777**.

---

## ⚡ Intégration avec Torrent Studio

Si vous possédez l'application **Torrent Studio** :

1. Sur n'importe quel torrent dans YggDex, cliquez sur le bouton doré **« ⚡ Télécharger »**.
2. YggDex vérifie si Torrent Studio est actif :
   - S'il est éteint, **il le démarre automatiquement en tâche de fond**.
   - Il transmet le torrent directement à l'API interne (`POST /api/torrents/add-magnet`).
3. Le téléchargement commence immédiatement dans votre dossier Downloads.
4. Le bouton passe en vert : **`✔ Dans Studio !`**.

> Un bouton **`⚡ Torrent Studio`** avec voyant d'état (🟢/⚪) est également présent dans la barre supérieure pour ouvrir le tableau de bord (`http://127.0.0.1:5050`).

---

## 🌐 Déploiement sur GitHub Pages

Le dossier **`docs/`** contient une édition web spécialement optimisée pour être hébergée sur **GitHub Pages** :

1. Sur votre dépôt GitHub [https://github.com/je-tu-il/YggDex](https://github.com/je-tu-il/YggDex), allez dans **Settings** > **Pages**.
2. Sous **Build and deployment** :
   - **Source** : `Deploy from a branch`
   - **Branch** : `main` et dossier `/docs`
   - Cliquez sur **Save**.
3. Votre site sera accessible sur :  
   **[https://je-tu-il.github.io/YggDex/](https://je-tu-il.github.io/YggDex/)**

**Fonctionnement de la version Web :**
- Si votre serveur local `YggDex` est allumé sur votre machine : la page web GitHub Pages s'y connecte automatiquement et interroge l'intégralité des **1,21 million de torrents** avec le bouton *Télécharger dans Torrent Studio* !
- Si le serveur local est éteint : la page bascule gracieusement en mode **Démo Web** avec un échantillon représentatif de torrents populaires.

---

## 🛠️ Structure du Projet

```
YggDex/
├── .gitignore               # Fichiers ignorés par Git (dont le fichier décompressé 950 Mo)
├── LICENSE                  # Licence MIT
├── README.md                # Documentation complète du projet
├── installer.bat            # Assistant d'installation et création de raccourci bureau
├── Lancer_YggDex.bat        # Lanceur rapide Windows (Port 7777)
├── server.py                # Serveur HTTP local multithreadé + Pont Torrent Studio
├── index.html               # Application Web locale avec affiches, filtres et liens magnets
├── studio.html              # Torrent Studio Web Edition (local)
├── database/                # Base SQLite découpée pour respecter la limite GitHub (< 100 Mo)
│   ├── ygg_db.part01        # Partie 1 (95 Mo)
│   ├── ygg_db.part02        # Partie 2 (95 Mo)
│   └── ygg_db.part03        # Partie 3 (78 Mo)
└── docs/                    # Version Web autonome pour GitHub Pages
    ├── index.html           # Interface Web avec passerelle localhost & liens client torrent
    ├── studio.html          # Torrent Studio Web Edition (WebTorrent in-browser)
    └── demo_torrents.json   # Échantillon de démonstration autonome
```

---

## 📦 Commandes pour Pousser sur GitHub

Pour envoyer le projet sur votre compte GitHub (`je-tu-il`) :

```bash
# 1. Vérifier l'état du dépôt
git status

# 2. Ajouter tous les fichiers (y compris database/ygg_db.part*)
git add .

# 3. Créer le commit
git commit -m "feat: YggDex v1.0.0 avec base de données complète intégrée et liens client torrent"

# 4. Configurer la branche principale et le remote distant
git branch -M main
git remote add origin https://github.com/je-tu-il/YggDex.git

# 5. Pousser vers GitHub
git push -u origin main
```

---

## 📜 Licence

Ce projet est sous licence [MIT](LICENSE).  
Base de données et métadonnées indexées à des fins d'archivage et d'indexation locale.
