extends Control

func _on_StartButton_pressed():
	var name = $VBoxContainer/NameInput.text.strip_edges()

	if name == "":
		$VBoxContainer/ErrorText.text = "⚠ Name required!"
		return

	# ✅ SAVE NAME
	GameManager.player_name = name

	# ✅ RESET DATA (important)
	GameManager.coins = 0
	GameManager.status = "playing"

	# ✅ GO TO GAME
	get_tree().change_scene_to_file("res://main.tscn")
