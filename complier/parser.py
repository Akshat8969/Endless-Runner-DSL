"""
parser.py  –  Recursive-descent parser for the Game DSL.

Supported grammar (EBNF sketch):

  program        ::= statement* EOF
  statement      ::= player_stmt
                   | increase_stmt
                   | obstacle_stmt
                   | coin_stmt
                   | powerup_stmt
                   | background_stmt
                   | difficulty_stmt
                   | sound_stmt
                   | music_stmt
                   | set_stmt

  player_stmt    ::= PLAYER SPEED NUMBER
                   | PLAYER LIVES NUMBER
                   | PLAYER SIZE NUMBER
                   | PLAYER COLOR STRING

  increase_stmt  ::= INCREASE SPEED NUMBER EVERY NUMBER
                   | INCREASE SCORE BY NUMBER

  obstacle_stmt  ::= OBSTACLE SPAWN RATE NUMBER
                   | OBSTACLE SPEED NUMBER
                   | OBSTACLE SIZE NUMBER
                   | OBSTACLE COLOR STRING

  coin_stmt      ::= COIN VALUE NUMBER
                   | COIN SPAWN RATE NUMBER
                   | COIN COLOR STRING

  powerup_stmt   ::= POWERUP SPAWN RATE NUMBER
                   | POWERUP VALUE NUMBER

  background_stmt::= BACKGROUND COLOR STRING
                   | BACKGROUND SPEED NUMBER

  difficulty_stmt::= DIFFICULTY (EASY | MEDIUM | HARD)

  sound_stmt     ::= SOUND ENABLE | SOUND DISABLE
  music_stmt     ::= MUSIC ENABLE | MUSIC DISABLE

  set_stmt       ::= SET ID NUMBER
"""

from __future__ import annotations
from lexer import Token


# ─────────────────────────────────────────────
#  AST node types
# ─────────────────────────────────────────────

class ASTNode:
    """Base class for all AST nodes."""
    node_type: str = "node"

    def to_dict(self) -> dict:
        raise NotImplementedError


class ProgramNode(ASTNode):
    node_type = "program"

    def __init__(self, statements: list[ASTNode]):
        self.statements = statements

    def to_dict(self):
        return {
            "type": self.node_type,
            "statements": [s.to_dict() for s in self.statements]
        }


class PlayerSpeedNode(ASTNode):
    node_type = "player_speed"
    def __init__(self, speed: int | float):
        self.speed = speed
    def to_dict(self):
        return {"type": self.node_type, "speed": self.speed}


class PlayerLivesNode(ASTNode):
    node_type = "player_lives"
    def __init__(self, lives: int):
        self.lives = lives
    def to_dict(self):
        return {"type": self.node_type, "lives": self.lives}


class PlayerSizeNode(ASTNode):
    node_type = "player_size"
    def __init__(self, size: int | float):
        self.size = size
    def to_dict(self):
        return {"type": self.node_type, "size": self.size}


class PlayerColorNode(ASTNode):
    node_type = "player_color"
    def __init__(self, color: str):
        self.color = color
    def to_dict(self):
        return {"type": self.node_type, "color": self.color}


class IncreaseSpeedNode(ASTNode):
    node_type = "increase_speed"
    def __init__(self, amount: int | float, interval: int | float):
        self.amount   = amount
        self.interval = interval
    def to_dict(self):
        return {"type": self.node_type,
                "amount": self.amount, "interval": self.interval}


class IncreaseScoreNode(ASTNode):
    node_type = "increase_score"
    def __init__(self, amount: int | float):
        self.amount = amount
    def to_dict(self):
        return {"type": self.node_type, "amount": self.amount}


class ObstacleSpawnRateNode(ASTNode):
    node_type = "obstacle_spawn_rate"
    def __init__(self, rate: int | float):
        self.rate = rate
    def to_dict(self):
        return {"type": self.node_type, "rate": self.rate}


class ObstacleSpeedNode(ASTNode):
    node_type = "obstacle_speed"
    def __init__(self, speed: int | float):
        self.speed = speed
    def to_dict(self):
        return {"type": self.node_type, "speed": self.speed}


class ObstacleSizeNode(ASTNode):
    node_type = "obstacle_size"
    def __init__(self, size: int | float):
        self.size = size
    def to_dict(self):
        return {"type": self.node_type, "size": self.size}


class ObstacleColorNode(ASTNode):
    node_type = "obstacle_color"
    def __init__(self, color: str):
        self.color = color
    def to_dict(self):
        return {"type": self.node_type, "color": self.color}


class CoinValueNode(ASTNode):
    node_type = "coin_value"
    def __init__(self, value: int | float):
        self.value = value
    def to_dict(self):
        return {"type": self.node_type, "value": self.value}


