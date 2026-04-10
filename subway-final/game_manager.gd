extends Node

var player_name = ""
var coins = 0
var status = "playing"

func end_game(win, score):
	coins = score
	status = "win" if win else "lose"

	get_tree().paused = false
	get_tree().change_scene_to_file("res://EndScreen.tscn")
