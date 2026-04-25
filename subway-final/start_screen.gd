extends Control

# -------------------------
# UI REFERENCES
# -------------------------
@onready var name_input   = $VBoxContainer/NameInput   if has_node("VBoxContainer/NameInput")   else null
@onready var error_text   = $VBoxContainer/ErrorText   if has_node("VBoxContainer/ErrorText")   else null
@onready var start_button = $VBoxContainer/StartButton if has_node("VBoxContainer/StartButton") else null
@onready var preview      = $VBoxContainer/PreviewLabel if has_node("VBoxContainer/PreviewLabel") else null
@onready var prompt_label = $VBoxContainer/PromptLabel  if has_node("VBoxContainer/PromptLabel")  else null

@onready var bg   = $TextureRect if has_node("TextureRect") else null
@onready var fade = $FadeRect    if has_node("FadeRect")    else null

@onready var click_sound = $ClickSound if has_node("ClickSound") else null
@onready var hover_sound = $HoverSound if has_node("HoverSound") else null

# -------------------------
# BACKGROUND MOTION
# -------------------------
var speed     = 15.0
var direction = 1
var limit     = 60

# -------------------------
# STATE
# -------------------------
var _waiting_for_enter := true   # true = showing "press enter", false = fading out


# -------------------------
# READY
# -------------------------
func _ready():
	# ── Hide / disable name-entry UI ──────────────────────────────────────
	if name_input:
		name_input.hide()
	if error_text:
		error_text.hide()
	if start_button:
		start_button.hide()
	if preview:
		preview.hide()

	# ── Fade rect starts invisible ────────────────────────────────────────
	if fade:
		fade.modulate.a = 0

	# ── Read player name from game_config.json ────────────────────────────
	_load_player_name()

	# ── Show "PRESS ENTER TO START" centered ─────────────────────────────
	var label_to_use = prompt_label if prompt_label else null
	if label_to_use == null and preview:
		preview.show()
		label_to_use = preview

	if label_to_use:
		label_to_use.text = "PRESS ENTER TO START"
		# ── CENTER the text ───────────────────────────────────────────────
		label_to_use.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		# Make the label span the full screen width so centering is visible
		label_to_use.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		label_to_use.grow_horizontal = Control.GROW_DIRECTION_BOTH

	# ── Background scaling ────────────────────────────────────────────────
	if bg:
		bg.scale        = Vector2(1.1, 1.1)
		bg.pivot_offset = bg.size / 2


# -------------------------
# LOAD NAME FROM JSON / WEB
# -------------------------
func _load_player_name():
	# 1. First, try to grab the name from the Web Browser's LocalStorage!
	if OS.has_feature("web"):
		var js_name = JavaScriptBridge.eval("window.localStorage.getItem('dsl_user_name')")
		if js_name and typeof(js_name) == TYPE_STRING and js_name.strip_edges() != "":
			GameManager.player_name = js_name.strip_edges()
			print("▶ Player name loaded from Web: ", GameManager.player_name)
			return

	# 2. Use the absolute filesystem path so Godot never reads a stale cached copy
	#    ProjectSettings.globalize_path("res://") gives the real folder on disk.
	var project_dir = ProjectSettings.globalize_path("res://")
	var abs_path    = project_dir.path_join("game_config.json")

	print("▶ Trying to load config from: ", abs_path)

	var file = FileAccess.open(abs_path, FileAccess.READ)

	# 3. Fallback to the virtual res:// path (works in most debug builds)
	if file == null:
		print("▶ Absolute path failed, trying res://game_config.json …")
		file = FileAccess.open("res://game_config.json", FileAccess.READ)

	if file == null:
		push_warning("start_screen.gd: could not open game_config.json from any path")
		GameManager.player_name = "Player"
		return

	var json_text = file.get_as_text()
	file.close()

	print("▶ Raw JSON read: ", json_text.left(200))   # print first 200 chars for debugging

	var parsed = JSON.parse_string(json_text)
	if parsed == null or typeof(parsed) != TYPE_DICTIONARY:
		push_warning("start_screen.gd: failed to parse game_config.json")
		GameManager.player_name = "Player"
		return

	var name_val = parsed.get("player_name", "")
	print("▶ player_name key in JSON: '", name_val, "'")

	if typeof(name_val) == TYPE_STRING and name_val.strip_edges() != "":
		GameManager.player_name = name_val.strip_edges()
	else:
		GameManager.player_name = name_val.strip_edges()

	print("▶ Final GameManager.player_name = ", GameManager.player_name)


# -------------------------
# BACKGROUND ANIMATION
# -------------------------
func _process(delta):
	if bg:
		bg.position.x += speed * direction * delta
		if bg.position.x > limit:
			direction = -1
		elif bg.position.x < -limit:
			direction = 1


# -------------------------
# INPUT — ENTER TO START
# -------------------------
func _input(event):
	if not _waiting_for_enter:
		return

	var pressed_enter = (
		(event is InputEventKey and event.pressed and
		 (event.keycode == KEY_ENTER or event.keycode == KEY_KP_ENTER))
	)

	if pressed_enter:
		_waiting_for_enter = false
		_start_game()


# -------------------------
# START GAME
# -------------------------
func _start_game():
	if click_sound:
		click_sound.play()

	# Set game state
	GameManager.coins  = 0
	GameManager.status = "playing"

	# Update prompt
	if prompt_label:
		prompt_label.text = "LOADING..."
	elif preview:
		preview.text = "LOADING..."

	# Fade out then switch scene
	await fade_out()
	get_tree().change_scene_to_file("res://main.tscn")


# -------------------------
# FADE TRANSITION
# -------------------------
func fade_out():
	if fade == null:
		return
	for i in range(25):
		fade.modulate.a += 0.04
		await get_tree().create_timer(0.03).timeout


# -------------------------
# SHAKE EFFECT (kept for potential reuse)
# -------------------------
func shake():
	for i in range(6):
		position.x += 5
		await get_tree().create_timer(0.02).timeout
		position.x -= 5
