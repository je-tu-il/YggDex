"""
Script de création automatique de la Release GitHub pour YggDex.
Génère les archives ZIP prêtes à être attachées à la release GitHub
et calcule les empreintes SHA-256 d'intégrité.
"""

import os
import sys
import time
import zipfile
import hashlib

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RELEASE_DIR = os.path.join(SCRIPT_DIR, "release")
os.makedirs(RELEASE_DIR, exist_ok=True)

VERSION = "1.0.0"

def get_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192 * 1024):
            h.update(chunk)
    return h.hexdigest()

def main():
    print("=" * 60)
    print(f"CRÉATION DU PACKAGE DE RELEASE YGGDEX v{VERSION}")
    print("=" * 60)

    # 1. Package AppOnly (sans la grosse base)
    app_zip_name = f"YggDex_v{VERSION}_AppOnly.zip"
    app_zip_path = os.path.join(RELEASE_DIR, app_zip_name)
    print(f"\n[1/2] Création de l'archive légère : {app_zip_name} ...")
    
    app_files = [
        "server.py",
        "index.html",
        "Lancer_YggDex.bat",
        "installer.bat",
        "README.md",
        "LICENSE"
    ]
    with zipfile.ZipFile(app_zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in app_files:
            fp = os.path.join(SCRIPT_DIR, f)
            if os.path.exists(fp):
                zf.write(fp, f)
                print(f"  + Ajouté : {f}")

    app_size_mb = os.path.getsize(app_zip_path) / (1024 * 1024)
    app_sha = get_sha256(app_zip_path)
    print(f"[OK] {app_zip_name} généré ({app_size_mb:.2f} Mo) - SHA256: {app_sha[:16]}...")

    # 2. Package Complet (avec la base de données SQLite 1.2M torrents)
    db_file = os.path.join(SCRIPT_DIR, "ygg_torrents.db")
    full_zip_name = f"YggDex_v{VERSION}_Full_With_Database.zip"
    full_zip_path = os.path.join(RELEASE_DIR, full_zip_name)

    if os.path.exists(db_file):
        print(f"\n[2/2] Création du package complet avec base de données (~950 Mo)...")
        t0 = time.time()
        # Compression rapide (niveau 1 ou 3 pour aller vite tout en réduisant bien la taille)
        with zipfile.ZipFile(full_zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=3) as zf:
            for f in app_files:
                fp = os.path.join(SCRIPT_DIR, f)
                if os.path.exists(fp):
                    zf.write(fp, f)
            print("  + Compression de ygg_torrents.db (veuillez patienter ~30s)...")
            zf.write(db_file, "ygg_torrents.db")

        full_size_mb = os.path.getsize(full_zip_path) / (1024 * 1024)
        full_sha = get_sha256(full_zip_path)
        print(f"[OK] {full_zip_name} généré en {time.time()-t0:.1f}s ({full_size_mb:.1f} Mo)")
    else:
        print("[!] ygg_torrents.db introuvable, package complet ignoré.")
        full_zip_name = None
        full_sha = None

    # 3. Génération des Release Notes au format Markdown
    notes_file = os.path.join(RELEASE_DIR, "RELEASE_NOTES.md")
    with open(notes_file, "w", encoding="utf-8") as f:
        f.write(f"""# 🏴‍☠️ YggDex v{VERSION} — L'Index & Moteur de Recherche Local Complet de YGG

Première version majeure de **YggDex**, le moteur de recherche local hors-ligne autonome indexant l'intégralité de la base de données YGG.

## 🚀 Nouveautés & Fonctionnalités

- **Base complète préservée** : 1 218 387 torrents avec titres exacts, dates et tailles réelles.
- **1 125 385 jaquettes & miniatures (92,4% de couverture)** : Affiches grand format pour les films, séries, jeux vidéo, ebooks et musique.
- **Recherche plein texte instantanée (SQLite FTS5)** : Temps de réponse inférieur à 5 ms avec tolérance complète aux accents (`amelie` = `Amélie`).
- **Intégration directe avec Torrent Studio** : Un clic sur **« ⚡ Télécharger »** démarre Torrent Studio en arrière-plan et lance immédiatement le téléchargement dans votre dossier Downloads.
- **Double affichage** : Mode Affiches / Posters (grille type Netflix/Plex) et Mode Liste compacte.
- **Filtres avancés** : Par catégories, résolutions (`4K`, `1080p`, `720p`, `MULTI`, `VOSTFR`) et tranches de taille.
- **Version Web GitHub Pages** : Explorez la démo en ligne sur GitHub Pages avec passerelle automatique vers votre instance locale.
- **Zéro dépendance externe** : Fonctionne avec Python standard sans aucun `pip install`.

---

## 📦 Fichiers de la Release

| Fichier | Description | Taille | SHA-256 |
|---------|-------------|--------|---------|
| **`{full_zip_name}`** | **Pack Complet Clé en Main** (Application + Base 1.2M torrents & jaquettes) | ~{full_size_mb:.1f} Mo | `{full_sha}` |
| **`{app_zip_name}`** | Application seule (légère, sans la base de données) | ~{app_size_mb:.2f} Mo | `{app_sha}` |

---

## ⚡ Installation Rapide

1. Téléchargez et décompressez **`{full_zip_name}`**.
2. Double-cliquez sur **`installer.bat`** (crée le raccourci sur le Bureau et initialise l'application).
3. Profitez de la recherche instantanée sur **http://localhost:7777** !
""")

    print("\n" + "=" * 60)
    print(f"[SUCCÈS] Release préparée avec succès dans : {RELEASE_DIR}")
    print(f"Notes de release prêtes : {notes_file}")
    print("=" * 60)

if __name__ == "__main__":
    main()
