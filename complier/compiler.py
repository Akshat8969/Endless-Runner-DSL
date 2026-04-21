"""
compiler.py  –  Main entry point for the Game DSL compiler.

Pipeline:
    Source code (.dsl)
        │
        ▼  [Lexer]        lexer.py
     Tokens
        │
        ▼  [Parser]       parser.py
        AST (ProgramNode)
        │
        ▼  [Semantic]     semantic.py
     Validated AST
        │
        ▼  [CodeGen]      codegen.py
    game_config dict
        │
        ▼  [Serialiser]   (here)
    game_config.json

Usage:
    python compiler.py game.dsl
    python compiler.py game.dsl --output path/to/game_config.json
    python compiler.py game.dsl --verbose     # prints each pipeline stage
    python compiler.py game.dsl --dump-tokens
    python compiler.py game.dsl --dump-ast
"""

from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

from lexer    import tokenize, LexerError
from parser   import Parser, ParseError
from semantic import SemanticAnalyser
from codegen  import CodeGenerator


# ─────────────────────────────────────────────
#  Coloured terminal output (degrades gracefully)
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
    """
    Run the full compilation pipeline.
    Returns the config dict on success, or None on failure.
    """

    # ── Read source ───────────────────────────
    src = Path(source_path)
    if not src.exists():
        _err(f"Source file not found: {source_path}")
        return None

    with src.open() as f:
        code = f.read()

    if verbose:
        _banner("Stage 0 · Source")
        print(code)

    # ── Lex ───────────────────────────────────
    _banner("Stage 1 · Lexer")
    try:
        tokens = tokenize(code)
    except LexerError as exc:
        _err(f"Lexer error at line {exc.line}, col {exc.col}: {exc}")
        return None

    if dump_tokens:
        print(f"  {'KIND':<20} {'VALUE':<25} {'LINE':>4}  {'COL':>4}")
        print(f"  {'─'*20} {'─'*25} {'─'*4}  {'─'*4}")
        for tok in tokens:
            print(f"  {tok.kind:<20} {str(tok.value):<25} {tok.line:>4}  {tok.col:>4}")

    _ok(f"{len(tokens)} tokens produced")

    # ── Parse ─────────────────────────────────
    _banner("Stage 2 · Parser")
    try:
        tree = Parser(tokens).parse()
    except ParseError as exc:
        _err(f"Parse error: {exc}")
        return None

    if dump_ast:
        print(json.dumps(tree.to_dict(), indent=2))

    _ok(f"{len(tree.statements)} AST statements generated")

    # ── Semantic analysis ─────────────────────
    _banner("Stage 3 · Semantic Analysis")
    analyser = SemanticAnalyser(tree)
    errors, warnings = analyser.analyse()

    for w in warnings:
        _warn(str(w))
    for e in errors:
        _err(f"[ERROR] {e}")

    if errors:
        _err(f"Compilation failed with {len(errors)} error(s).")
        return None

    _ok("Semantic checks passed" +
        (f" ({len(warnings)} warning(s))" if warnings else ""))

    # ── Code generation ───────────────────────
    _banner("Stage 4 · Code Generation")
    config = CodeGenerator(tree).generate()
    _ok("Config dict generated")

    # ── Serialise ─────────────────────────────
    _banner("Stage 5 · Serialise → JSON")
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    with out.open("w") as f:
        json.dump(config, f, indent=4)

    _ok(f"Written to {out.resolve()}")

    if verbose:
        print()
        print(json.dumps(config, indent=4))

    print(f"\n{BO}{G}  Compilation successful! ✓{W}\n")
    return config


# ─────────────────────────────────────────────
#  CLI
# ─────────────────────────────────────────────

def _build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="compiler",
        description="Game DSL → JSON compiler",
    )
    ap.add_argument("source",
                    help="Path to the .dsl source file")
    ap.add_argument("-o", "--output",
                    default="../subway-final/game_config.json",
                    help="Output JSON path (default: ../subway-final/game_config.json)")
    ap.add_argument("-v", "--verbose",
                    action="store_true",
                    help="Print source and final JSON")
    ap.add_argument("--dump-tokens",
                    action="store_true",
                    help="Print token table after lexing")
    ap.add_argument("--dump-ast",
                    action="store_true",
                    help="Print AST as JSON after parsing")
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
    sys.exit(0 if result is not None else 1)