import re

# ─────────────────────────────────────────────
#  TOKEN DEFINITIONS
#  Order matters: longer / more-specific patterns first
# ─────────────────────────────────────────────
TOKENS = [
    # Literals
    ('FLOAT',    r'\d+\.\d+'),
    ('NUMBER',   r'\d+'),
    ('STRING',   r'"[^"]*"'),
    ('BOOL',     r'\b(true|false)\b'),

    # Keywords – gameplay
    ('PLAYER',   r'\bPLAYER\b'),
    ('SPEED',    r'\bSPEED\b'),
    ('INCREASE', r'\bINCREASE\b'),
    ('EVERY',    r'\bEVERY\b'),
    ('LIVES',    r'\bLIVES\b'),
    ('SCORE',    r'\bSCORE\b'),

    # Keywords – world
    ('OBSTACLE', r'\bOBSTACLE\b'),
    ('COIN',     r'\bCOIN\b'),
    ('POWERUP',  r'\bPOWERUP\b'),
    ('BACKGROUND', r'\bBACKGROUND\b'),

    # Keywords – difficulty
    ('DIFFICULTY', r'\bDIFFICULTY\b'),
    ('EASY',     r'\bEASY\b'),
    ('MEDIUM',   r'\bMEDIUM\b'),
    ('HARD',     r'\bHARD\b'),

    # Keywords – audio / visual
    ('SOUND',    r'\bSOUND\b'),
    ('MUSIC',    r'\bMUSIC\b'),
    ('COLOR',    r'\bCOLOR\b'),
    ('SIZE',     r'\bSIZE\b'),

    # Modifiers
    ('SPAWN',    r'\bSPAWN\b'),
    ('RATE',     r'\bRATE\b'),
    ('VALUE',    r'\bVALUE\b'),
    ('ENABLE',   r'\bENABLE\b'),
    ('DISABLE',  r'\bDISABLE\b'),
    ('SET',      r'\bSET\b'),
    ('BY',       r'\bBY\b'),
    ('AT',       r'\bAT\b'),
    ('MAX',      r'\bMAX\b'),
    ('MIN',      r'\bMIN\b'),

    # Identifiers (must come after all keywords)
    ('ID',       r'[a-zA-Z_][a-zA-Z0-9_]*'),

    # Punctuation
    ('COLON',    r':'),
    ('COMMA',    r','),
    ('LPAREN',   r'\('),
    ('RPAREN',   r'\)'),
    ('LBRACE',   r'\{'),
    ('RBRACE',   r'\}'),

    # Whitespace / comments  (skipped)
    ('COMMENT',  r'#[^\n]*'),
    ('SKIP',     r'[ \t]+'),
    ('NEWLINE',  r'\n'),
]


class Token:
    """Holds a single lexed token with position information."""

    def __init__(self, kind: str, value, line: int, col: int):
        self.kind  = kind
        self.value = value
        self.line  = line
        self.col   = col

    def __repr__(self):
        return f"Token({self.kind}, {self.value!r}, line={self.line}, col={self.col})"

    def to_dict(self):
        return {"kind": self.kind, "value": self.value,
                "line": self.line, "col": self.col}


class LexerError(Exception):
    def __init__(self, message: str, line: int, col: int):
        super().__init__(message)
        self.line = line
        self.col  = col


def tokenize(code: str) -> list[Token]:
    """
    Tokenize *code* and return a list of Token objects.
    Raises LexerError on unrecognised characters.
    """
    token_regex = '|'.join(
        f'(?P<{name}>{pattern})' for name, pattern in TOKENS
    )
    tokens: list[Token] = []
    line   = 1
    line_start = 0

    for match in re.finditer(token_regex, code):
        kind  = match.lastgroup
        value = match.group()
        col   = match.start() - line_start + 1

        # Coerce numeric types
        if kind == 'NUMBER':
            value = int(value)
        elif kind == 'FLOAT':
            value = float(value)
        elif kind == 'BOOL':
            value = value == 'true'
        elif kind == 'STRING':
            value = value[1:-1]          # strip surrounding quotes

        if kind == 'NEWLINE':
            line += 1
            line_start = match.end()
        elif kind not in ('SKIP', 'COMMENT'):
            tokens.append(Token(kind, value, line, col))

    # Check for characters that didn't match any rule
    matched_end = 0
    for match in re.finditer(token_regex, code):
        if match.start() != matched_end:
            # Gap → unrecognised character
            bad_char  = code[matched_end]
            err_line  = code[:matched_end].count('\n') + 1
            err_col   = matched_end - code[:matched_end].rfind('\n')
            raise LexerError(
                f"Unexpected character {bad_char!r}",
                err_line, err_col
            )
        matched_end = match.end()

    tokens.append(Token('EOF', None, line, 0))
    return tokens