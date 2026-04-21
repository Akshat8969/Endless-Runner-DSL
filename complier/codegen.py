"""
codegen.py  –  Code-generation pass for the Game DSL.

Walks the validated AST and produces the final `game_config` dict
that is serialised to JSON.

The output structure is:

{
    "player": {
        "speed": 30,
        "lives": 3,
        "size":  50,
        "color": "#ffffff"
    },
    "speed_increase": {
        "amount":   3,
        "interval": 15
    },
    "score": {
        "increase_by": 1
    },
    "obstacle": {
        "spawn_rate": 2,
        "speed":      20,
        "size":       40,
        "color":      "#ff0000"
    },
    "coin": {
        "value":      10,
        "spawn_rate": 1,
        "color":      "#ffd700"
    },
    "powerup": {
        "value":      50,
        "spawn_rate": 0.5
    },
    "background": {
        "color": "#000000",
        "speed": 5
    },
    "difficulty": "medium",
    "audio": {
        "sound": true,
        "music": true
    },
    "variables": {
        "custom_var": 42
    }
}
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


class CodeGenerator:

    def __init__(self, tree: ProgramNode):
        self.tree   = tree
        self.config: dict = {
            "player":         {},
            "speed_increase": {},
            "score":          {},
            "obstacle":       {},
            "coin":           {},
            "powerup":        {},
            "background":     {},
            "difficulty":     None,
            "audio":          {},
            "variables":      {},
        }

    def generate(self) -> dict:
        for stmt in self.tree.statements:
            self._emit(stmt)
        self._clean()
        return self.config

    # ── dispatcher ─────────────────────────────

    def _emit(self, node: ASTNode):
        handlers = {
            PlayerSpeedNode:        self._emit_player_speed,
            PlayerLivesNode:        self._emit_player_lives,
            PlayerSizeNode:         self._emit_player_size,
            PlayerColorNode:        self._emit_player_color,
            IncreaseSpeedNode:      self._emit_increase_speed,
            IncreaseScoreNode:      self._emit_increase_score,
            ObstacleSpawnRateNode:  self._emit_obstacle_spawn_rate,
            ObstacleSpeedNode:      self._emit_obstacle_speed,
            ObstacleSizeNode:       self._emit_obstacle_size,
            ObstacleColorNode:      self._emit_obstacle_color,
            CoinValueNode:          self._emit_coin_value,
            CoinSpawnRateNode:      self._emit_coin_spawn_rate,
            CoinColorNode:          self._emit_coin_color,
            PowerupSpawnRateNode:   self._emit_powerup_spawn_rate,
            PowerupValueNode:       self._emit_powerup_value,
            BackgroundColorNode:    self._emit_background_color,
            BackgroundSpeedNode:    self._emit_background_speed,
            DifficultyNode:         self._emit_difficulty,
            SoundNode:              self._emit_sound,
            MusicNode:              self._emit_music,
            SetVarNode:             self._emit_set_var,
        }
        handler = handlers.get(type(node))
        if handler:
            handler(node)

    # ── emit methods ───────────────────────────

    def _emit_player_speed(self, n: PlayerSpeedNode):
        self.config["player"]["speed"] = n.speed

    def _emit_player_lives(self, n: PlayerLivesNode):
        self.config["player"]["lives"] = n.lives

    def _emit_player_size(self, n: PlayerSizeNode):
        self.config["player"]["size"] = n.size

    def _emit_player_color(self, n: PlayerColorNode):
        self.config["player"]["color"] = n.color

    def _emit_increase_speed(self, n: IncreaseSpeedNode):
        self.config["speed_increase"]["amount"]   = n.amount
        self.config["speed_increase"]["interval"] = n.interval

    def _emit_increase_score(self, n: IncreaseScoreNode):
        self.config["score"]["increase_by"] = n.amount

    def _emit_obstacle_spawn_rate(self, n: ObstacleSpawnRateNode):
        self.config["obstacle"]["spawn_rate"] = n.rate

    def _emit_obstacle_speed(self, n: ObstacleSpeedNode):
        self.config["obstacle"]["speed"] = n.speed

    def _emit_obstacle_size(self, n: ObstacleSizeNode):
        self.config["obstacle"]["size"] = n.size

    def _emit_obstacle_color(self, n: ObstacleColorNode):
        self.config["obstacle"]["color"] = n.color

    def _emit_coin_value(self, n: CoinValueNode):
        self.config["coin"]["value"] = n.value

    def _emit_coin_spawn_rate(self, n: CoinSpawnRateNode):
        self.config["coin"]["spawn_rate"] = n.rate

    def _emit_coin_color(self, n: CoinColorNode):
        self.config["coin"]["color"] = n.color

    def _emit_powerup_spawn_rate(self, n: PowerupSpawnRateNode):
        self.config["powerup"]["spawn_rate"] = n.rate

    def _emit_powerup_value(self, n: PowerupValueNode):
        self.config["powerup"]["value"] = n.value

    def _emit_background_color(self, n: BackgroundColorNode):
        self.config["background"]["color"] = n.color

    def _emit_background_speed(self, n: BackgroundSpeedNode):
        self.config["background"]["speed"] = n.speed

    def _emit_difficulty(self, n: DifficultyNode):
        self.config["difficulty"] = n.level

    def _emit_sound(self, n: SoundNode):
        self.config["audio"]["sound"] = n.enabled

    def _emit_music(self, n: MusicNode):
        self.config["audio"]["music"] = n.enabled

    def _emit_set_var(self, n: SetVarNode):
        self.config["variables"][n.name] = n.value

    # ── cleanup ────────────────────────────────

    def _clean(self):
        """Remove empty sub-dicts and None values for a tidy output."""
        keys_to_remove = [k for k, v in self.config.items()
                          if v == {} or v is None]
        for k in keys_to_remove:
            del self.config[k]