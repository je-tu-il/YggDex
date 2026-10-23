"""
Serveur Web local ultra-rapide pour le moteur de recherche YGG.
100% autonome, zéro dépendance externe (uniquement la bibliothèque standard Python).
Supporte les jaquettes / miniatures, recherche instantanée FTS5, gestion robuste des déconnexions
et intégration native directe avec Torrent Studio.
"""

import os
import sys
import re
import time
import json
import sqlite3
import datetime
import subprocess
import urllib.request
import urllib.parse
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
import webbrowser

PORT = int(os.environ.get("PORT", 7777))
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(SCRIPT_DIR, "ygg_torrents.db")
HTML_FILE = os.path.join(SCRIPT_DIR, "index.html")

# Configuration de Torrent Studio
TORRENT_STUDIO_DIR = r"E:\App\All\Media\App\Torrent_Studio"
TORRENT_STUDIO_EXE = os.path.join(TORRENT_STUDIO_DIR, "TorrentStudio.exe")
TORRENT_STUDIO_API = "http://127.0.0.1:5050"

def is_studio_alive():
    try:
        req = urllib.request.urlopen(f"{TORRENT_STUDIO_API}/api/settings", timeout=1)
        return req.status == 200
    except Exception:
        return False

def ensure_studio_running():
    if is_studio_alive():
        return True
    if os.path.exists(TORRENT_STUDIO_EXE):
        try:
            subprocess.Popen([TORRENT_STUDIO_EXE], cwd=TORRENT_STUDIO_DIR)
            for _ in range(30):  # jusqu'à 6s d'attente
                time.sleep(0.2)
                if is_studio_alive():
                    return True
        except Exception as e:
            print(f"[!] Erreur au lancement de TorrentStudio : {e}")
    return False

def format_size(bytes_val):
    if not bytes_val or bytes_val <= 0:
        return "0 o"
    for unit in ['o', 'Ko', 'Mo', 'Go', 'To', 'Po']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} Po"

def format_date(timestamp):
    if not timestamp or timestamp <= 0:
        return "Inconnue"
    try:
        return datetime.datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M')
    except Exception:
        return "Inconnue"

MEDIA_EXTENSIONS = ('.mp4', '.mkv', '.avi', '.mov', '.webm', '.m4v', '.ts', '.mp3', '.flac', '.m4a', '.ogg')

def find_best_media_file(directory):
    best_file = None
    best_size = 0
    if not os.path.exists(directory):
        return None
    for root, _, files in os.walk(directory):
        for f in files:
            if f.lower().endswith(MEDIA_EXTENSIONS):
                fp = os.path.join(root, f)
                try:
                    sz = os.path.getsize(fp)
                    if sz > best_size:
                        best_size = sz
                        best_file = fp
                except Exception:
                    pass
    return best_file

def find_torrent_file(name="", target_path="", hash_info=""):
    user_dl = os.path.expanduser(r"~\Downloads")
    studio_dl = os.path.join(TORRENT_STUDIO_DIR, "downloads")
    search_dirs = [user_dl, studio_dl]

    # 1. Chemin direct
    if target_path and os.path.exists(target_path):
        if os.path.isfile(target_path):
            return target_path
        elif os.path.isdir(target_path):
            best = find_best_media_file(target_path)
            if best:
                return best

    # 2. Recherche par nom direct dans Downloads
    if name:
        for base in search_dirs:
            if not os.path.exists(base):
                continue
            cand = os.path.join(base, name)
            if os.path.exists(cand):
                if os.path.isfile(cand):
                    return cand
                elif os.path.isdir(cand):
                    best = find_best_media_file(cand)
                    if best:
                        return best

        # 3. Recherche floue / partielle
        clean_target = re.sub(r'[^a-zA-Z0-9]', '', name).lower()
        if len(clean_target) >= 5:
            for base in search_dirs:
                if not os.path.exists(base):
                    continue
                try:
                    for item in os.listdir(base):
                        clean_item = re.sub(r'[^a-zA-Z0-9]', '', item).lower()
                        if clean_target in clean_item or clean_item in clean_target:
                            full_p = os.path.join(base, item)
                            if os.path.isfile(full_p) and full_p.lower().endswith(MEDIA_EXTENSIONS):
                                return full_p
                            elif os.path.isdir(full_p):
                                best = find_best_media_file(full_p)
                                if best:
                                    return best
                except Exception:
                    pass
    return None

