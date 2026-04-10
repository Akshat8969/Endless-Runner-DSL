extends Control

func _ready():
	var name = GameManager.player_name
	var coins = GameManager.coins
	var status = GameManager.status

	if status == "win":
		$VBoxContainer/ResultText.text = "🏆 Well played, " + name + "!"
	else:
		$VBoxContainer/ResultText.text = "💀 Better luck next time, " + name + "!"

	$VBoxContainer/CoinsText.text = "Coins: " + str(coins)

func _on_RestartButton_pressed():
	get_tree().change_scene_to_file("res://StartScreen.tscn")
