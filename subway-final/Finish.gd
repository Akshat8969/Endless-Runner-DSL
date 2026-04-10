extends Area3D

func _ready():
	body_entered.connect(_on_body_entered)

func _on_body_entered(body):
	if not body.is_in_group("Player"):
		return

	print("🏁 FINISH LINE REACHED!")

	if body.has_method("win_game"):
		body.win_game()
