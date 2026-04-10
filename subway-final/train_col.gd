extends Area3D

func _ready():
	body_entered.connect(_on_body_entered)

func _on_body_entered(body):
	if body.is_in_group("Player"):
		print("PLAYER HIT TRAIN")

		if body.has_method("game_over"):
			body.game_over()
