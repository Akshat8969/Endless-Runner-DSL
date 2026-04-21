"""
semantic.py  –  Semantic analysis pass for the Game DSL.

Validates the AST before code generation:
  • Checks that required settings are present (PLAYER SPEED, PLAYER LIVES)
  • Validates numeric ranges (speed > 0, lives ∈ [1,10], rates ≥ 0, …)
  • Warns about contradictions (e.g. spawn rate 0 with a value defined)
  • Accumulates all errors/warnings so the whole file is checked at once
"""

from __future__ import annotations
from parser import (
    ProgramNode, ASTNode,
    PlayerSpeedNode, PlayerLivesNode, PlayerSizeNode, PlayerColorNode,
    IncreaseSpeedNode, IncreaseScoreNode,
    ObstacleSpawnRateNode, ObstacleSpeedNode, ObstacleSizeNode, ObstacleColorNode,
    CoinValueNode, CoinSpawnRateNode, CoinColorNode,
    PowerupSpawnRateNode, PowerupValueNode,
    BackgroundColorNode, BackgroundSpeedNode,
    DifficultyNode, SoundNode, MusicNode, SetVarNode,
)


class SemanticError(Exception):
    pass


class SemanticWarning:
    def __init__(self, message: str):
        self.message = message
    def __str__(self):
        return f"[WARNING] {self.message}"


class SemanticAnalyser:
    """
    Walk a ProgramNode AST, collect errors + warnings.
    Call `.analyse()` which returns `(errors, warnings)`.
    """

    REQUIRED = {'player_speed', 'player_lives'}

    # Numeric bounds: node_type → {field: (min, max)}  (None = no bound)
    BOUNDS: dict[str, dict[str, tuple]] = {
        'player_speed':       {'speed':    (1, 9999)},
        'player_lives':       {'lives':    (1, 10)},
        'player_size':        {'size':     (1, 500)},
        'increase_speed':     {'amount':   (0.1, 100), 'interval': (1, 3600)},
        'increase_score':     {'amount':   (1, 100000)},
        'obstacle_spawn_rate':{'rate':     (0, 100)},
        'obstacle_speed':     {'speed':    (1, 9999)},
        'obstacle_size':      {'size':     (1, 500)},
        'coin_value':         {'value':    (1, 1000000)},
        'coin_spawn_rate':    {'rate':     (0, 100)},
        'powerup_spawn_rate': {'rate':     (0, 100)},
        'powerup_value':      {'value':    (1, 1000000)},
        'background_speed':   {'speed':    (0, 9999)},
    }

    def __init__(self, tree: ProgramNode):
        self.tree     = tree
        self.errors:   list[str]            = []
        self.warnings: list[SemanticWarning] = []
        self._seen:    set[str]             = set()    # node types seen

    def analyse(self) -> tuple[list[str], list[SemanticWarning]]:
        for stmt in self.tree.statements:
            self._check(stmt)
        self._check_required()
        self._cross_checks()
        return self.errors, self.warnings

    # ── per-node checks ────────────────────────

    def _check(self, node: ASTNode):
        self._seen.add(node.node_type)
        self._check_bounds(node)

    def _check_bounds(self, node: ASTNode):
        bounds = self.BOUNDS.get(node.node_type, {})
        for field, (lo, hi) in bounds.items():
            val = getattr(node, field, None)
            if val is None:
                continue
            if lo is not None and val < lo:
                self.errors.append(
                    f"{node.node_type}.{field} = {val} is below minimum ({lo})"
                )
            if hi is not None and val > hi:
                self.errors.append(
                    f"{node.node_type}.{field} = {val} exceeds maximum ({hi})"
                )

    # ── global checks ──────────────────────────

    def _check_required(self):
        for req in self.REQUIRED:
            if req not in self._seen:
                self.errors.append(
                    f"Missing required statement: {req.upper().replace('_', ' ')}"
                )

    def _cross_checks(self):
        # Warn if coin_value defined but coin_spawn_rate is 0
        if 'coin_value' in self._seen and 'coin_spawn_rate' in self._seen:
            for stmt in self.tree.statements:
                if isinstance(stmt, CoinSpawnRateNode) and stmt.rate == 0:
                    self.warnings.append(SemanticWarning(
                        "COIN VALUE is set but COIN SPAWN RATE is 0 — coins will never appear."
                    ))

        # Warn if powerup_value defined but powerup_spawn_rate is 0
        if 'powerup_value' in self._seen and 'powerup_spawn_rate' in self._seen:
            for stmt in self.tree.statements:
                if isinstance(stmt, PowerupSpawnRateNode) and stmt.rate == 0:
                    self.warnings.append(SemanticWarning(
                        "POWERUP VALUE is set but POWERUP SPAWN RATE is 0 — power-ups will never appear."
                    ))

        # Warn if increase_speed interval is extremely short
        for stmt in self.tree.statements:
            if isinstance(stmt, IncreaseSpeedNode) and stmt.interval < 3:
                self.warnings.append(SemanticWarning(
                    f"INCREASE SPEED interval is very short ({stmt.interval}s) — "
                    "game may become impossibly fast quickly."
                ))