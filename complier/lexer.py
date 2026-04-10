import re

TOKENS = [
    ('NUMBER', r'\d+'),
    ('PLAYER', r'PLAYER'),
    ('SPEED', r'SPEED'),
    ('INCREASE', r'INCREASE'),
    ('EVERY', r'EVERY'),
    ('ID', r'[a-zA-Z_]+'),
    ('SKIP', r'[ \t]+'),
    ('NEWLINE', r'\n'),
]

def tokenize(code):
    token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKENS)
    tokens = []

    for match in re.finditer(token_regex, code):
        kind = match.lastgroup
        value = match.group()

        if kind == 'NUMBER':
            value = int(value)

        if kind != 'SKIP' and kind != 'NEWLINE':
            tokens.append((kind, value))

    return tokens