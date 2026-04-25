from __future__ import annotations
import argparse
import json
import sys
import os
import webbrowser
import http.server
import socketserver
import subprocess
import re
import threading
from pathlib import Path

from lexer    import tokenize, LexerError
from parser   import Parser, ParseError
from semantic import SemanticAnalyser
from codegen  import CodeGenerator

try:
    import colorama
    colorama.init(autoreset=True)
    R  = colorama.Fore.RED
    G  = colorama.Fore.GREEN
    Y  = colorama.Fore.YELLOW
    B  = colorama.Fore.CYAN
    W  = colorama.Style.RESET_ALL
    BO = colorama.Style.BRIGHT
except ImportError:
    R = G = Y = B = W = BO = ""

def _banner(title: str):
    print(f"\n{BO}{B}{'─'*55}")
    print(f"  {title}")
    print(f"{'─'*55}{W}")

def _ok(msg: str):   print(f"{G}  ✓  {msg}{W}")
def _warn(msg: str): print(f"{Y}  ⚠  {msg}{W}")
def _err(msg: str):  print(f"{R}  ✗  {msg}{W}")

def compile_dsl(
    source_path: str,
    output_path: str  = "../subway-final/game_config.json",
    verbose:     bool = False,
    dump_tokens: bool = False,
    dump_ast:    bool = False,
) -> dict | None:

    src = Path(source_path)
    if not src.exists():
        _err(f"Source file not found: {source_path}")
        return None

    with src.open() as f:
        code = f.read()

    if verbose:
        _banner("Stage 0 · Source")
        print(code)

    _banner("Stage 1 · Lexer")
    try:
        tokens = tokenize(code)
    except LexerError as exc:
        _err(f"Lexer error at line {exc.line}, col {exc.col}: {exc}")
        return None

    if dump_tokens:
        for tok in tokens:
            print(f"  {tok.kind:<20} {str(tok.value):<25} {tok.line:>4}  {tok.col:>4}")
    _ok(f"{len(tokens)} tokens produced")

    _banner("Stage 2 · Parser")
    try:
        tree = Parser(tokens).parse()
    except ParseError as exc:
        _err(f"Parse error: {exc}")
        return None

    if dump_ast:
        print(json.dumps(tree.to_dict(), indent=2))
    _ok(f"{len(tree.statements)} AST statements generated")

    _banner("Stage 3 · Semantic Analysis")
    analyser = SemanticAnalyser(tree)
    errors, warnings = analyser.analyse()

    for w in warnings: _warn(str(w))
    for e in errors:   _err(f"[ERROR] {e}")

    if errors:
        _err(f"Compilation failed with {len(errors)} error(s).")
        return None

    _ok("Semantic checks passed")

    _banner("Stage 4 · Code Generation")
    config = CodeGenerator(tree).generate()
    _ok("Config dict generated")

    _banner("Stage 5 · Serialise → JSON")
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    with out.open("w") as f:
        json.dump(config, f, indent=4)

    _ok(f"Written to {out.resolve()}")
    print(f"\n{BO}{G}  Compilation successful! ✓{W}\n")
    return config


