"""
Script de nettoyage complet des fichiers d'archive volumineux et sensibles de YGG.
Supprime tous les dossiers 01_... à 11_... pour ne conserver QUE le moteur de recherche
(ygg_torrents.db, server.py, index.html, Lancer_Recherche_YGG.bat, README.md).
"""

import os
import shutil
import glob
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(SCRIPT_DIR, "ygg_torrents.db")

FOLDERS_TO_DELETE = [
    "01_SOURCE_CODE",
    "02_SERVEUR_PRE_PROD",
    "03_DATABASES",
    "04_CREDENTIALS",
    "05_CRYPTO",
    "06_ACTIVITE_MALVEILLANTE",
    "07_DOCUMENTS_DIVERS",
    "08_COMMUNICATION",
    "09_COMMERCE",
    "10_SERVEURS_LATERAUX",
    "11_OSINT"
]

def purge():
    if not os.path.exists(DB_FILE):
        print("[ERREUR] Le fichier ygg_torrents.db n'existe pas ! Abandon pour sécurité.")
        return

    db_size = os.path.getsize(DB_FILE)
    if db_size < 500 * 1024 * 1024:  # Minimum 500 MB expected
        print(f"[ERREUR] Le fichier ygg_torrents.db est trop petit ({db_size / (1024**2):.1f} Mo). Abandon pour sécurité.")
        return

    print("=" * 60)
    print("NETTOYAGE ET PURGE DES FICHIERS SOURCES DE L'ARCHIVE YGG")
    print(f"Base préservée : ygg_torrents.db ({db_size / (1024**2):.1f} Mo)")
    print("=" * 60)

    # 1. Supprimer les dossiers sources volumineux
    for folder in FOLDERS_TO_DELETE:
        path = os.path.join(SCRIPT_DIR, folder)
        if os.path.exists(path):
            print(f"[-] Suppression du dossier : {folder} ...")
            try:
                shutil.rmtree(path)
                print(f"    [OK] {folder} supprimé.")
            except Exception as e:
                print(f"    [!] Erreur lors de la suppression de {folder}: {e}")

    # 2. Supprimer les fichiers résiduels macOS et logs
    patterns = ["._*", "._.*", ".DS_Store", "import_torrents.py", "extract_covers.py"]
    for pat in patterns:
        for file in glob.glob(os.path.join(SCRIPT_DIR, pat)):
            try:
                if os.path.isfile(file):
                    os.remove(file)
                    print(f"[-] Fichier supprimé : {os.path.basename(file)}")
                elif os.path.isdir(file):
                    shutil.rmtree(file)
                    print(f"[-] Dossier supprimé : {os.path.basename(file)}")
            except Exception as e:
                print(f"    [!] Erreur sur {file}: {e}")

    print("=" * 60)
    print("[SUCCÈS] Nettoyage terminé ! Espace disque libéré.")
    print("Seuls les fichiers nécessaires au moteur de recherche sont conservés.")
    print("=" * 60)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--confirm":
        purge()
    else:
        print("Pour exécuter le nettoyage, lancez avec : python nettoyer_archives_ygg.py --confirm")