class CoinSpawnRateNode(ASTNode):
    node_type = "coin_spawn_rate"
    def __init__(self, rate: int | float):
        self.rate = rate
    def to_dict(self):
        return {"type": self.node_type, "rate": self.rate}


class CoinColorNode(ASTNode):
    node_type = "coin_color"
    def __init__(self, color: str):
        self.color = color
    def to_dict(self):
        return {"type": self.node_type, "color": self.color}


class PowerupSpawnRateNode(ASTNode):
    node_type = "powerup_spawn_rate"
    def __init__(self, rate: int | float):
        self.rate = rate
    def to_dict(self):
        return {"type": self.node_type, "rate": self.rate}


class PowerupValueNode(ASTNode):
    node_type = "powerup_value"
    def __init__(self, value: int | float):
        self.value = value
    def to_dict(self):
        return {"type": self.node_type, "value": self.value}


class BackgroundColorNode(ASTNode):
    node_type = "background_color"
    def __init__(self, color: str):
        self.color = color
    def to_dict(self):
        return {"type": self.node_type, "color": self.color}


class BackgroundSpeedNode(ASTNode):
    node_type = "background_speed"
    def __init__(self, speed: int | float):
        self.speed = speed
    def to_dict(self):
        return {"type": self.node_type, "speed": self.speed}


class DifficultyNode(ASTNode):
    node_type = "difficulty"
    def __init__(self, level: str):
        self.level = level
    def to_dict(self):
        return {"type": self.node_type, "level": self.level}


class SoundNode(ASTNode):
    node_type = "sound"
    def __init__(self, enabled: bool):
        self.enabled = enabled
    def to_dict(self):
        return {"type": self.node_type, "enabled": self.enabled}


class MusicNode(ASTNode):
    node_type = "music"
    def __init__(self, enabled: bool):
        self.enabled = enabled
    def to_dict(self):
        return {"type": self.node_type, "enabled": self.enabled}


class SetVarNode(ASTNode):
    node_type = "set_var"
    def __init__(self, name: str, value: int | float):
        self.name  = name
        self.value = value
    def to_dict(self):
        return {"type": self.node_type, "name": self.name, "value": self.value}


# ─────────────────────────────────────────────
#  Parser
# ─────────────────────────────────────────────

class ParseError(Exception):
    def __init__(self, message: str, token: Token | None = None):
        super().__init__(message)
        self.token = token


