extends Control

# -------------------------
# UI REFERENCES
# -------------------------
@onready var name_input = $VBoxContainer/NameInput
@onready var error_text = $VBoxContainer/ErrorText
@onready var start_button = $VBoxContainer/StartButton
@onready var preview = $VBoxContainer/PreviewLabel

@onready var bg = $TextureRect
@onready var fade = $FadeRect

@onready var click_sound = $ClickSound
@onready var hover_sound = $HoverSound


# -------------------------
# BACKGROUND MOTION
# -------------------------
var speed = 15.0
var direction = 1
var limit = 60


# -------------------------
# READY
# -------------------------

func _ready():
	name_input.text = ""
	error_text.text = ""
	fade.modulate.a = 0   # invisible at start

	# --- NEW CODE: ADD "BLEED ROOM" FOR PANNING ---
	# Make the background 10% larger so we don't see the edges when it moves
	bg.scale = Vector2(1.1, 1.1)
	
	# Center the pivot point so it scales out equally in all directions
	bg.pivot_offset = bg.size / 2
# -------------------------
# BACKGROUND ANIMATION
# -------------------------
func _process(delta):
	bg.position.x += speed * direction * delta

	if bg.position.x > limit:
		direction = -1
	elif bg.position.x < -limit:
		direction = 1


# -------------------------
# START BUTTON LOGIC
# -------------------------
func _on_StartButton_pressed():
	click_sound.play()

	var player_name = name_input.text.strip_edges()

	# validation
	if player_name == "":
		error_text.text = "⚠ Enter your name!"
		await shake()
		name_input.grab_focus()
		return

	if player_name.length() < 2:
		error_text.text = "⚠ Name too short!"
		await shake()
		name_input.grab_focus()
		return

	# save data
	GameManager.player_name = player_name
	GameManager.coins = 0
	GameManager.status = "playing"

	# UI feedback
	start_button.disabled = true

	# loading animation
	for i in range(6):
		var dots = ""

		for j in range(i % 4):
			dots += "."

		start_button.text = "Loading" + dots
	await get_tree().create_timer(0.3).timeout

	# fade out
	await fade_out()

	# change scene
	get_tree().change_scene_to_file("res://main.tscn")


# -------------------------
# BUTTON HOVER EFFECT
# -------------------------
func _on_StartButton_mouse_entered():
	start_button.scale = Vector2(1.1, 1.1)
	hover_sound.play()

func _on_StartButton_mouse_exited():
	start_button.scale = Vector2(1, 1)


# -------------------------
# INPUT HANDLING
# -------------------------
func _on_NameInput_text_changed(new_text):
	error_text.text = ""
	preview.text = "Hello, " + new_text


func _on_NameInput_focus_entered():
	name_input.modulate = Color(1, 1, 1)

func _on_NameInput_focus_exited():
	name_input.modulate = Color(0.8, 0.8, 0.8)


# -------------------------
# FADE TRANSITION
# -------------------------
func fade_out():
	for i in range(25):
		fade.modulate.a += 0.04
		await get_tree().create_timer(0.03).timeout


# -------------------------
# SHAKE EFFECT
# -------------------------
func shake():
	for i in range(6):
		position.x += 5
		await get_tree().create_timer(0.02).timeout
		position.x -= 5
