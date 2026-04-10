extends CharacterBody3D

# ========================
# SCORE SYSTEM
# ========================
var score := 0

func add_score(value):
	score += value

# ========================
# MOVEMENT SETTINGS
# ========================
var forward_speed := 30.0
var speed_increase_amount := 3
var speed_interval := 15

var gravity := 20.0
var jump_force := 8.0

# ========================
# LANE SYSTEM
# ========================
var lanes = [-4.7, 0.0, 4.7]
var current_lane = 1
var lane_speed := 10.0

# ========================
# STATES
# ========================
var is_rolling := false
var is_jumping := false
var is_game_over := false

# ========================
# CONTROL FLAGS
# ========================
var initial_speed_set := false

# ========================
# TIMERS (🔥 NEW SYSTEM)
# ========================
var speed_timer_node
var reload_timer_node

# ========================
# ANIMATIONS
# ========================
const ANIM_RUN = "Armature|mixamo_com|Layer0_002"
const ANIM_JUMP = "Armature|mixamo_com|Layer0_001"
const ANIM_ROLL = "Armature|mixamo_com|Layer0"

@onready var anim = $run/AnimationPlayer

# ========================
# READY
# ========================
func _ready():
	print("🔥 READY RUNNING")

	anim.play(ANIM_RUN)
	anim.speed_scale = 1.2
	

	load_config()

	setup_timers()

# ========================
# SETUP TIMERS (🔥 KEY)
# ========================
func setup_timers():

	# SPEED TIMER
	speed_timer_node = Timer.new()
	speed_timer_node.wait_time = speed_interval
	speed_timer_node.one_shot = false
	speed_timer_node.timeout.connect(_on_speed_tick)
	add_child(speed_timer_node)
	speed_timer_node.start()

	# RELOAD TIMER
	reload_timer_node = Timer.new()
	reload_timer_node.wait_time = 5
	reload_timer_node.one_shot = false
	reload_timer_node.timeout.connect(_on_reload_tick)
	add_child(reload_timer_node)
	reload_timer_node.start()

	print("🔥 TIMERS STARTED")

# ========================
# TIMER CALLBACKS
# ========================
func _on_speed_tick():
	if is_game_over:
		return
	
	forward_speed += speed_increase_amount
	print("🚀 Speed:", forward_speed)

func _on_reload_tick():
	if is_game_over:
		return
	
	load_config()

# ========================
# INPUT
# ========================
func _input(event):
	if is_game_over:
		return

	if event.is_action_pressed("ui_left"):
		current_lane = min(2, current_lane + 1)

	if event.is_action_pressed("ui_right"):
		current_lane = max(0, current_lane - 1)

# ========================
# PHYSICS
# ========================
func _physics_process(delta):

	if is_game_over:
		return

	if not is_on_floor():
		velocity.y -= gravity * delta
	else:
		if is_jumping:
			is_jumping = false
			if not is_rolling:
				anim.play(ANIM_RUN)
		velocity.y = 0

	velocity.x = -forward_speed

	var target_z = lanes[current_lane]
	var direction_z = target_z - transform.origin.z
	velocity.z = direction_z * lane_speed

	if Input.is_action_just_pressed("ui_up") and is_on_floor() and not is_rolling:
		velocity.y = jump_force
		is_jumping = true
		anim.play(ANIM_JUMP)

	move_and_slide()
	check_collision()

# ========================
# LOAD CONFIG
# ========================
func load_config():
	var path = "res://game_config.json"

	if not FileAccess.file_exists(path):
		return

	var file = FileAccess.open(path, FileAccess.READ)
	var data = JSON.parse_string(file.get_as_text())

	if data == null:
		return

	if "speed" in data and not initial_speed_set:
		forward_speed = data["speed"]
		initial_speed_set = true

	if "speed_increase" in data:
		var si = data["speed_increase"]

		if "amount" in si:
			speed_increase_amount = si["amount"]

		if "interval" in si:
			speed_interval = si["interval"]

# ========================
# COLLISION
# ========================
func check_collision():
	for i in range(get_slide_collision_count()):
		var collision = get_slide_collision(i)
		var obj = collision.get_collider()

		if obj:
			if obj.is_in_group("obstacle") or obj.is_in_group("train"):
				game_over()

# ========================
# GAME OVER
# ========================
func game_over():
	if is_game_over:
		return

	is_game_over = true

	print("💀 GAME OVER")
	print("🪙 Total Coins Collected:", score)

	stop_all()

# ========================
# WIN GAME
# ========================
func win_game():
	if is_game_over:
		return

	is_game_over = true

	print("🏁 YOU WIN!")
	print("🪙 Total Coins Collected:", score)

	stop_all()

# ========================
# STOP EVERYTHING (🔥 FINAL FIX)
# ========================
func stop_all():
	if speed_timer_node:
		speed_timer_node.stop()

	if reload_timer_node:
		reload_timer_node.stop()

	velocity = Vector3.ZERO
	set_physics_process(false)
	get_tree().paused = true
