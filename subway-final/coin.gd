extends Area3D

@export var value := 1
var collected = false

func _ready():
	body_entered.connect(_on_body_entered)

func _on_body_entered(body):
	if collected:
		return

	if not body.is_in_group("Player"):
		return

	collected = true

	if body.has_method("add_score"):
		body.add_score(value)

	visible = false
