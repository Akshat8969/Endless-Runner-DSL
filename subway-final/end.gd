extends Control

@onready var result_text = $VBoxContainer/ResultText
@onready var coins_text = $VBoxContainer/CoinsText
@onready var restart_button = $VBoxContainer/RestartButton

var crash_log = ""

func _ready():
	restart_button.hide()
	coins_text.hide()
	result_text.text = ""
	
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
	
	# ==========================================
	# CHECK IF WE WON OR LOST
	# ==========================================
	if GameManager.is_winner:
		# --- THE VICTORY TEXT ---
		crash_log = "MISSION ACCOMPLISHED\n"
		crash_log += "=====================================\n\n"
		crash_log += "DUMPING SESSION DATA:\n"
		crash_log += "{\n"
		crash_log += '  "pilot_id": "' + GameManager.player_name.to_upper() + '",\n'
		crash_log += '  "status": "SUCCESS",\n'
		crash_log += '  "objective": "COMPLETE"\n'
		crash_log += "}\n\n"
		crash_log += "CONGRATULATIONS. AWAITING NEXT COMMAND...\n"
		
		coins_text.text = "> COINS EARNED: " + str(GameManager.coins)
		restart_button.text = "> PLAY AGAIN"
		
		# Turn the text bright cyan for a win
		result_text.modulate = Color(0.2, 1.0, 1.0)
		coins_text.modulate = Color(0.2, 1.0, 1.0)
		restart_button.modulate = Color(0.2, 1.0, 1.0)
		
	else:
		# --- THE CRASH TEXT ---
		crash_log = "FATAL EXCEPTION: COLLISION_DETECTED\n"
		crash_log += "=====================================\n\n"
		crash_log += "DUMPING SESSION DATA:\n"
		crash_log += "{\n"
		crash_log += '  "pilot_id": "' + GameManager.player_name.to_upper() + '",\n'
		crash_log += '  "status": "TERMINATED"\n'
		crash_log += "}\n\n"
		crash_log += "SYSTEM HALTED. AWAITING USER INPUT...\n"
		
		coins_text.text = "> COINS RECOVERED: " + str(GameManager.coins)
		restart_button.text = "> REBOOT_SYSTEM"
		
		# Keep the text standard terminal green
		result_text.modulate = Color(0.2, 1.0, 0.2)
		coins_text.modulate = Color(0.2, 1.0, 0.2)
		restart_button.modulate = Color(0.2, 1.0, 0.2)

	
	# Start the typewriter effect
	print_terminal()

func print_terminal():
	for i in range(crash_log.length()):
		result_text.text += crash_log[i]
		await get_tree().create_timer(0.02).timeout
		
	await get_tree().create_timer(0.5).timeout
	coins_text.show()
	restart_button.show()

# ========================
# BUTTON SIGNALS
# ========================
func _on_restart_button_pressed():
	if GameManager.is_winner:
		GameManager.coins = 0
		GameManager.status = "playing"
		get_tree().paused = false
		get_tree().change_scene_to_file("res://main.tscn")
		queue_free()
	else:
		# We just quit the game. The web browser is watching for this!
		get_tree().quit()