class Parser:

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos    = 0

    # ── helpers ────────────────────────────────

    def current(self) -> Token:
        return self.tokens[self.pos]

    def peek(self, offset: int = 1) -> Token:
        idx = self.pos + offset
        return self.tokens[idx] if idx < len(self.tokens) else self.tokens[-1]

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def expect(self, kind: str) -> Token:
        tok = self.current()
        if tok.kind != kind:
            raise ParseError(
                f"Expected {kind} but got {tok.kind!r} ({tok.value!r}) "
                f"at line {tok.line}, col {tok.col}",
                tok
            )
        return self.advance()

    def expect_number(self) -> int | float:
        tok = self.current()
        if tok.kind not in ('NUMBER', 'FLOAT'):
            raise ParseError(
                f"Expected a number but got {tok.kind!r} ({tok.value!r}) "
                f"at line {tok.line}, col {tok.col}",
                tok
            )
        return self.advance().value

    def expect_string(self) -> str:
        tok = self.current()
        if tok.kind != 'STRING':
            raise ParseError(
                f"Expected a string (quoted) but got {tok.kind!r} ({tok.value!r}) "
                f"at line {tok.line}, col {tok.col}",
                tok
            )
        return self.advance().value

    # ── top-level ──────────────────────────────

    def parse(self) -> ProgramNode:
        statements: list[ASTNode] = []
        while self.current().kind != 'EOF':
            stmt = self._parse_statement()
            if stmt is not None:
                statements.append(stmt)
        return ProgramNode(statements)

    def _parse_statement(self) -> ASTNode | None:
        tok = self.current()

        dispatch = {
            'PLAYER':     self._parse_player,
            'INCREASE':   self._parse_increase,
            'OBSTACLE':   self._parse_obstacle,
            'COIN':       self._parse_coin,
            'POWERUP':    self._parse_powerup,
            'BACKGROUND': self._parse_background,
            'DIFFICULTY': self._parse_difficulty,
            'SOUND':      self._parse_sound,
            'MUSIC':      self._parse_music,
            'SET':        self._parse_set,
        }

        handler = dispatch.get(tok.kind)
        if handler:
            return handler()

        # Unknown token — skip with a warning
        print(f"  [parser] Warning: unexpected token {tok.kind!r} at "
              f"line {tok.line}, col {tok.col} — skipping.")
        self.advance()
        return None

    # ── statement parsers ──────────────────────

    def _parse_player(self) -> ASTNode:
        self.expect('PLAYER')
        kind = self.current().kind

        if kind == 'SPEED':
            self.advance()
            return PlayerSpeedNode(self.expect_number())
        if kind == 'LIVES':
            self.advance()
            return PlayerLivesNode(int(self.expect_number()))
        if kind == 'SIZE':
            self.advance()
            return PlayerSizeNode(self.expect_number())
        if kind == 'COLOR':
            self.advance()
            return PlayerColorNode(self.expect_string())
        raise ParseError(
            f"Unknown PLAYER attribute {self.current().kind!r} at "
            f"line {self.current().line}",
            self.current()
        )

    def _parse_increase(self) -> ASTNode:
        self.expect('INCREASE')
        kind = self.current().kind

        if kind == 'SPEED':
            self.advance()
            amount = self.expect_number()
            self.expect('EVERY')
            interval = self.expect_number()
            return IncreaseSpeedNode(amount, interval)

        if kind == 'SCORE':
            self.advance()
            self.expect('BY')
            amount = self.expect_number()
            return IncreaseScoreNode(amount)

        raise ParseError(
            f"Unknown INCREASE target {self.current().kind!r} at "
            f"line {self.current().line}",
            self.current()
        )

    def _parse_obstacle(self) -> ASTNode:
        self.expect('OBSTACLE')
        kind = self.current().kind

        if kind == 'SPAWN':
            self.advance()
            self.expect('RATE')
            return ObstacleSpawnRateNode(self.expect_number())
        if kind == 'SPEED':
            self.advance()
            return ObstacleSpeedNode(self.expect_number())
        if kind == 'SIZE':
            self.advance()
            return ObstacleSizeNode(self.expect_number())
        if kind == 'COLOR':
            self.advance()
            return ObstacleColorNode(self.expect_string())

        raise ParseError(
            f"Unknown OBSTACLE attribute {self.current().kind!r} at "
            f"line {self.current().line}",
            self.current()
        )

    def _parse_coin(self) -> ASTNode:
        self.expect('COIN')
        kind = self.current().kind

        if kind == 'VALUE':
            self.advance()
            return CoinValueNode(self.expect_number())
        if kind == 'SPAWN':
            self.advance()
            self.expect('RATE')
            return CoinSpawnRateNode(self.expect_number())
        if kind == 'COLOR':
            self.advance()
            return CoinColorNode(self.expect_string())

        raise ParseError(
            f"Unknown COIN attribute {self.current().kind!r} at "
            f"line {self.current().line}",
            self.current()
        )

    def _parse_powerup(self) -> ASTNode:
        self.expect('POWERUP')
        kind = self.current().kind

        if kind == 'SPAWN':
            self.advance()
            self.expect('RATE')
            return PowerupSpawnRateNode(self.expect_number())
        if kind == 'VALUE':
            self.advance()
            return PowerupValueNode(self.expect_number())

        raise ParseError(
            f"Unknown POWERUP attribute {self.current().kind!r} at "
            f"line {self.current().line}",
            self.current()
        )

    def _parse_background(self) -> ASTNode:
        self.expect('BACKGROUND')
        kind = self.current().kind

        if kind == 'COLOR':
            self.advance()
            return BackgroundColorNode(self.expect_string())
        if kind == 'SPEED':
            self.advance()
            return BackgroundSpeedNode(self.expect_number())

        raise ParseError(
            f"Unknown BACKGROUND attribute {self.current().kind!r} at "
            f"line {self.current().line}",
            self.current()
        )

    def _parse_difficulty(self) -> ASTNode:
        self.expect('DIFFICULTY')
        tok = self.current()
        if tok.kind in ('EASY', 'MEDIUM', 'HARD'):
            self.advance()
            return DifficultyNode(tok.kind.lower())
        raise ParseError(
            f"Expected EASY | MEDIUM | HARD but got {tok.kind!r} at "
            f"line {tok.line}",
            tok
        )

    def _parse_sound(self) -> ASTNode:
        self.expect('SOUND')
        tok = self.current()
        if tok.kind in ('ENABLE', 'DISABLE'):
            self.advance()
            return SoundNode(tok.kind == 'ENABLE')
        raise ParseError(
            f"Expected ENABLE or DISABLE after SOUND at line {tok.line}",
            tok
        )

    def _parse_music(self) -> ASTNode:
        self.expect('MUSIC')
        tok = self.current()
        if tok.kind in ('ENABLE', 'DISABLE'):
            self.advance()
            return MusicNode(tok.kind == 'ENABLE')
        raise ParseError(
            f"Expected ENABLE or DISABLE after MUSIC at line {tok.line}",
            tok
        )

    def _parse_set(self) -> ASTNode:
        self.expect('SET')
        name  = self.expect('ID').value
        value = self.expect_number()
        return SetVarNode(name, value)