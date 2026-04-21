extends Node

var player_name = ""
var coins = 0
var status = "menu"

# Track if the player won or lost
var is_winner = false 

# We changed the parameter to 'is_win' to match what player.gd is sending
func end_game(is_win: bool, final_score: int):
	status = "game_over"
	coins = final_score
	
	# If player.gd sends 'true', they won. If 'false', they lost!
	is_winner = is_win 
	
	# Freeze the 3D world
	get_tree().paused = true 
	
	# Load the Terminal Crash/Victory Screen
	var end_screen_scene = load("res://EndScreen.tscn").instantiate()
	get_tree().root.add_child(end_screen_scene)
