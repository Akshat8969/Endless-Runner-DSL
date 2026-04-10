extends Area3D

func _ready():
	body_entered.connect(_on_body_entered)

func _on_body_entered(body):

	if not body.is_in_group("Player"):
		return

	print("🏁 YOU WIN!")
	print("🪙 Total Coins Collected:", body.score)

	body.velocity = Vector3.ZERO
	body.set_physics_process(false)

	get_tree().paused = true
