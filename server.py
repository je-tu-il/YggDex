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
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
import webbrowser

PORT = 7777
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

def get_db():
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

            elif path == "/api/torrent-studio/status":
                running = is_studio_alive()
                self.send_json({
                    "installed": os.path.exists(TORRENT_STUDIO_EXE),
                    "running": running,
                    "url": TORRENT_STUDIO_API
                })
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
    server_address = ("127.0.0.1", PORT)
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
