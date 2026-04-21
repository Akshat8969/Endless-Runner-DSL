"""
compiler.py  –  Main entry point for the Game DSL compiler.
"""

from __future__ import annotations
import argparse
import json
import sys
import os
import webbrowser
import http.server
import socketserver
import subprocess
from pathlib import Path

from lexer    import tokenize, LexerError
from parser   import Parser, ParseError
from semantic import SemanticAnalyser
from codegen  import CodeGenerator

# ─────────────────────────────────────────────
#  Coloured terminal output
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
#  Pipeline runner
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
#  CLI & UI Injector / Server
# ─────────────────────────────────────────────
def _build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Game DSL → JSON compiler")
    ap.add_argument("source", help="Path to the .dsl source file")
    ap.add_argument("-o", "--output", default="../subway-final/game_config.json", help="Output JSON path")
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument("--dump-tokens", action="store_true")
    ap.add_argument("--dump-ast", action="store_true")
    return ap

if __name__ == "__main__":
    args = _build_arg_parser().parse_args()
    result = compile_dsl(
        source_path = args.source,
        output_path = args.output,
        verbose     = args.verbose,
        dump_tokens = args.dump_tokens,
        dump_ast    = args.dump_ast,
    )
    
    if result is not None:
        try:
            # 1. Read the fresh DSL code
            with open(args.source, "r", encoding="utf-8") as f:
                raw_dsl = f.read()
                
            # 2. Read the base HTML template
            with open("front.html", "r", encoding="utf-8") as f:
                html_content = f.read()
                
            # 3. Inject the DSL into the placeholder
            injected_html = html_content.replace("__DSL_CONTENT__", raw_dsl)
            
            # 4. Save and launch the live file
            live_html_path = "front_live.html"
            with open(live_html_path, "w", encoding="utf-8") as f:
                f.write(injected_html)
                
            browser_path = 'file://' + os.path.realpath(live_html_path)
            print(f"Launching interactive pipeline: {browser_path}")
            webbrowser.open(browser_path)
           # ────────────────────────────────────────────────────────
            # 5. START BACKGROUND SERVER TO LISTEN FOR GODOT LAUNCH
            # ────────────────────────────────────────────────────────
            
            GODOT_EXE_PATH = r"C:\Users\aksha\Downloads\Godot_v4.6-stable_win64.exe\Godot_v4.6-stable_win64.exe"
            GODOT_PROJECT_PATH = "../subway-final"
            
            class GodotLaunchHandler(http.server.SimpleHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/launch-godot':
                        self.send_response(200)
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(b"Launching!")
                        
                        print(f"\n{BO}{B}▶ Browser requested Engine Launch...{W}")
                        try:
                            subprocess.Popen([GODOT_EXE_PATH, '--path', GODOT_PROJECT_PATH])
                            print(f"{G}  Godot launched successfully!{W}")
                        except FileNotFoundError:
                            print(f"{R}  ✗ Could not find Godot executable. Please update GODOT_EXE_PATH in compiler.py{W}")
                    else:
                        super().do_GET()
                        
            PORT = 8080
            
            # ---> ADD THIS MAGIC LINE HERE <---
            socketserver.TCPServer.allow_reuse_address = True
            
            print(f"\n{BO}{Y}Compiler is now listening on port {PORT}. Waiting for launch signal...{W}")
            print(f"{Y}(Press Ctrl+C in this terminal to shut down the compiler when you are done.){W}")
            
            with socketserver.TCPServer(("", PORT), GodotLaunchHandler) as httpd:
                httpd.serve_forever()

        except Exception as e:
            print(f"Could not launch visualizer or server: {e}")

    sys.exit(0 if result is not None else 1)