def _inject_player_name(output_path: str, player_name: str):
    """Reads compiled game_config.json, injects player_name, writes back."""
    p = Path(output_path)
    if not p.exists():
        _warn("game_config.json not found — skipping name injection")
        return
    try:
        with p.open("r", encoding="utf-8") as f:
            cfg = json.load(f)
        cfg["player_name"] = player_name
        with p.open("w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
        _ok(f"Player name '{player_name}' injected into game_config.json")
    except Exception as e:
        _warn(f"Could not inject player name: {e}")


def _build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Game DSL → JSON compiler")
    ap.add_argument("source", help="Path to the .dsl source file")
    ap.add_argument("-o", "--output", default="../subway-final/game_config.json")
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument("--dump-tokens", action="store_true")
    ap.add_argument("--dump-ast", action="store_true")
    return ap


# ── Global state ──────────────────────────────────────────────────────────────
godot_process      = None
godot_closed_event = threading.Event()
OUTPUT_PATH        = "../subway-final/game_config.json"


def _watch_godot(proc: subprocess.Popen):
    proc.wait()
    print(f"\n{BO}{Y}  Godot has closed — returning to welcome page…{W}")
    godot_closed_event.set()


if __name__ == "__main__":
    args = _build_arg_parser().parse_args()
    OUTPUT_PATH = args.output

    result = compile_dsl(
        source_path = args.source,
        output_path = args.output,
        verbose     = args.verbose,
        dump_tokens = args.dump_tokens,
        dump_ast    = args.dump_ast,
    )

    if result is not None:
        try:
            with open(args.source, "r", encoding="utf-8") as f:
                raw_dsl = f.read()

            html_path = os.path.join("pages", "index.html")
            with open(html_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            injected_html = re.sub(
                r'(<textarea id="source"[^>]*>).*?(</textarea>)',
                rf'\1\n{raw_dsl}\n\2',
                html_content,
                flags=re.DOTALL
            )

            with open(html_path, "w", encoding="utf-8") as f:
                f.write(injected_html)

            browser_url = 'http://localhost:8000/welcome.html'
            print(f"{BO}{B}Launching interactive pipeline: {browser_url}{W}")
            webbrowser.open(browser_url)

            GODOT_EXE_PATH     = r"C:\Users\aksha\Downloads\Godot_v4.6-stable_win64.exe\Godot_v4.6-stable_win64.exe"
            GODOT_PROJECT_PATH = "../subway-final"

            class GodotLaunchHandler(http.server.SimpleHTTPRequestHandler):

                def do_GET(self):
                    global godot_process

                    # /launch-godot?name=PlayerName
                    if self.path.startswith('/launch-godot'):
                        import urllib.parse
                        player_name = "Player"
                        if '?' in self.path:
                            qs = self.path.split('?', 1)[1]
                            for part in qs.split('&'):
                                if part.startswith('name='):
                                    player_name = urllib.parse.unquote_plus(
                                        part[5:]
                                    ).strip() or "Player"

                        self.send_response(200)
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(b"Launching!")

                        # Inject name BEFORE Godot opens
                        _inject_player_name(OUTPUT_PATH, player_name)

                        print(f"\n{BO}{B}▶ Launching Godot (player: {player_name})…{W}")
                        try:
                            godot_closed_event.clear()
                            godot_process = subprocess.Popen(
                                [GODOT_EXE_PATH, '--path', GODOT_PROJECT_PATH]
                            )
                            t = threading.Thread(
                                target=_watch_godot, args=(godot_process,), daemon=True
                            )
                            t.start()
                            print(f"{G}  Godot launched (PID {godot_process.pid})!{W}")
                        except FileNotFoundError:
                            print(f"{R}  ✗ Godot not found. Update GODOT_EXE_PATH.{W}")

                    elif self.path.startswith('/check-status'):
                        self.send_response(200)
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        is_running = godot_process is not None and godot_process.poll() is None
                        payload = (
                            '{"running":true}' if is_running
                            else '{"running":false,"redirect":"http://localhost:8000/welcome.html"}'
                        )
                        self.wfile.write(payload.encode())

                    elif self.path == '/godot-closed':
                        fired = godot_closed_event.wait(timeout=10)
                        self.send_response(200)
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(b'{"closed":true}' if fired else b'{"closed":false}')

                    else:
                        super().do_GET()

                def log_message(self, format, *args):
                    pass

            PORT = 8080
            socketserver.TCPServer.allow_reuse_address = True
            print(f"\n{BO}{Y}Backend listening on port {PORT}. Press Ctrl+C to stop.{W}")
            with socketserver.TCPServer(("", PORT), GodotLaunchHandler) as httpd:
                httpd.serve_forever()

        except Exception as e:
            print(f"Could not launch visualiser: {e}")

    sys.exit(0 if result is not None else 1)