def ensure_database_extracted():
    if os.path.exists(DB_FILE):
        return True
    db_parts_dir = os.path.join(SCRIPT_DIR, "database")
    if os.path.exists(db_parts_dir):
        parts = sorted([os.path.join(db_parts_dir, f) for f in os.listdir(db_parts_dir) if f.startswith("ygg_db.part")])
        if parts:
            print("[+] Décompression initiale de la base de données YGG (1,22 million de torrents)...")
            import zipfile
            temp_zip = os.path.join(SCRIPT_DIR, "temp_ygg_db.zip")
            try:
                with open(temp_zip, "wb") as f_out:
                    for p in parts:
                        with open(p, "rb") as f_in:
                            while chunk := f_in.read(1024 * 1024 * 8):
                                f_out.write(chunk)
                with zipfile.ZipFile(temp_zip) as zf:
                    zf.extractall(SCRIPT_DIR)
                print("[OK] Base de données ygg_torrents.db prête !")
                return True
            finally:
                if os.path.exists(temp_zip):
                    try:
                        os.remove(temp_zip)
                    except Exception:
                        pass
    return False

def get_db():
    ensure_database_extracted()
    conn = sqlite3.connect(f"file:{DB_FILE}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn

class SearchHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silence HTTP logs in standard console
        pass

    def send_json(self, data, status=200):
        try:
            body = json.dumps(data, ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()
            self.wfile.write(body)
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        try:
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path

            if path == "/api/torrent-studio/download":
                length = int(self.headers.get("Content-Length", 0))
                raw_data = self.rfile.read(length) if length > 0 else b"{}"
                data = json.loads(raw_data.decode("utf-8"))
                magnet = data.get("magnet", "").strip()

                if not magnet:
                    self.send_json({"error": "Lien magnet requis"}, status=400)
                    return

                # Démarrage automatique de Torrent Studio s'il n'est pas encore actif
                if not ensure_studio_running():
                    self.send_json({"error": "Impossible de démarrer Torrent Studio (fichier introuvable)"}, status=500)
                    return

                # Répertoire de téléchargement (Downloads par défaut)
                user_dl = os.path.expanduser(r"~\Downloads")
                save_path = data.get("save_path") or (user_dl if os.path.exists(user_dl) else os.path.join(TORRENT_STUDIO_DIR, "downloads"))

                payload = json.dumps({
                    "magnet": magnet,
                    "save_path": save_path
                }).encode("utf-8")

                req = urllib.request.Request(
                    f"{TORRENT_STUDIO_API}/api/torrents/add-magnet",
                    data=payload,
                    headers={"Content-Type": "application/json"}
                )

                try:
                    resp = urllib.request.urlopen(req, timeout=5)
                    studio_resp = json.loads(resp.read().decode("utf-8"))
                    self.send_json({
                        "success": True,
                        "message": "Téléchargement lancé dans Torrent Studio !",
                        "studio_url": TORRENT_STUDIO_API,
                        "torrent": studio_resp.get("torrent")
                    })
                except urllib.error.HTTPError as e:
                    err_content = e.read().decode("utf-8", errors="replace")
                    self.send_json({"error": f"Torrent Studio Error: {err_content}"}, status=e.code)
                return

            elif path == "/api/torrent-studio/action":
                length = int(self.headers.get("Content-Length", 0))
                raw_data = self.rfile.read(length) if length > 0 else b"{}"
                try:
                    req = urllib.request.Request(
                        f"{TORRENT_STUDIO_API}/api/torrents/action",
                        data=raw_data,
                        headers={"Content-Type": "application/json"}
                    )
                    resp = urllib.request.urlopen(req, timeout=5)
                    self.send_json(json.loads(resp.read().decode("utf-8")))
                except Exception as e:
                    self.send_json({"error": str(e)}, status=500)
                return

            elif path == "/api/torrent-studio/open-folder":
                length = int(self.headers.get("Content-Length", 0))
                raw_data = self.rfile.read(length) if length > 0 else b"{}"
                data = json.loads(raw_data.decode("utf-8")) if raw_data else {}
                target_path = data.get("path")
                torrent_name = data.get("name")
                user_dl = os.path.expanduser(r"~\Downloads")
                full_path = None
                if target_path and os.path.exists(target_path):
                    full_path = target_path
                elif torrent_name:
                    cand = os.path.join(user_dl, torrent_name)
                    if os.path.exists(cand):
                        full_path = cand

                try:
                    if full_path and os.path.exists(full_path):
                        subprocess.Popen(['explorer.exe', '/select,', os.path.normpath(full_path)])
                    else:
                        os.startfile(user_dl)
                    self.send_json({"success": True})
                except Exception as e:
                    self.send_json({"error": str(e)}, status=500)
                return

            self.send_error(404, "Endpoint POST introuvable")

        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            pass
        except Exception as e:
            try:
                self.send_json({"error": str(e)}, status=500)
            except Exception:
                pass

    def do_GET(self):
        try:
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path
            params = urllib.parse.parse_qs(parsed.query)

            if path == "/" or path == "/index.html":
                if os.path.exists(HTML_FILE):
                    with open(HTML_FILE, "rb") as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                else:
                    self.send_error(404, "index.html introuvable")
                return

            elif path in ("/studio", "/studio.html"):
                studio_file = os.path.join(SCRIPT_DIR, "studio.html")
                if not os.path.exists(studio_file):
                    studio_file = os.path.join(SCRIPT_DIR, "docs", "studio.html")
                if os.path.exists(studio_file):
                    with open(studio_file, "rb") as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                else:
                    self.send_error(404, "studio.html introuvable")
                return

            elif path == "/api/torrent-studio/status":
                running = is_studio_alive()
                self.send_json({
                    "installed": os.path.exists(TORRENT_STUDIO_EXE),
                    "running": running,
                    "url": TORRENT_STUDIO_API
                })
                return

            elif path == "/api/torrent-studio/start":
                started = ensure_studio_running()
                self.send_json({"running": started, "url": TORRENT_STUDIO_API})
                return

            elif path == "/api/torrent-studio/torrents":
                if not is_studio_alive():
                    if os.path.exists(TORRENT_STUDIO_EXE):
                        ensure_studio_running()
                if not is_studio_alive():
                    self.send_json({"running": False, "torrents": [], "stats": {}})
                    return
                try:
                    req = urllib.request.urlopen(f"{TORRENT_STUDIO_API}/api/torrents", timeout=3)
                    data = json.loads(req.read().decode("utf-8"))
                    data["running"] = True
                    self.send_json(data)
                except Exception as e:
                    self.send_json({"running": False, "error": str(e), "torrents": [], "stats": {}})
                return

            elif path == "/api/torrent-studio/file":
                name = params.get("name", [""])[0]
                target_path = params.get("path", [""])[0]
                target_file = find_torrent_file(name=name, target_path=target_path)

                if target_file and os.path.isfile(target_file):
                    filename = os.path.basename(target_file)
                    file_size = os.path.getsize(target_file)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/octet-stream")
                    self.send_header("Content-Disposition", f'attachment; filename="{urllib.parse.quote(filename)}"')
                    self.send_header("Content-Length", str(file_size))
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    with open(target_file, "rb") as f:
                        while chunk := f.read(1024 * 1024):
                            self.wfile.write(chunk)
                else:
                    self.send_error(404, "Fichier introuvable dans les Téléchargements")
                return

            elif path == "/api/stream/start":
                magnet = params.get("magnet", [""])[0].strip()
                name = params.get("name", [""])[0].strip()
                target_path = params.get("path", [""])[0].strip()
                hash_info = params.get("hash", [""])[0].strip()

                target_file = find_torrent_file(name=name, target_path=target_path, hash_info=hash_info)
                if target_file and os.path.exists(target_file) and os.path.getsize(target_file) > 1024 * 512:
                    self.send_json({
                        "ready": True,
                        "status": "ready",
                        "name": os.path.basename(target_file),
                        "path": target_file,
                        "size": os.path.getsize(target_file),
                        "size_formatted": format_size(os.path.getsize(target_file)),
                        "stream_url": f"/api/stream/video?path={urllib.parse.quote(target_file)}"
                    })
                    return

                if magnet:
                    ensure_studio_running()
                    try:
                        user_dl = os.path.expanduser(r"~\Downloads")
                        payload = json.dumps({
                            "magnet": magnet,
                            "save_path": user_dl
                        }).encode("utf-8")
                        req = urllib.request.Request(
                            f"{TORRENT_STUDIO_API}/api/torrents/add-magnet",
                            data=payload,
                            headers={"Content-Type": "application/json"}
                        )
                        urllib.request.urlopen(req, timeout=4)
                    except Exception:
                        pass

                self.send_json({
                    "ready": False,
                    "status": "buffering",
                    "name": name,
                    "message": "Démarrage du téléchargement séquentiel dans Torrent Studio..."
                })
                return

            elif path == "/api/stream/status":
                name = params.get("name", [""])[0].strip()
                target_path = params.get("path", [""])[0].strip()
                hash_info = params.get("hash", [""])[0].strip()

                target_file = find_torrent_file(name=name, target_path=target_path, hash_info=hash_info)
                if target_file and os.path.exists(target_file) and os.path.getsize(target_file) > 1024 * 1024:
                    self.send_json({
                        "ready": True,
                        "status": "ready",
                        "name": os.path.basename(target_file),
                        "path": target_file,
                        "size": os.path.getsize(target_file),
                        "size_formatted": format_size(os.path.getsize(target_file)),
                        "stream_url": f"/api/stream/video?path={urllib.parse.quote(target_file)}"
                    })
                    return

                studio_info = {}
                if is_studio_alive():
                    try:
                        req = urllib.request.urlopen(f"{TORRENT_STUDIO_API}/api/torrents", timeout=2)
                        data = json.loads(req.read().decode("utf-8"))
                        for t in data.get("torrents", []):
                            if (hash_info and hash_info.lower() in t.get("hash", "").lower()) or (name and name.lower() in t.get("name", "").lower()):
                                studio_info = t
                                break
                    except Exception:
                        pass

                self.send_json({
                    "ready": False,
                    "status": "buffering",
                    "name": name,
                    "torrent": studio_info
                })
                return

            elif path == "/api/stream/video":
                name = params.get("name", [""])[0].strip()
                target_path = params.get("path", [""])[0].strip()
                hash_info = params.get("hash", [""])[0].strip()

                target_file = find_torrent_file(name=name, target_path=target_path, hash_info=hash_info)
                if not target_file or not os.path.exists(target_file):
                    self.send_error(404, "Fichier vidéo non encore disponible pour le streaming")
                    return

                file_size = os.path.getsize(target_file)
                mime_type, _ = mimetypes.guess_type(target_file)
                if not mime_type:
                    ext = os.path.splitext(target_file)[1].lower()
                    if ext in ('.mp4', '.m4v'):
                        mime_type = 'video/mp4'
                    elif ext in ('.webm',):
                        mime_type = 'video/webm'
                    elif ext in ('.mkv',):
                        mime_type = 'video/mp4'
                    elif ext in ('.mp3',):
                        mime_type = 'audio/mpeg'
                    else:
                        mime_type = 'video/mp4'

                range_header = self.headers.get("Range")
                if range_header and range_header.startswith("bytes="):
                    range_val = range_header[6:].strip()
                    parts = range_val.split("-")
                    start = int(parts[0]) if parts[0] else 0
                    end = int(parts[1]) if len(parts) > 1 and parts[1] else file_size - 1
                    if end >= file_size:
                        end = file_size - 1
                    content_length = end - start + 1

                    self.send_response(206)
                    self.send_header("Content-Type", mime_type)
                    self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
                    self.send_header("Content-Length", str(content_length))
                    self.send_header("Accept-Ranges", "bytes")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()

                    with open(target_file, "rb") as f:
                        f.seek(start)
                        remaining = content_length
                        chunk_size = 64 * 1024
                        while remaining > 0:
                            read_len = min(remaining, chunk_size)
                            chunk = f.read(read_len)
                            if not chunk:
                                break
                            try:
                                self.wfile.write(chunk)
                            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                                break
                            remaining -= len(chunk)
                else:
                    self.send_response(200)
                    self.send_header("Content-Type", mime_type)
                    self.send_header("Content-Length", str(file_size))
                    self.send_header("Accept-Ranges", "bytes")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()

                    with open(target_file, "rb") as f:
                        chunk_size = 64 * 1024
                        while chunk := f.read(chunk_size):
                            try:
                                self.wfile.write(chunk)
                            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                                break
                return

            elif path == "/api/stream/open-external":
                name = params.get("name", [""])[0].strip()
                target_path = params.get("path", [""])[0].strip()
                hash_info = params.get("hash", [""])[0].strip()

                target_file = find_torrent_file(name=name, target_path=target_path, hash_info=hash_info)
                if target_file and os.path.exists(target_file):
                    try:
                        os.startfile(target_file)
                        self.send_json({"success": True, "path": target_file})
                    except Exception as e:
                        self.send_json({"error": str(e)}, status=500)
                else:
                    self.send_json({"error": "Fichier introuvable sur le disque"}, status=404)
                return

            elif path == "/api/stats":
                conn = get_db()
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*), SUM(size) FROM torrents")
                row = cur.fetchone()
                total_count = row[0] or 0
                total_size = row[1] or 0

                cover_count = 0
                try:
                    cur.execute("SELECT COUNT(*) FROM covers")
                    cover_count = cur.fetchone()[0] or 0
                except Exception:
                    pass

                conn.close()
                self.send_json({
                    "total_torrents": total_count,
                    "total_size": total_size,
                    "total_size_formatted": format_size(total_size),
                    "total_covers": cover_count
                })
                return

            elif path == "/api/categories":
                conn = get_db()
                cur = conn.cursor()
                cur.execute("""
                    SELECT 
                        parent_category_id, parent_category_name, 
                        category_id, category_name, COUNT(*) as count 
                    FROM torrents 
                    WHERE category_name != '' 
                    GROUP BY parent_category_id, category_id 
                    ORDER BY parent_category_name, category_name
                """)
                rows = cur.fetchall()
                parents = {}
                for r in rows:
                    pid = r["parent_category_id"]
                    pname = r["parent_category_name"] or "Autre"
                    if pid not in parents:
                        parents[pid] = {
                            "id": pid,
                            "name": pname,
                            "count": 0,
                            "subcategories": []
                        }
                    parents[pid]["count"] += r["count"]
                    parents[pid]["subcategories"].append({
                        "id": r["category_id"],
                        "name": r["category_name"],
                        "count": r["count"]
                    })
                conn.close()
                self.send_json({"categories": list(parents.values())})
                return

            elif path == "/api/search":
                q = params.get("q", [""])[0].strip()
                cat_id = params.get("category", [""])[0].strip()
                pcat_id = params.get("parent_category", [""])[0].strip()
                quality = params.get("quality", [""])[0].strip()
                has_image = params.get("has_image", ["0"])[0].strip() == "1"
                min_size = params.get("min_size", [""])[0].strip()
                max_size = params.get("max_size", [""])[0].strip()
                sort = params.get("sort", ["relevance" if q else "date"])[0].strip()
                order = params.get("order", ["desc"])[0].strip().upper()
                if order not in ["ASC", "DESC"]:
                    order = "DESC"

                page = max(1, int(params.get("page", ["1"])[0]))
                limit = min(100, max(10, int(params.get("limit", ["48"])[0])))
                offset = (page - 1) * limit

                conn = get_db()
                cur = conn.cursor()

                conditions = []
                args = []

                if cat_id and cat_id.isdigit():
                    conditions.append("t.category_id = ?")
                    args.append(int(cat_id))
                elif pcat_id and pcat_id.isdigit():
                    conditions.append("t.parent_category_id = ?")
                    args.append(int(pcat_id))

                if has_image:
                    conditions.append("c.image_url IS NOT NULL")

                if min_size and min_size.isdigit():
                    conditions.append("t.size >= ?")
                    args.append(int(min_size))
                if max_size and max_size.isdigit():
                    conditions.append("t.size <= ?")
                    args.append(int(max_size))

                # Traitement de la recherche (mots-clés + qualité)
                search_terms = []
                if q:
                    search_terms.extend(q.replace('"', ' ').replace("'", ' ').split())
                if quality:
                    search_terms.append(quality)

                use_fts = bool(search_terms)
                if use_fts:
                    clean_terms = []
                    for term in search_terms:
                        clean_t = re.sub(r'[^a-zA-Z0-9\u00C0-\u017F]', '', term)
                        if clean_t:
                            clean_terms.append(f'"{clean_t}"*')
                    
                    if clean_terms:
                        fts_query = " AND ".join(clean_terms)
                        conditions.append("f.torrents_fts MATCH ?")
                        args.append(fts_query)
                    else:
                        use_fts = False

                where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""

                # Définition du tri
                order_by_sql = "t.publish_date DESC"
                if sort == "relevance" and use_fts:
                    order_by_sql = f"f.rank ASC, t.publish_date {order}"
                elif sort == "size":
                    order_by_sql = f"t.size {order}"
                elif sort == "date":
                    order_by_sql = f"t.publish_date {order}"
                elif sort == "seed":
                    order_by_sql = f"t.seed {order}"
                elif sort == "completed":
                    order_by_sql = f"t.completed {order}"
                elif sort == "name":
                    order_by_sql = f"t.name {order}"

                has_covers_table = True
                try:
                    cur.execute("SELECT 1 FROM covers LIMIT 1")
                except Exception:
                    has_covers_table = False

                covers_join = "LEFT JOIN covers c ON c.id = t.id" if has_covers_table else ""
                covers_col = "c.image_url" if has_covers_table else "NULL as image_url"

                if use_fts:
                    count_sql = f"""
                        SELECT COUNT(*) 
                        FROM torrents_fts f
                        JOIN torrents t ON t.id = f.rowid
                        {covers_join}
                        {where_clause}
                    """
                    data_sql = f"""
                        SELECT 
                            t.id, t.name, t.category_id, t.parent_category_id,
                            t.category_name, t.parent_category_name, t.category_slug,
                            t.size, t.publish_date, t.hash_info, t.magnet,
                            t.seed, t.leech, t.completed,
                            {covers_col}
                        FROM torrents_fts f
                        JOIN torrents t ON t.id = f.rowid
                        {covers_join}
                        {where_clause}
                        ORDER BY {order_by_sql}
                        LIMIT ? OFFSET ?
                    """
                else:
                    count_sql = f"SELECT COUNT(*) FROM torrents t {covers_join} {where_clause}"
                    data_sql = f"""
                        SELECT 
                            t.id, t.name, t.category_id, t.parent_category_id,
                            t.category_name, t.parent_category_name, t.category_slug,
                            t.size, t.publish_date, t.hash_info, t.magnet,
                            t.seed, t.leech, t.completed,
                            {covers_col}
                        FROM torrents t
                        {covers_join}
                        {where_clause}
                        ORDER BY {order_by_sql}
                        LIMIT ? OFFSET ?
                    """

                cur.execute(count_sql, args)
                total = cur.fetchone()[0]

                cur.execute(data_sql, args + [limit, offset])
                rows = cur.fetchall()

                results = []
                for r in rows:
                    results.append({
                        "id": r["id"],
                        "name": r["name"],
                        "category_id": r["category_id"],
                        "parent_category_id": r["parent_category_id"],
                        "category_name": r["category_name"] or "Inconnue",
                        "parent_category_name": r["parent_category_name"] or "",
                        "category_slug": r["category_slug"] or "",
                        "size": r["size"],
                        "size_formatted": format_size(r["size"]),
                        "publish_date": r["publish_date"],
                        "date_formatted": format_date(r["publish_date"]),
                        "hash_info": r["hash_info"],
                        "magnet": r["magnet"],
                        "seed": r["seed"],
                        "leech": r["leech"],
                        "completed": r["completed"],
                        "image_url": r["image_url"] if r["image_url"] else "",
                        "torrent_url": f"https://itorrents.org/torrent/{r['hash_info'].upper()}.torrent" if r["hash_info"] else ""
                    })

                conn.close()

                pages = (total + limit - 1) // limit if total > 0 else 1
                self.send_json({
                    "total": total,
                    "page": page,
                    "pages": pages,
                    "limit": limit,
                    "results": results
                })
                return

            self.send_error(404, "Page introuvable")

        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            pass
        except Exception as e:
            try:
                self.send_json({"error": str(e)}, status=500)
            except Exception:
                pass

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):
        err_type = sys.exc_info()[0]
        if err_type in (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            return
        super().handle_error(request, client_address)

def run():
    server_address = ("0.0.0.0", PORT)
    httpd = ThreadedHTTPServer(server_address, SearchHandler)
    url = f"http://localhost:{PORT}"
    print("=" * 60)
    print(f"MOTEUR DE RECHERCHE YGG ACTIF : {url}")
    print(f"Torrent Studio lié : {TORRENT_STUDIO_DIR}")
    print("Appuyez sur Ctrl+C pour arrêter le serveur.")
    print("=" * 60)
    if "--no-browser" not in sys.argv:
        webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt du serveur...")
        httpd.server_close()

if __name__ == "__main__":
    run()
