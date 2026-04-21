extends CharacterBody3D

# ========================
# SCORE SYSTEM
# ========================
var score := 0

func add_score(value):
	score += value


# ========================
# CONTROL FLAG
# ========================
var can_move = false


# ========================
# MOVEMENT SETTINGS
# ========================
var forward_speed := 30.0
var speed_increase_amount := 3
var speed_interval := 15

var gravity := 20.0
var jump_force := 8.0



# ========================
# UI REFERENCES
# ========================
# Look up to Main, down into UI, then grab the Label
@onready var countdown_label = $"../UI/CountdownLabel"


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
# TIMERS
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
	can_move = false
	
	# Play the run animation, but freeze it instantly so they look ready to sprint!
	anim.play(ANIM_RUN)
	anim.speed_scale = 0.0 
	
	load_config()
	setup_timers()
	
	# Start the 3-2-1 Go sequence
	start_countdown()

# ========================
# COUNTDOWN SEQUENCE
# ========================
func start_countdown():
	if countdown_label:
		countdown_label.show()
		# Center the pivot so the text scales from the middle
		countdown_label.pivot_offset = countdown_label.size / 2
		
		# 1. Show "Are you ready to play?" first
		countdown_label.text = "Are you ready to play?"
		countdown_label.scale = Vector2.ZERO 
		
		var ready_tween = get_tree().create_tween()
		# CHANGED: Vector2(2.0, 2.0) makes it pop to twice its normal size!
		ready_tween.tween_property(countdown_label, "scale", Vector2(0.7, 0.7), 0.5)\
			.set_trans(Tween.TRANS_ELASTIC)\
			.set_ease(Tween.EASE_OUT)
		
		# Wait 1.5 seconds so they have time to read it!
		await get_tree().create_timer(1.5).timeout 
		
		# Shrink it away quickly before the numbers start
		var shrink_tween = get_tree().create_tween()
		shrink_tween.tween_property(countdown_label, "scale", Vector2.ZERO, 0.2)\
			.set_trans(Tween.TRANS_BACK)\
			.set_ease(Tween.EASE_IN)
		await shrink_tween.finished
		
		# 2. Loop from 3 down to 1
		for i in range(3, 0, -1):
			countdown_label.text = str(i)
			countdown_label.scale = Vector2.ZERO
			
			var tween = get_tree().create_tween()
			tween.tween_property(countdown_label, "scale", Vector2(1.5, 1.5), 0.4)\
				.set_trans(Tween.TRANS_ELASTIC)\
				.set_ease(Tween.EASE_OUT)
			
			await get_tree().create_timer(1.0).timeout 
			
		# 3. Show "GO!" with a massive pop and color change
		countdown_label.text = "GO!"
		countdown_label.modulate = Color(0.2, 1.0, 0.2) # Turn it bright green
		countdown_label.scale = Vector2.ZERO
		
		var go_tween = get_tree().create_tween()
		go_tween.tween_property(countdown_label, "scale", Vector2(2.5, 2.5), 0.5)\
			.set_trans(Tween.TRANS_ELASTIC)\
			.set_ease(Tween.EASE_OUT)
		
		await get_tree().create_timer(0.6).timeout
		
		# 4. Smoothly fade the text out
		var fade_tween = get_tree().create_tween()
		fade_tween.tween_property(countdown_label, "modulate:a", 0.0, 0.2)
		await fade_tween.finished
		
		countdown_label.hide()
		
		# Reset the label back to normal for the next time they play
		countdown_label.modulate = Color.WHITE
		countdown_label.scale = Vector2.ONE
	
	else:
		print("⚠ ERROR: CountdownLabel not found! Check your node paths.")
	
	# Unlock movement and resume the running animation
	can_move = true
	anim.speed_scale = 1.2

# ========================
# TIMERS
# ========================
func setup_timers():
	speed_timer_node = Timer.new()
	speed_timer_node.wait_time = speed_interval
	speed_timer_node.timeout.connect(_on_speed_tick)
	add_child(speed_timer_node)
	speed_timer_node.start()

	reload_timer_node = Timer.new()
	reload_timer_node.wait_time = 5
	reload_timer_node.timeout.connect(_on_reload_tick)
	add_child(reload_timer_node)
	reload_timer_node.start()


func _on_speed_tick():
	if is_game_over:
		return
	forward_speed += speed_increase_amount


func _on_reload_tick():
	if is_game_over:
		return
	load_config()


# ========================
# INPUT
# ========================
func _input(event):
	if is_game_over or not can_move:
		return

	if event.is_action_pressed("ui_left"):
		current_lane = min(2, current_lane + 1)

	if event.is_action_pressed("ui_right"):
		current_lane = max(0, current_lane - 1)


# ========================
# PHYSICS
# ========================
func _physics_process(delta):
	if is_game_over or not can_move:
		return

	if not is_on_floor():
		velocity.y -= gravity * delta
	else:
		if is_jumping:
			is_jumping = false
			anim.play(ANIM_RUN)
		velocity.y = 0

	velocity.x = -forward_speed

	var target_z = lanes[current_lane]
	var direction_z = target_z - transform.origin.z
	velocity.z = direction_z * lane_speed

	if Input.is_action_just_pressed("ui_up") and is_on_floor():
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

	GameManager.end_game(false, score)


# ========================
# WIN GAME (OPTIONAL)
# ========================
func win_game():
	if is_game_over:
		return

	is_game_over = true

	print("🏁 YOU WIN!")
	print("🪙 Total Coins Collected:", score)

	stop_all()

	GameManager.end_game(true, score)


# ========================
# STOP EVERYTHING
# ========================
func stop_all():
	if speed_timer_node:
		speed_timer_node.stop()

	if reload_timer_node:
		reload_timer_node.stop()

	velocity = Vector3.ZERO
	set_physics_process(false)
	get_tree().paused = true
