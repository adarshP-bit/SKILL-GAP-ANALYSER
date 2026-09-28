"""Local server for Skill Gap Analyzer.
Serves the web page and forwards job-API requests (avoids browser CORS blocks).
Uses only the Python standard library."""
import http.server, socketserver, urllib.request, urllib.parse, os, threading, webbrowser, sys

LIBS = {
    "pdf.min.js": "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js",
    "pdf.worker.min.js": "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js",
}
ALLOWED = {"remotive.com", "www.arbeitnow.com", "www.themuse.com", "jobicy.com", "remoteok.com", "himalayas.app"}
ROOT = os.path.dirname(os.path.abspath(__file__))
PAGE = "skill-gap-analyzer.html"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def log_message(self, fmt, *args):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        if self.path.startswith("/proxy?"):
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            url = (qs.get("url") or [""])[0]
            host = urllib.parse.urlparse(url).netloc
            if host not in ALLOWED:
                self.send_error(403, "Host not allowed")
                return
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 SkillGapAnalyzer", "Accept": "application/json"})
                with urllib.request.urlopen(req, timeout=20) as r:
                    body = r.read(8_000_000)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                self.send_error(502, str(e)[:100])
            return
        super().do_GET()

class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

def fetch_libs():
    """Download the PDF reader once so PDF upload works without the CDN."""
    d = os.path.join(ROOT, "libs")
    os.makedirs(d, exist_ok=True)
    for name, url in LIBS.items():
        path = os.path.join(d, name)
        if os.path.exists(path) and os.path.getsize(path) > 10000:
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=40) as r, open(path, "wb") as f:
                f.write(r.read())
            print("Downloaded", name)
        except Exception as e:
            print("Could not download", name, "(the page will use the online copy)")

def main():
    for port in range(8765, 8785):
        try:
            srv = Server(("127.0.0.1", port), Handler)
            break
        except OSError:
            continue
    else:
        print("No free port found."); sys.exit(1)
    url = f"http://localhost:{port}/{PAGE}"
    print(f"Skill Gap Analyzer running at {url}")
    print("Keep this window open. Press Ctrl+C to stop.")
    threading.Thread(target=fetch_libs, daemon=True).start()
    threading.Timer(1.5, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
