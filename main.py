"""
FitForge - Full Body Workout App
Mobile workout tracker with rest timers, audio cues, progress tracking, and exercise instructions.
Built with Kivy for Android/iOS deployment.
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.utils import get_color_from_hex
from kivy.core.audio import SoundLoader  # reserved for future audio cues
from kivy.metrics import dp, sp
from kivy.properties import StringProperty
import json
import os
import datetime

# ─────────────────────────────────────────────
# THEME
# ─────────────────────────────────────────────
COLORS = {
    'bg':           '#0D0F14',
    'surface':      '#161A24',
    'surface2':     '#1E2433',
    'accent':       '#E8FF47',
    'accent2':      '#47FFD4',
    'danger':       '#FF4757',
    'text':         '#F0F4FF',
    'text_dim':     '#7A8599',
    'card':         '#1A1F2E',
    'success':      '#2ECC71',
}

def c(key):
    return get_color_from_hex(COLORS[key])

# ─────────────────────────────────────────────
# WORKOUT DATA
# ─────────────────────────────────────────────
WORKOUT_PLAN = {
    "Day 1": {
        "name": "Push + Core",
        "emoji": "",
        "color": "#E8FF47",
        "warmup": [
            {"name": "Jump Rope", "duration": 300, "type": "timed",
             "instruction": "Easy pace, focus on rhythm. Land softly on the balls of your feet. Keep elbows close to your sides. This gets your heart rate up and primes the whole body."},
            {"name": "Arm Circles — Forward", "duration": 30, "type": "timed",
             "instruction": "Arms straight out to the sides, make big slow forward circles. Progressively increase the circle size. Opens the shoulder joint before pressing work."},
            {"name": "Arm Circles — Backward", "duration": 30, "type": "timed",
             "instruction": "Same motion, reverse direction. You'll feel the rear deltoid and rotator cuff engage. Keep your neck relaxed."},
            {"name": "Hip Circles", "reps": "10 each direction", "type": "reps",
             "instruction": "Hands on hips, feet shoulder-width. Make big slow circles with your hips. Forward 10, then backward 10. Loosens the hip flexors and lower back."},
            {"name": "Walkouts", "reps": "5 reps", "type": "reps",
             "instruction": "Stand tall, hinge forward at the hips, walk your hands out to a plank position, hold 2 seconds, walk back and stand. Warms up shoulders, hamstrings, and core all at once."},
            {"name": "Lateral Lunges", "reps": "10 per side", "type": "reps",
             "instruction": "Step wide to the side, sink your hips down, reach the opposite arm across toward your foot. Hold 1 second at the bottom. Opens the groin and hip flexors."},
            {"name": "Shoulder Rotations (Band)", "reps": "10 per direction", "type": "reps",
             "instruction": "Hold a light resistance band wide with both hands, arms straight. Bring it overhead and behind your back if mobility allows. Reverse the motion. Directly primes the shoulder for pressing."},
            {"name": "Push-Up Plank Hold", "duration": 20, "type": "timed",
             "instruction": "Get into push-up position on the rotating handles or floor and simply hold. Straight line from head to heels, core tight, glutes squeezed. Activates everything before your first working set."},
        ],
        "exercises": [
            {"name": "Single-Arm Floor Press", "sets": 3, "reps": "8–12 per side", "weight": "25 or 35 lb",
             "rest": 60,
             "instruction": "Lie on your back, press one arm at a time. Brace your core — the uneven load forces anti-rotation work. Drive through your chest, not your shoulder."},
            {"name": "Rotating Push-Up Handles", "sets": 3, "reps": "10–15", "weight": "Bodyweight",
             "rest": 60,
             "instruction": "Let the handles rotate naturally as you push up. This reduces wrist strain and deepens chest activation. Keep your body in a straight plank line."},
            {"name": "Single-Arm Shoulder Press", "sets": 3, "reps": "8–10 per side", "weight": "25 lb",
             "rest": 60,
             "instruction": "Stand or sit. Brace your core hard to resist leaning to the side. Press straight up, don't flare the elbow out too wide."},
            {"name": "Alternating Lateral Raises", "sets": 3, "reps": "12–15 per side", "weight": "5–10 lb",
             "rest": 45,
             "instruction": "Slight bend in the elbow, raise to shoulder height only. Don't shrug. These add up fast — lighter is smarter here."},
            {"name": "Band Tricep Pushdowns", "sets": 3, "reps": "15", "weight": "Medium band",
             "rest": 45,
             "instruction": "Anchor band overhead. Keep elbows pinned to your sides and push down until arms are fully extended. Squeeze at the bottom."},
            {"name": "Single-Arm Overhead Tricep Extension", "sets": 3, "reps": "10–12 per side", "weight": "25 lb",
             "rest": 45,
             "instruction": "Hold dumbbell overhead, lower behind your head by bending the elbow. Keep upper arm still and vertical. Extend back up fully."},
            {"name": "Plank", "sets": 3, "reps": "45 sec", "weight": "Bodyweight",
             "rest": 30, "type": "timed", "duration": 45,
             "instruction": "Forearms or hands. Keep hips level — don't let them sag or pike up. Squeeze glutes and abs throughout."},
            {"name": "Dead Bugs", "sets": 3, "reps": "10 per side", "weight": "Bodyweight",
             "rest": 30,
             "instruction": "Lying on back, arms up, knees at 90°. Lower opposite arm and leg slowly while pressing lower back into the floor. Exhale as you lower."},
            {"name": "Bicycle Crunches", "sets": 3, "reps": "20", "weight": "Bodyweight",
             "rest": 30,
             "instruction": "Slow and controlled — don't rush. Rotate your shoulder toward the knee, not just your elbow. Keep lower back pressed down."},
        ]
    },
    "Day 2": {
        "name": "Pull + Biceps",
        "emoji": "",
        "color": "#47FFD4",
        "warmup": [
            {"name": "Jump Rope", "duration": 120, "type": "timed",
             "instruction": "Easy pace to get blood flowing. Focus on relaxed shoulders and light landings. 2 minutes is enough to prime the system before pull work."},
            {"name": "Arm Circles — Forward", "duration": 30, "type": "timed",
             "instruction": "Big slow forward circles with straight arms. Opens the shoulder capsule and rotator cuff — essential before pulling movements."},
            {"name": "Arm Circles — Backward", "duration": 30, "type": "timed",
             "instruction": "Reverse direction. The backward motion specifically targets the rear deltoids and external rotators you'll be using heavily today."},
            {"name": "Band Pull-Aparts", "reps": "20 reps", "type": "reps",
             "instruction": "Hold a light band at chest width, arms straight. Pull apart until band touches your chest, squeezing shoulder blades together. Controlled return. This is your single best pre-pull warm-up movement."},
            {"name": "Hip Circles", "reps": "10 each direction", "type": "reps",
             "instruction": "Hands on hips, big slow circles in both directions. Loosens up the hip joint and lower back before the bent-over rowing position."},
            {"name": "Dead Hang — Short", "duration": 15, "type": "timed",
             "instruction": "Jump up and simply hang from the pull-up bar for 15 seconds. Let your shoulders decompress and your grip wake up. This is your activation set before the real pull-up work."},
            {"name": "Scapular Pull-Ups", "reps": "8 reps", "type": "reps",
             "instruction": "Hang from the bar with straight arms. Without bending your elbows, retract your shoulder blades — you'll rise just a couple inches. Lower back down. This isolates the lat activation you need for full pull-ups."},
            {"name": "Walkouts", "reps": "5 reps", "type": "reps",
             "instruction": "Hinge forward, walk hands to plank, hold 2 seconds, walk back. Warms up the posterior chain — hamstrings and lower back — which get loaded during bent-over rows."},
        ],
        "exercises": [
            {"name": "Pull-Ups", "sets": 3, "reps": "6–10", "weight": "Assisted or Bodyweight",
             "rest": 90,
             "instruction": "Use a resistance band looped over the bar for assistance. Full dead hang at the bottom, chin over bar at the top. Don't kip — strict reps only for now."},
            {"name": "Single-Arm Bent-Over Row", "sets": 3, "reps": "10–12 per side", "weight": "35 lb",
             "rest": 60,
             "instruction": "Brace one hand on a chair or bench. Keep your back flat and parallel to the floor. Drive your elbow back, not up. Squeeze at the top."},
            {"name": "Band Face Pulls", "sets": 3, "reps": "15", "weight": "Light-Medium band",
             "rest": 45,
             "instruction": "Anchor band at face height. Pull toward your forehead, elbows flaring up and out. This is your most important posture exercise — don't skip it."},
            {"name": "Band Pull-Aparts", "sets": 3, "reps": "20", "weight": "Light band",
             "rest": 30,
             "instruction": "Start at chest width, pull until band touches chest. Controlled return. Rear delts and upper back."},
            {"name": "Alternating Dumbbell Curls", "sets": 3, "reps": "10–12 per side", "weight": "25 lb",
             "rest": 45,
             "instruction": "Supinate (rotate) the wrist as you curl up. Don't swing — keep upper arms pinned to your sides. Full extension at the bottom."},
            {"name": "Alternating Hammer Curls", "sets": 3, "reps": "10 per side", "weight": "25 lb",
             "rest": 45,
             "instruction": "Neutral grip (thumbs up). Targets the brachialis — the muscle under the bicep that adds width. Same strict form as curls."},
            {"name": "Dead Hangs", "sets": 3, "reps": "20–30 sec", "weight": "Bodyweight",
             "rest": 45, "type": "timed", "duration": 25,
             "instruction": "Full grip on the bar, let your body hang completely. Builds grip strength and decompresses your spine. Breathe slowly."},
        ]
    },
    "Day 3": {
        "name": "Legs + Glutes",
        "emoji": "",
        "color": "#FF6B9D",
        "warmup": [
            {"name": "Jump Rope", "duration": 120, "type": "timed",
             "instruction": "2 minutes easy. Warms up the ankles and calves specifically, which take a beating in squats and lunges. Land softly and rhythmically."},
            {"name": "Leg Swings — Forward & Back", "reps": "10 per leg", "type": "reps",
             "instruction": "Hold a wall for balance. Swing one leg forward and back like a pendulum, gradually increasing the range. 10 reps per leg. Loosens the hip flexor and hamstring."},
            {"name": "Leg Swings — Side to Side", "reps": "10 per leg", "type": "reps",
             "instruction": "Same wall hold. Swing the leg across your body and out to the side. 10 reps per leg. Targets the adductors and outer hip — both get loaded during lateral movements."},
            {"name": "Hip Circles", "reps": "10 each direction", "type": "reps",
             "instruction": "Hands on hips, feet wide, big slow circles. Forward 10, backward 10. Opens the hip joint specifically before the goblet squat and RDL loading."},
            {"name": "Lateral Lunges", "reps": "10 per side", "type": "reps",
             "instruction": "Bodyweight only, no weight. Sink as deep as you can and hold 1 second at the bottom. The adductor stretch here is your best prep for the goblet squat depth you'll need."},
            {"name": "Glute Bridges — Bodyweight", "reps": "15 reps", "type": "reps",
             "instruction": "No weights yet. Lie on back, feet flat, drive hips up and squeeze glutes hard at the top. This is a glute activation warm-up — if your glutes don't fire properly, your lower back takes the load instead."},
            {"name": "Bodyweight Squat", "reps": "10 reps", "type": "reps",
             "instruction": "Feet shoulder-width, toes slightly out. Full depth, chest tall, knees tracking over toes. These are pure movement prep — slow and controlled, pausing 1 second at the bottom to open the ankle and hip."},
            {"name": "Hip Flexor Stretch", "duration": 20, "type": "timed",
             "instruction": "Kneel on one knee, the other foot forward. Push your hips gently forward until you feel a stretch in the front of the back-leg hip. Hold 20 seconds per side. Tight hip flexors are the number one reason squats go wrong."},
        ],
        "exercises": [
            {"name": "Goblet Squat", "sets": 3, "reps": "12–15", "weight": "35 lb",
             "rest": 60,
             "instruction": "Hold dumbbell at chest height in both hands. Feet shoulder-width, toes slightly out. Squat deep, keeping chest tall. Drive knees out over toes."},
            {"name": "Single-Leg Romanian Deadlift", "sets": 3, "reps": "8–10 per side", "weight": "35 lb",
             "rest": 60,
             "instruction": "Hold dumbbell in opposite hand to working leg. Hinge at the hip, let the free leg trail back. Keep back flat. Feel the hamstring stretch at the bottom."},
            {"name": "Reverse Lunges (Weight Vest)", "sets": 3, "reps": "12 per leg", "weight": "Weight vest",
             "rest": 60,
             "instruction": "Step back, lower the back knee toward the floor. Keep front shin vertical. Drive through the front heel to return. Control the descent."},
            {"name": "Glute Bridges (Leg Weights)", "sets": 3, "reps": "20", "weight": "Leg weights",
             "rest": 45,
             "instruction": "Lie on back, feet flat, leg weights strapped on. Drive hips up by squeezing glutes hard. Hold at top for 1 second. Lower slowly."},
            {"name": "Donkey Kicks (Leg Weights)", "sets": 3, "reps": "15 per side", "weight": "Leg weights",
             "rest": 30,
             "instruction": "On all fours. Keep the 90° bend in your knee and kick straight up toward the ceiling. Squeeze the glute at the top. Hips stay level."},
            {"name": "Banded Lateral Walks", "sets": 3, "reps": "15 steps each way", "weight": "Medium band",
             "rest": 30,
             "instruction": "Band around thighs just above knees. Slight squat position, stay low throughout. Step side to side maintaining tension in the band. Burns the outer glute (gluteus medius)."},
            {"name": "Jump Rope Intervals", "sets": 5, "reps": "30s on / 15s off", "weight": "Bodyweight",
             "rest": 15, "type": "timed", "duration": 30,
             "instruction": "Push the pace here. This is conditioning. Breathe rhythmically and try to maintain form even when tired."},
        ]
    },
    "Day 4": {
        "name": "Full Body + Conditioning",
        "emoji": "",
        "color": "#FF8C42",
        "warmup": [
            {"name": "Jump Rope", "duration": 180, "type": "timed",
             "instruction": "3 minutes — start easy and build pace in the last minute. Today is your highest intensity day so this warm-up matters more than any other. Don't skip a second of it."},
            {"name": "Arm Circles — Forward", "duration": 30, "type": "timed",
             "instruction": "Big forward circles, progressively wider. Today hits chest, back, and shoulders all in the same session — this opens everything at once."},
            {"name": "Arm Circles — Backward", "duration": 30, "type": "timed",
             "instruction": "Reverse direction. Pay attention to any shoulder tightness — today's pressing and pulling in the same circuit puts extra demand on the joint."},
            {"name": "Hip Circles", "reps": "10 each direction", "type": "reps",
             "instruction": "Hands on hips, big slow circles both ways. Full body day means full body warm-up — the hips are the hinge of everything."},
            {"name": "Walkouts", "reps": "5 reps", "type": "reps",
             "instruction": "Slow and deliberate. This one movement warms up shoulders, hamstrings, and core simultaneously — perfect for a day that hits all three. Pause 2 seconds in the plank."},
            {"name": "Lateral Lunges", "reps": "10 per side", "type": "reps",
             "instruction": "Get the hips and adductors ready. Reach the opposite arm across as you lunge. Today's circuit is relentless — walk in ready."},
            {"name": "Bodyweight Squat", "reps": "10 reps", "type": "reps",
             "instruction": "Full depth, slow, controlled. These prime the pattern you'll use in the dumbbell thrusters. Focus on sitting back into the squat, not just bending your knees."},
            {"name": "Push-Up Plank Hold", "duration": 20, "type": "timed",
             "instruction": "Final activation before the circuit begins. Straight plank position, core braced hard, breathe steadily. You are about to work — this is your last moment of stillness."},
        ],
        "exercises": [
            {"name": "Rotating Push-Up Handles", "sets": 4, "reps": "10", "weight": "Bodyweight",
             "rest": 15,
             "instruction": "CIRCUIT — minimal rest between exercises, 60s rest between rounds. Keep your plank tight and let handles rotate freely."},
            {"name": "Chin-Ups", "sets": 4, "reps": "8", "weight": "Assisted or Bodyweight",
             "rest": 15,
             "instruction": "Underhand grip (easier than pull-ups). Full range of motion. Use band assist if needed to complete all reps with good form."},
            {"name": "Single-Arm Dumbbell Thrusters", "sets": 4, "reps": "5 per side", "weight": "25 lb",
             "rest": 15,
             "instruction": "Squat to press combined. Hold dumbbell at shoulder, squat down, drive up and press overhead in one fluid motion. Alternate sides each rep."},
            {"name": "Single-Leg Romanian Deadlift", "sets": 4, "reps": "5 per side", "weight": "35 lb",
             "rest": 15,
             "instruction": "Keep it controlled even in the circuit. Quality over speed on this one — it's a balance and hinge movement."},
            {"name": "Glute Bridges (Leg Weights)", "sets": 4, "reps": "15", "weight": "Leg weights",
             "rest": 15,
             "instruction": "Squeeze and hold 1 second at the top of every rep. Even in a circuit, make these count."},
            {"name": "Jump Rope", "sets": 4, "reps": "30 seconds", "weight": "Bodyweight",
             "rest": 60, "type": "timed", "duration": 30,
             "instruction": "This is your round finisher. Push hard. After this, rest 60 seconds and start the next round from Push-Ups."},
        ]
    },
}

REST_DAY_STRETCHING = [
    {"name": "Chest Doorway Stretch", "duration": 60, "sides": True,
     "instruction": "Forearm on doorframe at 90°. Gently lean through. Hold 60s per side. Critical after pressing days."},
    {"name": "Cross-Body Shoulder Stretch", "duration": 45, "sides": True,
     "instruction": "Pull arm across chest with opposite hand. Keep shoulder down. Feel the rear deltoid and upper back open up."},
    {"name": "Lat Stretch", "duration": 45, "sides": False,
     "instruction": "Grab pull-up bar or doorframe, hinge hips back. Let upper back open completely. Breathe into the stretch."},
    {"name": "Thread the Needle", "duration": 45, "sides": True,
     "instruction": "On all fours, slide one arm under your body along the floor. Rotate your upper back. Targets thoracic spine and rear shoulder."},
    {"name": "Neck Stretch", "duration": 30, "sides": True,
     "instruction": "Drop one ear toward shoulder. Then look down toward your armpit for a different angle. Never force — just let gravity do the work."},
    {"name": "Pigeon Pose", "duration": 90, "sides": True,
     "instruction": "From plank, bring one knee forward toward your wrist. Let shin rest diagonally. Sink hips down. 90 seconds per side — your most important stretch."},
    {"name": "Lying Hamstring Stretch (Band)", "duration": 45, "sides": True,
     "instruction": "Loop resistance band around foot. Lie on back, keep leg straight, gently pull toward you. Don't force — breathe and let the muscle release."},
    {"name": "Butterfly Stretch", "duration": 60, "sides": False,
     "instruction": "Soles of feet together, press knees toward floor, hinge forward at the hips. Opens the inner groin and hips."},
    {"name": "Child's Pose", "duration": 90, "sides": False,
     "instruction": "Arms extended or alongside body. Focus on your lower back decompressing. Breathe deeply — exhale and sink further each breath."},
    {"name": "Supine Spinal Twist", "duration": 45, "sides": True,
     "instruction": "On your back, bring one knee across your body, look the opposite direction. Feel the rotation through your entire spine."},
]

PROGRESS_FILE = "workout_progress.json"
EQUIPMENT_FILE = "equipment.json"

APP_VERSION = "1.3.0"
CHANGELOG = [
    {
        "version": "1.3.0",
        "date": "Feb 2026",
        "changes": [
            "Expanded equipment library to 60+ items covering every training environment",
            "Added location presets (Home, Gym, Park, Hotel, Travel, Office)",
            "Added app menu with exit, version info, and changelog",
            "Equipment screen now grouped and scrollable with preset quick-load",
        ]
    },
    {
        "version": "1.2.0",
        "date": "Feb 2026",
        "changes": [
            "Full equipment system — exercises auto-adapt to what you own",
            "13 exercise types each with 4–6 variations from full equipment to bodyweight",
            "Equipment saved to disk and loaded on every workout start",
        ]
    },
    {
        "version": "1.1.0",
        "date": "Feb 2026",
        "changes": [
            "Expanded warmup routines — 8 movements per day, specifically chosen per workout",
            "Warmup complete transition screen before workout begins",
            "Start / Pause / Stop workout controls with confirmation dialog",
            "Rest timers auto-start between sets with restart button",
        ]
    },
    {
        "version": "1.0.0",
        "date": "Feb 2026",
        "changes": [
            "Initial release with 4-day workout split + rest day stretching",
            "Exercise instructions for every movement",
            "Workout progress tracking with streak counter",
            "Dark theme UI with per-day accent colours",
        ]
    },
]

# ─────────────────────────────────────────────
# EQUIPMENT SYSTEM
# ─────────────────────────────────────────────

ALL_EQUIPMENT = {
    # ── CARDIO ──
    "jump_rope":          {"label": "Jump Rope",                "emoji": "-", "group": "Cardio"},
    "treadmill":          {"label": "Treadmill",                "emoji": "-", "group": "Cardio"},
    "stationary_bike":    {"label": "Stationary Bike",          "emoji": "-", "group": "Cardio"},
    "rowing_machine":     {"label": "Rowing Machine",           "emoji": "-", "group": "Cardio"},
    "stair_climber":      {"label": "Stair Climber",            "emoji": "-", "group": "Cardio"},
    "elliptical":         {"label": "Elliptical",               "emoji": "-", "group": "Cardio"},
    "assault_bike":       {"label": "Assault / Air Bike",       "emoji": "-", "group": "Cardio"},

    # ── BARS & RIGS ──
    "pull_up_bar":        {"label": "Pull-Up Bar",              "emoji": "-", "group": "Bars & Rigs"},
    "dip_bars":           {"label": "Dip Bars / Parallel Bars", "emoji": "-", "group": "Bars & Rigs"},
    "barbell":            {"label": "Barbell",                  "emoji": "", "group": "Bars & Rigs"},
    "ez_curl_bar":        {"label": "EZ Curl Bar",              "emoji": "-", "group": "Bars & Rigs"},
    "squat_rack":         {"label": "Squat Rack / Power Rack",  "emoji": "-", "group": "Bars & Rigs"},
    "smith_machine":      {"label": "Smith Machine",            "emoji": "-", "group": "Bars & Rigs"},

    # ── PUSH EQUIPMENT ──
    "push_up_handles":    {"label": "Rotating Push-Up Handles", "emoji": "-", "group": "Push"},
    "push_up_board":      {"label": "Push-Up Board",            "emoji": "-", "group": "Push"},
    "bench_flat":         {"label": "Flat Bench",               "emoji": "-", "group": "Push"},
    "bench_adjustable":   {"label": "Adjustable Bench",         "emoji": "-", "group": "Push"},

    # ── DUMBBELLS ──
    "dumbbells_light":    {"label": "Dumbbells 3–10 lb",        "emoji": "", "group": "Dumbbells"},
    "dumbbells_medium":   {"label": "Dumbbells 12–25 lb",       "emoji": "", "group": "Dumbbells"},
    "dumbbells_heavy":    {"label": "Dumbbells 30–50 lb",       "emoji": "", "group": "Dumbbells"},
    "dumbbell_25":        {"label": "Single 25 lb Dumbbell",    "emoji": "", "group": "Dumbbells"},
    "dumbbell_35":        {"label": "Single 35 lb Dumbbell",    "emoji": "", "group": "Dumbbells"},
    "adjustable_dumbbell":{"label": "Adjustable Dumbbells",     "emoji": "-", "group": "Dumbbells"},

    # ── KETTLEBELLS ──
    "kettlebell_light":   {"label": "Kettlebell 8–16 kg",       "emoji": "-", "group": "Kettlebells"},
    "kettlebell_heavy":   {"label": "Kettlebell 20–32 kg",      "emoji": "-", "group": "Kettlebells"},

    # ── RESISTANCE BANDS ──
    "bands_light":        {"label": "Light Resistance Band",    "emoji": "-", "group": "Bands"},
    "bands_medium":       {"label": "Medium Resistance Band",   "emoji": "-", "group": "Bands"},
    "bands_heavy":        {"label": "Heavy Resistance Band",    "emoji": "-", "group": "Bands"},
    "bands_loop":         {"label": "Loop / Booty Bands",       "emoji": "-", "group": "Bands"},
    "cable_machine":      {"label": "Cable Machine",            "emoji": "-", "group": "Bands"},

    # ── WEIGHTED GEAR ──
    "weight_vest":        {"label": "Weight Vest",              "emoji": "-", "group": "Weighted Gear"},
    "arm_weights":        {"label": "Arm Weights",              "emoji": "", "group": "Weighted Gear"},
    "leg_weights":        {"label": "Leg Weights",              "emoji": "", "group": "Weighted Gear"},
    "weight_plates":      {"label": "Weight Plates",            "emoji": "-", "group": "Weighted Gear"},

    # ── MACHINES (GYM) ──
    "leg_press":          {"label": "Leg Press Machine",        "emoji": "", "group": "Machines"},
    "leg_curl":           {"label": "Leg Curl Machine",         "emoji": "", "group": "Machines"},
    "leg_extension":      {"label": "Leg Extension Machine",    "emoji": "", "group": "Machines"},
    "lat_pulldown":       {"label": "Lat Pulldown Machine",     "emoji": "-", "group": "Machines"},
    "seated_row":         {"label": "Seated Row Machine",       "emoji": "-", "group": "Machines"},
    "chest_fly_machine":  {"label": "Chest Fly / Pec Deck",     "emoji": "-", "group": "Machines"},
    "shoulder_press_mach":{"label": "Shoulder Press Machine",   "emoji": "-", "group": "Machines"},
    "hack_squat":         {"label": "Hack Squat Machine",       "emoji": "-", "group": "Machines"},
    "ab_crunch_machine":  {"label": "Ab Crunch Machine",        "emoji": "-", "group": "Machines"},

    # ── FLOOR & STABILITY ──
    "yoga_mat":           {"label": "Yoga / Exercise Mat",      "emoji": "-", "group": "Floor & Stability"},
    "foam_roller":        {"label": "Foam Roller",              "emoji": "-", "group": "Floor & Stability"},
    "stability_ball":     {"label": "Stability / Swiss Ball",   "emoji": "-", "group": "Floor & Stability"},
    "bosu_ball":          {"label": "BOSU Ball",                "emoji": "-", "group": "Floor & Stability"},
    "ab_wheel":           {"label": "Ab Wheel",                 "emoji": "-", "group": "Floor & Stability"},
    "balance_board":      {"label": "Balance Board",            "emoji": "-", "group": "Floor & Stability"},
    "parallettes":        {"label": "Parallettes",              "emoji": "-", "group": "Floor & Stability"},

    # ── SUSPENSION & RINGS ──
    "trx":                {"label": "TRX / Suspension Trainer", "emoji": "-", "group": "Suspension"},
    "gymnastic_rings":    {"label": "Gymnastic Rings",          "emoji": "-", "group": "Suspension"},

    # ── ENVIRONMENT ──
    "stairs":             {"label": "Stairs / Steps",           "emoji": "-", "group": "Environment"},
    "outdoor_park":       {"label": "Outdoor Park / Playground","emoji": "-", "group": "Environment"},
    "swimming_pool":      {"label": "Swimming Pool",            "emoji": "-", "group": "Environment"},
    "open_floor":         {"label": "Open Floor Space",         "emoji": "-", "group": "Environment"},
    "wall":               {"label": "Sturdy Wall",              "emoji": "-", "group": "Environment"},
    "chair_or_bench":     {"label": "Chair or Sturdy Surface",  "emoji": "-", "group": "Environment"},
    "sandbag":            {"label": "Sandbag",                  "emoji": "-", "group": "Environment"},
    "sled":               {"label": "Push / Pull Sled",         "emoji": "-", "group": "Environment"},
    "battle_ropes":       {"label": "Battle Ropes",             "emoji": "-", "group": "Environment"},
    "medicine_ball":      {"label": "Medicine Ball",            "emoji": "-", "group": "Environment"},
}

DEFAULT_EQUIPMENT = set(ALL_EQUIPMENT.keys())  # start with everything owned

# ── Location presets — tap to load a typical environment ──
LOCATION_PRESETS = {
    "Home (Minimal)": {
        "keys": {"open_floor",
                 "chair_or_bench","wall"},
        "desc": "Your home setup with personal equipment",
    },
    "Commercial Gym": {
        "keys": {"barbell","squat_rack","bench_flat","bench_adjustable","dumbbells_light",
                 "dumbbells_medium","dumbbells_heavy","adjustable_dumbbell","kettlebell_light",
                 "kettlebell_heavy","cable_machine","lat_pulldown","seated_row","leg_press",
                 "leg_curl","leg_extension","chest_fly_machine","shoulder_press_mach",
                 "hack_squat","ab_crunch_machine","pull_up_bar","dip_bars","bands_light",
                 "bands_medium","bands_heavy","bands_loop","treadmill","stationary_bike",
                 "rowing_machine","stair_climber","elliptical","assault_bike","yoga_mat",
                 "foam_roller","stability_ball","ab_wheel","open_floor"},
        "desc": "Full commercial gym with all equipment",
    },
    "Outdoor / Park": {
        "keys": {"outdoor_park","stairs",
                 "open_floor","wall"},
        "desc": "Park, calisthenics area, or outdoor gym",
    },
    "Office / Desk Break": {
        "keys": {"chair_or_bench","wall"},
        "desc": "No equipment, just your bodyweight and what's in the room",
    },
}

def load_equipment():
    try:
        if os.path.exists(EQUIPMENT_FILE):
            with open(EQUIPMENT_FILE, 'r') as f:
                data = json.load(f)
                return set(data.get("owned", list(DEFAULT_EQUIPMENT)))
    except (json.JSONDecodeError, IOError, KeyError):
        pass
    return set(DEFAULT_EQUIPMENT)

def save_equipment(owned_set):
    try:
        with open(EQUIPMENT_FILE, 'w') as f:
            json.dump({"owned": list(owned_set)}, f)
    except IOError:
        pass

PRESETS_FILE = "presets.json"

def load_presets():
    """Load all presets. On first run, seeds from LOCATION_PRESETS defaults."""
    try:
        if os.path.exists(PRESETS_FILE):
            with open(PRESETS_FILE, 'r') as f:
                data = json.load(f)
                return {name: {"keys": set(v["keys"]), "desc": v.get("desc", "")}
                        for name, v in data.items()}
    except (json.JSONDecodeError, IOError, KeyError):
        pass
    # First run — seed from built-in defaults
    return {name: {"keys": set(v["keys"]), "desc": v["desc"]}
            for name, v in LOCATION_PRESETS.items()}

def save_presets(presets):
    try:
        with open(PRESETS_FILE, 'w') as f:
            json.dump({name: {"keys": list(v["keys"]), "desc": v.get("desc", "")}
                       for name, v in presets.items()}, f, indent=2)
    except IOError:
        pass

# ─────────────────────────────────────────────
# EXERCISE VARIATION LIBRARY
# Each exercise has variations keyed by equipment requirements.
# The resolver picks the best available variation.
# ─────────────────────────────────────────────

EXERCISE_VARIATIONS = {
    # ── PUSH ──
    "chest_press": [
        {"requires": {"push_up_handles", "dumbbell_25"},
         "name": "Single-Arm Floor Press + Push-Up Handles Superset",
         "weight": "25 lb / Bodyweight",
         "instruction": "Alternate: Single-arm floor press (25 lb) then immediately drop to push-up handles. Chest is fully fried by the end of each set."},
        {"requires": {"dumbbell_25"},
         "name": "Single-Arm Floor Press",
         "weight": "25 or 35 lb",
         "instruction": "Lie on your back, press one arm at a time. Brace your core — the uneven load forces anti-rotation work. Drive through your chest, not your shoulder."},
        {"requires": {"dumbbell_35"},
         "name": "Single-Arm Floor Press",
         "weight": "35 lb",
         "instruction": "Lie on your back, press one arm at a time. Heavier load — brace harder. Drive through your chest, not your shoulder."},
        {"requires": {"push_up_handles"},
         "name": "Rotating Push-Up Handles",
         "weight": "Bodyweight",
         "instruction": "Let handles rotate as you push. Deep chest activation. Keep a rigid plank throughout."},
        {"requires": {"bands_medium"},
         "name": "Band Push-Up (Band Across Back)",
         "weight": "Medium Band",
         "instruction": "Loop band across your upper back, hold ends in each hand on the floor. Push-up as normal — band adds resistance at the top."},
        {"requires": set(),
         "name": "Push-Ups",
         "weight": "Bodyweight",
         "instruction": "Classic push-up. Hands slightly wider than shoulders. Lower chest to within an inch of the floor. Full lockout at the top."},
    ],
    "shoulder_press": [
        {"requires": {"dumbbell_25"},
         "name": "Single-Arm Shoulder Press",
         "weight": "25 lb",
         "instruction": "Stand or sit. Brace your core hard to resist leaning to the side. Press straight up, don't flare the elbow out too wide."},
        {"requires": {"dumbbell_35"},
         "name": "Single-Arm Shoulder Press",
         "weight": "35 lb",
         "instruction": "Heavier press — sit for stability. Drive through the heel of your palm. Core must stay rigid to protect the lower back."},
        {"requires": {"dumbbells_light"},
         "name": "Single-Arm Shoulder Press",
         "weight": "10 lb",
         "instruction": "Lighter load — focus on full range of motion. Elbow at 90° at the bottom, full lockout at the top."},
        {"requires": {"bands_medium"},
         "name": "Band Overhead Press",
         "weight": "Medium Band",
         "instruction": "Stand on the band, hold at shoulder height with both hands, press overhead. Bands provide ascending resistance — hardest at the top."},
        {"requires": set(),
         "name": "Pike Push-Ups",
         "weight": "Bodyweight",
         "instruction": "Hands on floor, hips high in an inverted V. Lower your head toward the floor bending at the elbows. Targets the shoulder similarly to an overhead press."},
    ],
    "lateral_raise": [
        {"requires": {"dumbbells_light"},
         "name": "Alternating Lateral Raises",
         "weight": "5–10 lb",
         "instruction": "Slight bend in the elbow, raise to shoulder height only. Don't shrug. These add up fast — lighter is smarter here."},
        {"requires": {"bands_light"},
         "name": "Band Lateral Raises",
         "weight": "Light Band",
         "instruction": "Stand on band, one end in each hand. Raise arms out to the sides. Band tension increases as you raise — squeeze at the top."},
        {"requires": set(),
         "name": "Bodyweight Lateral Arm Raises",
         "weight": "Bodyweight",
         "instruction": "No weight — just the arm movement. Focus on the mind-muscle connection and squeezing the lateral deltoid. Higher reps, 20–25."},
    ],
    "tricep_pushdown": [
        {"requires": {"bands_medium"},
         "name": "Band Tricep Pushdowns",
         "weight": "Medium Band",
         "instruction": "Anchor band overhead. Keep elbows pinned to your sides and push down until arms are fully extended. Squeeze at the bottom."},
        {"requires": {"dumbbell_25"},
         "name": "Single-Arm Overhead Tricep Extension",
         "weight": "25 lb",
         "instruction": "Hold dumbbell overhead, lower behind your head by bending the elbow. Keep upper arm still and vertical. Extend back up fully."},
        {"requires": set(),
         "name": "Diamond Push-Ups",
         "weight": "Bodyweight",
         "instruction": "Hands close together forming a diamond shape under your chest. Elbows track back along your sides. Intense tricep isolation."},
    ],
    "pull_up": [
        {"requires": {"pull_up_bar", "bands_heavy"},
         "name": "Assisted Pull-Ups (Heavy Band)",
         "weight": "Band Assisted",
         "instruction": "Loop heavy band over bar, kneel or stand in loop. Full dead hang at the bottom, chin over bar at the top. Band reduces bodyweight load significantly."},
        {"requires": {"pull_up_bar", "bands_medium"},
         "name": "Assisted Pull-Ups (Medium Band)",
         "weight": "Band Assisted",
         "instruction": "Medium band assist — less help than heavy band. You're doing more of the work. Good for the transition to unassisted."},
        {"requires": {"pull_up_bar"},
         "name": "Pull-Ups",
         "weight": "Bodyweight",
         "instruction": "Full dead hang at the bottom, chin over bar at the top. Don't kip — strict reps only. If you can't complete a rep, do a slow negative (jump to top, lower over 5 seconds)."},
        {"requires": {"bands_heavy"},
         "name": "Band Pull-Downs",
         "weight": "Heavy Band",
         "instruction": "Anchor band above your head. Kneel and pull band down to your chest, driving elbows toward your hips. Mimics the pull-up movement pattern."},
        {"requires": {"bands_medium"},
         "name": "Band Rows (Standing)",
         "weight": "Medium Band",
         "instruction": "Anchor band at chest height. Pull toward your torso, driving elbows back. Best substitute when no bar is available."},
        {"requires": set(),
         "name": "Inverted Rows (Table/Chair)",
         "weight": "Bodyweight",
         "instruction": "Lie under a sturdy table, grip the edge, pull your chest up to it. Straight body like a reverse plank. One of the best pull-up substitutes."},
    ],
    "bent_over_row": [
        {"requires": {"dumbbell_35"},
         "name": "Single-Arm Bent-Over Row",
         "weight": "35 lb",
         "instruction": "Brace one hand on a chair or bench. Keep your back flat and parallel to the floor. Drive your elbow back, not up. Squeeze at the top."},
        {"requires": {"dumbbell_25"},
         "name": "Single-Arm Bent-Over Row",
         "weight": "25 lb",
         "instruction": "Brace one hand for support. Full range of motion — dead hang at the bottom, elbow past your torso at the top. Focus on lat engagement."},
        {"requires": {"dumbbells_light"},
         "name": "Single-Arm Bent-Over Row",
         "weight": "10 lb",
         "instruction": "Lighter weight — focus on the movement pattern and lat squeeze. Higher reps (15 per side) to compensate."},
        {"requires": {"bands_medium"},
         "name": "Band Bent-Over Row",
         "weight": "Medium Band",
         "instruction": "Stand on band, hinge forward, row both ends up simultaneously. Drive elbows back and squeeze at the top."},
        {"requires": set(),
         "name": "Bodyweight Superman Rows",
         "weight": "Bodyweight",
         "instruction": "Lie face down, arms extended. Lift chest and arms simultaneously squeezing the back. Hold 2 seconds at the top. Lower back and repeat."},
    ],
    "face_pull": [
        {"requires": {"bands_light"},
         "name": "Band Face Pulls",
         "weight": "Light Band",
         "instruction": "Anchor band at face height. Pull toward your forehead, elbows flaring up and out. This is your most important posture exercise — don't skip it."},
        {"requires": {"bands_medium"},
         "name": "Band Face Pulls",
         "weight": "Medium Band",
         "instruction": "Anchor band at face height. Pull toward your forehead with elbows high. More resistance — focus on controlled reps."},
        {"requires": set(),
         "name": "Prone Y-T-W Raises",
         "weight": "Bodyweight",
         "instruction": "Lie face down. Raise arms into a Y shape (overhead), then T (out to sides), then W (bent elbows, hands near ears). Each letter is one rep cycle. Targets the exact same muscles as face pulls."},
    ],
    "bicep_curl": [
        {"requires": {"dumbbell_25"},
         "name": "Alternating Dumbbell Curls",
         "weight": "25 lb",
         "instruction": "Supinate (rotate) the wrist as you curl up. Don't swing — keep upper arms pinned to your sides. Full extension at the bottom."},
        {"requires": {"dumbbells_light"},
         "name": "Alternating Dumbbell Curls",
         "weight": "8–10 lb",
         "instruction": "Full range of motion. Squeeze at the top, controlled descent. Higher reps (15 per side) to compensate for lighter weight."},
        {"requires": {"bands_medium"},
         "name": "Band Bicep Curls",
         "weight": "Medium Band",
         "instruction": "Stand on band, curl both ends up simultaneously. Bands provide constant tension — there's no easy spot in the range of motion."},
        {"requires": set(),
         "name": "Isometric Towel Curls",
         "weight": "Bodyweight",
         "instruction": "Loop a towel under your foot. Pull the towel up with both hands like a curl, resisting with your foot. Not ideal but targets the bicep with zero equipment."},
    ],
    "goblet_squat": [
        {"requires": {"dumbbell_35"},
         "name": "Goblet Squat",
         "weight": "35 lb",
         "instruction": "Hold dumbbell at chest height in both hands. Feet shoulder-width, toes slightly out. Squat deep, keeping chest tall. Drive knees out over toes."},
        {"requires": {"dumbbell_25"},
         "name": "Goblet Squat",
         "weight": "25 lb",
         "instruction": "Hold dumbbell at chest height. Focus on depth and chest position. Heels flat, drive knees out. Full range of motion every rep."},
        {"requires": {"weight_vest"},
         "name": "Weighted Squat (Vest)",
         "weight": "Weight Vest",
         "instruction": "Vest on, hands clasped at chest or extended forward for balance. Squat as deep as mobility allows. The vest loads your spine — keep it absolutely upright."},
        {"requires": {"bands_heavy"},
         "name": "Banded Squat",
         "weight": "Heavy Band",
         "instruction": "Band across upper back, held at shoulders. Squat to depth. Band adds resistance at the top where bodyweight squats get too easy."},
        {"requires": set(),
         "name": "Bodyweight Squat",
         "weight": "Bodyweight",
         "instruction": "Arms out front for balance. Squat as deep as possible, chest tall. Slow the descent (3 seconds down) to increase difficulty without added weight."},
    ],
    "romanian_deadlift": [
        {"requires": {"dumbbell_35"},
         "name": "Single-Leg Romanian Deadlift",
         "weight": "35 lb",
         "instruction": "Hold dumbbell in opposite hand to working leg. Hinge at the hip, let the free leg trail back. Keep back flat. Feel the hamstring stretch at the bottom."},
        {"requires": {"dumbbell_25"},
         "name": "Single-Leg Romanian Deadlift",
         "weight": "25 lb",
         "instruction": "Opposite hand holds the weight. Hinge slowly — balance is the challenge here. If unstable, lightly touch your free toe to the floor."},
        {"requires": {"dumbbells_light"},
         "name": "Single-Leg Romanian Deadlift",
         "weight": "10 lb",
         "instruction": "Light weight — really focus on the hamstring stretch and hip hinge pattern. Touch the dumbbell to the floor if mobility allows."},
        {"requires": set(),
         "name": "Single-Leg Hip Hinge",
         "weight": "Bodyweight",
         "instruction": "Arms out for balance. Hinge forward on one leg, free leg trails back. Touch your fingers to the floor if possible. The hamstring and glute still get a strong stimulus."},
    ],
    "reverse_lunge": [
        {"requires": {"weight_vest"},
         "name": "Reverse Lunges (Weight Vest)",
         "weight": "Weight Vest",
         "instruction": "Step back, lower the back knee toward the floor. Keep front shin vertical. Drive through the front heel to return. Control the descent."},
        {"requires": {"dumbbell_25"},
         "name": "Single-Arm Reverse Lunge",
         "weight": "25 lb",
         "instruction": "Hold dumbbell in one hand, alternate sides. The offset load challenges your core and balance on top of the leg work."},
        {"requires": set(),
         "name": "Reverse Lunges",
         "weight": "Bodyweight",
         "instruction": "Step back, lower back knee toward the floor. Front shin stays vertical. Slow 3-second descent to maximize time under tension without added weight."},
    ],
    "glute_bridge": [
        {"requires": {"leg_weights"},
         "name": "Glute Bridges (Leg Weights)",
         "weight": "Leg Weights",
         "instruction": "Lie on back, feet flat, leg weights strapped on. Drive hips up by squeezing glutes hard. Hold at top for 1 second. Lower slowly."},
        {"requires": {"dumbbell_25"},
         "name": "Dumbbell Glute Bridge",
         "weight": "25 lb",
         "instruction": "Rest 25 lb dumbbell across your hips. Drive hips up and squeeze hard at the top. The extra load makes even low reps effective."},
        {"requires": {"bands_medium"},
         "name": "Banded Glute Bridge",
         "weight": "Medium Band",
         "instruction": "Band across hips anchored by your hands. Bridges as normal — band adds resistance at the top of the movement where glutes are most engaged."},
        {"requires": set(),
         "name": "Glute Bridges",
         "weight": "Bodyweight",
         "instruction": "Drive hips up, hold 2 seconds at the top, lower slowly. Higher reps (25–30) to compensate for no external load. Squeeze hard every rep."},
    ],
    "thruster": [
        {"requires": {"dumbbell_25"},
         "name": "Single-Arm Dumbbell Thruster",
         "weight": "25 lb",
         "instruction": "Squat to press combined. Hold dumbbell at shoulder, squat down, drive up and press overhead in one fluid motion. Alternate sides each rep."},
        {"requires": {"dumbbells_light"},
         "name": "Single-Arm Dumbbell Thruster",
         "weight": "10 lb",
         "instruction": "Lighter thruster — focus on the fluid squat-to-press connection. Higher reps (10 per side) to compensate."},
        {"requires": {"bands_medium"},
         "name": "Band Thruster",
         "weight": "Medium Band",
         "instruction": "Stand on band, hold at shoulders. Squat down, drive up and press overhead in one movement. Bands make the top half hardest — push through it."},
        {"requires": set(),
         "name": "Jump Squat to Overhead Reach",
         "weight": "Bodyweight",
         "instruction": "Squat down, explode up into a jump reaching both arms overhead. Land soft. This is a full-body power movement — pure conditioning when no weights are available."},
    ],
}


def resolve_exercise(exercise_key, owned_equipment, sets, reps, rest):
    """Pick the best variation of an exercise based on owned equipment."""
    variations = EXERCISE_VARIATIONS.get(exercise_key, [])
    for variation in variations:
        if variation["requires"].issubset(owned_equipment):
            return {
                "name": variation["name"],
                "sets": sets,
                "reps": reps,
                "rest": rest,
                "weight": variation["weight"],
                "instruction": variation["instruction"],
            }
    # Fallback — last variation always has empty requires set
    fallback = variations[-1] if variations else {}
    return {
        "name": fallback.get("name", exercise_key),
        "sets": sets,
        "reps": reps,
        "rest": rest,
        "weight": fallback.get("weight", "Bodyweight"),
        "instruction": fallback.get("instruction", ""),
    }


def build_workout_for_equipment(day_key, owned_equipment):
    """Return a workout day's exercise list resolved for current equipment."""
    base = WORKOUT_PLAN[day_key]

    # Map each exercise in the static plan to its variation key
    EXERCISE_KEY_MAP = {
        "Day 1": [
            ("chest_press",     3, "8–12 per side", 60),
            ("chest_press",     3, "10–15",          60),   # push-up handles variation
            ("shoulder_press",  3, "8–10 per side",  60),
            ("lateral_raise",   3, "12–15 per side", 45),
            ("tricep_pushdown", 3, "15",              45),
            ("tricep_pushdown", 3, "10–12 per side",  45),
            # Core exercises are always bodyweight — keep as-is
        ],
        "Day 2": [
            ("pull_up",         3, "6–10",            90),
            ("bent_over_row",   3, "10–12 per side",  60),
            ("face_pull",       3, "15",              45),
            ("face_pull",       3, "20",              30),   # pull-aparts
            ("bicep_curl",      3, "10–12 per side",  45),
            ("bicep_curl",      3, "10 per side",     45),   # hammer curl slot
        ],
        "Day 3": [
            ("goblet_squat",       3, "12–15",         60),
            ("romanian_deadlift",  3, "8–10 per side", 60),
            ("reverse_lunge",      3, "12 per leg",    60),
            ("glute_bridge",       3, "20",            45),
        ],
        "Day 4": [
            ("chest_press",        4, "10",            15),
            ("pull_up",            4, "8",             15),
            ("thruster",           4, "5 per side",    15),
            ("romanian_deadlift",  4, "5 per side",    15),
            ("glute_bridge",       4, "15",            15),
        ],
    }

    resolved = []
    for key, sets, reps, rest in EXERCISE_KEY_MAP.get(day_key, []):
        resolved.append(resolve_exercise(key, owned_equipment, sets, reps, rest))

    # Always append the bodyweight-only exercises (core, jump rope finisher, dead hangs)
    STATIC_EXTRAS = {
        "Day 1": [
            {"name": "Plank", "sets": 3, "reps": "45 sec", "weight": "Bodyweight",
             "rest": 30, "type": "timed", "duration": 45,
             "instruction": "Forearms or hands. Keep hips level — don't let them sag or pike up. Squeeze glutes and abs throughout."},
            {"name": "Dead Bugs", "sets": 3, "reps": "10 per side", "weight": "Bodyweight",
             "rest": 30,
             "instruction": "Lying on back, arms up, knees at 90°. Lower opposite arm and leg slowly while pressing lower back into the floor. Exhale as you lower."},
            {"name": "Bicycle Crunches", "sets": 3, "reps": "20", "weight": "Bodyweight",
             "rest": 30,
             "instruction": "Slow and controlled. Rotate your shoulder toward the knee, not just your elbow. Keep lower back pressed down."},
        ],
        "Day 2": [
            {"name": "Dead Hangs", "sets": 3, "reps": "20–30 sec", "weight": "Bodyweight",
             "rest": 45, "type": "timed", "duration": 25,
             "instruction": "Full grip on the bar, let your body hang completely. Builds grip strength and decompresses your spine. Breathe slowly."
             } if "pull_up_bar" in owned_equipment else
            {"name": "Band Pull-Aparts", "sets": 3, "reps": "20", "weight": "Light Band",
             "rest": 30,
             "instruction": "Hold band at chest width, pull apart until band touches your chest. Squeeze shoulder blades together. Controlled return."},
        ],
        "Day 3": [
            {"name": "Donkey Kicks (Leg Weights)" if "leg_weights" in owned_equipment else "Donkey Kicks",
             "sets": 3, "reps": "15 per side",
             "weight": "Leg Weights" if "leg_weights" in owned_equipment else "Bodyweight",
             "rest": 30,
             "instruction": "On all fours. Keep the 90° bend in your knee and kick straight up. Squeeze the glute at the top. Hips stay level."},
            {"name": "Banded Lateral Walks" if "bands_medium" in owned_equipment else "Lateral Walks",
             "sets": 3, "reps": "15 steps each way",
             "weight": "Medium Band" if "bands_medium" in owned_equipment else "Bodyweight",
             "rest": 30,
             "instruction": "Band around thighs above knees. Slight squat position, step side to side maintaining band tension. Burns the outer glute." if "bands_medium" in owned_equipment else "Stay in a half-squat, step side to side with controlled movement. Slow pace maximises glute activation."},
            {"name": "Jump Rope Intervals" if "jump_rope" in owned_equipment else "High Knees Intervals",
             "sets": 5, "reps": "30s on / 15s off",
             "weight": "Bodyweight",
             "rest": 15, "type": "timed", "duration": 30,
             "instruction": "Push the pace. This is conditioning. Breathe rhythmically and maintain form even when tired." if "jump_rope" in owned_equipment else "Drive knees up to hip height, arms pumping. Same cardio stimulus as jump rope with no equipment needed."},
        ],
        "Day 4": [
            {"name": "Jump Rope" if "jump_rope" in owned_equipment else "High Knees",
             "sets": 4, "reps": "30 seconds",
             "weight": "Bodyweight",
             "rest": 60, "type": "timed", "duration": 30,
             "instruction": "Round finisher. Push hard. After this, rest 60 seconds and start the next round." if "jump_rope" in owned_equipment else "Drive knees to hip height, arms pumping. Same intensity as jump rope. Round finisher — push hard."},
        ],
    }

    resolved.extend(STATIC_EXTRAS.get(day_key, []))
    return resolved


def load_progress():
    try:
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return {"completed_workouts": [], "total_sets": 0, "total_workouts": 0, "streak": 0, "last_date": ""}

def save_progress(data):
    try:
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(data, f)
    except IOError:
        pass

# ─────────────────────────────────────────────
# CUSTOM WIDGETS
# ─────────────────────────────────────────────

class ColoredBox(BoxLayout):
    def __init__(self, bg_color='surface', radius=12, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.radius = radius
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*c(self.bg_color))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(self.radius)])


class FitButton(Button):
    def __init__(self, accent=True, **kwargs):
        super().__init__(**kwargs)
        self.accent = accent
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.color = c('bg') if accent else c('text')
        self.font_size = sp(16)
        self.bold = True
        self.size_hint_y = None
        self.height = dp(54)
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*(c('accent') if self.accent else c('surface2')))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])


# ─────────────────────────────────────────────
# SCREENS
# ─────────────────────────────────────────────

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.progress = load_progress()

    def on_enter(self):
        self.progress = load_progress()
        self.clear_widgets()
        self._build()

    def _build(self):
        root = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(16))

        with root.canvas.before:
            Color(*c('bg'))
            self._bg_rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: setattr(self._bg_rect, 'pos', root.pos),
                  size=lambda *a: setattr(self._bg_rect, 'size', root.size))

        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(64), spacing=dp(8))

        title_col = BoxLayout(orientation='vertical', spacing=dp(2))
        title_lbl = Label(text="FITFORGE", font_size=sp(26), bold=True,
                          color=c('accent'), halign='left', valign='bottom')
        title_lbl.bind(size=title_lbl.setter('text_size'))
        sub_lbl = Label(text="Your personal workout companion",
                        font_size=sp(11), color=c('text_dim'),
                        halign='left', valign='top')
        sub_lbl.bind(size=sub_lbl.setter('text_size'))
        title_col.add_widget(title_lbl)
        title_col.add_widget(sub_lbl)
        header.add_widget(title_col)

        btn_col = BoxLayout(orientation='vertical', spacing=dp(6),
                            size_hint_x=None, width=dp(72))

        def make_header_btn(text, color, callback):
            btn = Button(text=text, font_size=sp(11), bold=True,
                         background_normal='', background_color=(0,0,0,0),
                         color=color, size_hint_y=None, height=dp(26))
            with btn.canvas.before:
                Color(*c('surface'))
                btn._bg = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(6)])
            btn.bind(pos=lambda i, *a: setattr(i._bg, 'pos', i.pos),
                     size=lambda i, *a: setattr(i._bg, 'size', i.size))
            btn.bind(on_press=callback)
            return btn

        btn_col.add_widget(make_header_btn("EQUIP", c('accent2'), self._go_equipment))
        btn_col.add_widget(make_header_btn("MENU",  c('text_dim'), self._go_menu))
        header.add_widget(btn_col)
        root.add_widget(header)

        # Stats row
        stats = GridLayout(cols=3, size_hint_y=None, height=dp(90), spacing=dp(10))
        for label, value in [
            ("WORKOUTS", str(self.progress.get('total_workouts', 0))),
            ("TOTAL SETS", str(self.progress.get('total_sets', 0))),
            ("STREAK", str(self.progress.get("streak", 0))),
        ]:
            card = ColoredBox(bg_color='surface', radius=12, orientation='vertical',
                              padding=dp(8))
            card.add_widget(Label(text=value, font_size=sp(22), bold=True,
                                  color=c('accent'), size_hint_y=0.6))
            card.add_widget(Label(text=label, font_size=sp(10), color=c('text_dim'),
                                  size_hint_y=0.4))
            stats.add_widget(card)
        root.add_widget(stats)

        # Workout days
        scroll = ScrollView()
        days_layout = BoxLayout(orientation='vertical', spacing=dp(12),
                                size_hint_y=None, padding=(0, dp(4)))
        days_layout.bind(minimum_height=days_layout.setter('height'))

        for day_key, day_data in WORKOUT_PLAN.items():
            btn = self._make_day_card(day_key, day_data)
            days_layout.add_widget(btn)

        # Rest day stretch button
        rest_btn = self._make_rest_card()
        days_layout.add_widget(rest_btn)

        scroll.add_widget(days_layout)
        root.add_widget(scroll)

        self.add_widget(root)

    def _make_day_card(self, day_key, day_data):
        card = ColoredBox(bg_color='card', radius=16, orientation='horizontal',
                          size_hint_y=None, height=dp(88), padding=dp(16), spacing=dp(12))

        # Accent left bar
        with card.canvas.before:
            Color(*get_color_from_hex(day_data['color']))
            card._accent_bar = Rectangle()

        def update_bar(*args):
            card._accent_bar.pos = (card.x, card.y + dp(12))
            card._accent_bar.size = (dp(4), card.height - dp(24))
        card.bind(pos=update_bar, size=update_bar)

        # Info
        left = BoxLayout(orientation='vertical', spacing=dp(4))
        top_row = BoxLayout(orientation='horizontal', spacing=dp(8), size_hint_y=None, height=dp(20))
        day_lbl = Label(text=day_key.upper(), font_size=sp(11), bold=True,
                        color=get_color_from_hex(day_data['color']),
                        halign='left', valign='middle')
        day_lbl.bind(size=day_lbl.setter('text_size'))
        top_row.add_widget(day_lbl)
        left.add_widget(top_row)

        name_lbl = Label(text=day_data['name'], font_size=sp(17), bold=True,
                         color=c('text'), halign='left', valign='middle',
                         size_hint_y=None, height=dp(28))
        name_lbl.bind(size=name_lbl.setter('text_size'))
        left.add_widget(name_lbl)

        ex_count = f"{len(day_data['exercises'])} exercises  •  {len(day_data['warmup'])} warmup"
        count_lbl = Label(text=ex_count, font_size=sp(11), color=c('text_dim'),
                          halign='left', valign='middle')
        count_lbl.bind(size=count_lbl.setter('text_size'))
        left.add_widget(count_lbl)

        card.add_widget(left)

        # Chevron
        card.add_widget(Label(text=">", font_size=sp(20), bold=True, color=c('text_dim'),
                               size_hint_x=None, width=dp(20)))

        # Make card tappable directly
        card.day_key = day_key

        def card_touch(instance, touch, dk=day_key):
            if instance.collide_point(*touch.pos) and touch.grab_current is None:
                app = App.get_running_app()
                app.current_day = dk
                app.root.transition = SlideTransition(direction='left')
                app.root.current = 'workout'
                return True

        card.bind(on_touch_up=card_touch)
        return card

    def _make_rest_card(self):
        card = ColoredBox(bg_color='card', radius=16, orientation='horizontal',
                          size_hint_y=None, height=dp(88), padding=dp(16), spacing=dp(12))

        with card.canvas.before:
            Color(*get_color_from_hex('#A78BFA'))
            card._accent_bar = Rectangle()

        def update_bar(*args):
            card._accent_bar.pos = (card.x, card.y + dp(12))
            card._accent_bar.size = (dp(4), card.height - dp(24))
        card.bind(pos=update_bar, size=update_bar)

        left = BoxLayout(orientation='vertical', spacing=dp(4))
        top_row = BoxLayout(orientation='horizontal', spacing=dp(8), size_hint_y=None, height=dp(20))
        rest_lbl = Label(text="REST DAY", font_size=sp(11), bold=True,
                         color=get_color_from_hex('#A78BFA'),
                         halign='left', valign='middle')
        rest_lbl.bind(size=rest_lbl.setter('text_size'))
        top_row.add_widget(rest_lbl)
        left.add_widget(top_row)

        name_lbl = Label(text="Full Body Stretch Routine", font_size=sp(17), bold=True,
                         color=c('text'), halign='left', valign='middle',
                         size_hint_y=None, height=dp(28))
        name_lbl.bind(size=name_lbl.setter('text_size'))
        left.add_widget(name_lbl)

        sub_lbl = Label(text=f"{len(REST_DAY_STRETCHING)} stretches  •  ~20 minutes",
                        font_size=sp(11), color=c('text_dim'),
                        halign='left', valign='middle')
        sub_lbl.bind(size=sub_lbl.setter('text_size'))
        left.add_widget(sub_lbl)

        card.add_widget(left)
        card.add_widget(Label(text=">", font_size=sp(20), bold=True, color=c('text_dim'),
                               size_hint_x=None, width=dp(20)))

        def card_touch(instance, touch):
            if instance.collide_point(*touch.pos) and touch.grab_current is None:
                app = App.get_running_app()
                app.root.transition = SlideTransition(direction='left')
                app.root.current = 'stretch'
                return True

        card.bind(on_touch_up=card_touch)
        return card

    def _go_equipment(self, *args):
        app = App.get_running_app()
        app.root.transition = SlideTransition(direction='left')
        app.root.current = 'equipment'

    def _go_menu(self, *args):
        app = App.get_running_app()
        app.root.transition = SlideTransition(direction='left')
        app.root.current = 'menu'


class WorkoutScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timer_event = None
        self.timer_remaining = 0
        self.current_exercise_idx = 0
        self.current_set = 1
        self.phase = 'warmup'  # 'warmup' or 'workout'
        self.warmup_idx = 0
        self.sets_completed = 0
        self.workout_started = False
        self.paused = False
        self.exercise_timer_paused = False
        self.active_timer_type = None  # 'exercise' or 'rest'
        self.active_timer_duration = 0

    def on_enter(self):
        self.clear_widgets()
        app = App.get_running_app()
        self.day_key = app.current_day
        self.day_data = WORKOUT_PLAN[self.day_key]
        # Resolve exercises based on current equipment
        owned = load_equipment()
        self.day_data = dict(self.day_data)  # shallow copy
        self.day_data['exercises'] = build_workout_for_equipment(self.day_key, owned)
        self.current_exercise_idx = 0
        self.current_set = 1
        self.phase = 'warmup'
        self.warmup_idx = 0
        self.sets_completed = 0
        self.workout_started = False
        self.paused = False
        self.exercise_timer_paused = False
        self.active_timer_type = None
        self.active_timer_duration = 0
        self._build()

    def _build(self):
        self.root_layout = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))

        with self.root_layout.canvas.before:
            Color(*c('bg'))
            self._bg = Rectangle(pos=self.root_layout.pos, size=self.root_layout.size)
        self.root_layout.bind(
            pos=lambda *a: setattr(self._bg, 'pos', self.root_layout.pos),
            size=lambda *a: setattr(self._bg, 'size', self.root_layout.size))

        # Top bar
        topbar = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        back_btn = Button(text="Back", size_hint_x=None, width=dp(80),
                          background_normal='', background_color=(0,0,0,0),
                          color=c('text_dim'), font_size=sp(14))
        back_btn.bind(on_press=self._go_back)
        topbar.add_widget(back_btn)

        self.day_label = Label(
            text=f"{self.day_key}: {self.day_data['name']}",
            font_size=sp(16), bold=True, color=c('text'))
        topbar.add_widget(self.day_label)
        self.root_layout.add_widget(topbar)

        # Phase indicator
        self.phase_label = Label(text="WARM UP", font_size=sp(11), bold=True,
                                  color=get_color_from_hex(self.day_data['color']),
                                  size_hint_y=None, height=dp(20))
        self.root_layout.add_widget(self.phase_label)

        # Exercise card
        self.exercise_card = ColoredBox(bg_color='surface', radius=20,
                                         orientation='vertical', padding=dp(20),
                                         spacing=dp(12), size_hint_y=None, height=dp(280))

        self.ex_name_label = Label(text="", font_size=sp(22), bold=True,
                                    color=c('text'), halign='center', valign='middle')
        self.ex_name_label.bind(size=self.ex_name_label.setter('text_size'))
        self.exercise_card.add_widget(self.ex_name_label)

        self.ex_detail_label = Label(text="", font_size=sp(14), color=c('accent'),
                                      halign='center', valign='middle',
                                      size_hint_y=None, height=dp(28))
        self.exercise_card.add_widget(self.ex_detail_label)

        self.set_label = Label(text="", font_size=sp(28), bold=True,
                                color=c('accent'), size_hint_y=None, height=dp(40))
        self.exercise_card.add_widget(self.set_label)

        self.weight_label = Label(text="", font_size=sp(13), color=c('text_dim'),
                                   size_hint_y=None, height=dp(22))
        self.exercise_card.add_widget(self.weight_label)

        self.root_layout.add_widget(self.exercise_card)

        # Instruction box
        self.instruction_scroll = ScrollView(size_hint_y=None, height=dp(100))
        self.instruction_label = Label(text="", font_size=sp(13), color=c('text_dim'),
                                        halign='center', valign='top',
                                        size_hint_y=None, padding=(dp(10), dp(6)))
        self.instruction_label.bind(texture_size=self.instruction_label.setter('size'))
        self.instruction_label.bind(width=lambda *a: setattr(
            self.instruction_label, 'text_size', (self.instruction_label.width, None)))
        self.instruction_scroll.add_widget(self.instruction_label)
        self.root_layout.add_widget(self.instruction_scroll)

        # Timer display
        self.timer_box = ColoredBox(bg_color='surface2', radius=16,
                                     orientation='vertical', padding=dp(12),
                                     size_hint_y=None, height=dp(80))
        self.timer_label = Label(text="", font_size=sp(36), bold=True, color=c('accent'))
        self.timer_sub = Label(text="", font_size=sp(12), color=c('text_dim'),
                                size_hint_y=None, height=dp(18))
        self.timer_box.add_widget(self.timer_label)
        self.timer_box.add_widget(self.timer_sub)
        self.root_layout.add_widget(self.timer_box)
        self.timer_box.opacity = 0

        # Progress bar
        self.progress_bar = ProgressBar(max=100, value=0,
                                         size_hint_y=None, height=dp(6))
        self.root_layout.add_widget(self.progress_bar)

        # Workout control row: Start/Pause | Stop
        control_row = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(10))

        self.start_pause_btn = FitButton(text="START WORKOUT", accent=True)
        self.start_pause_btn.bind(on_press=self._toggle_start_pause)
        control_row.add_widget(self.start_pause_btn)

        self.stop_btn = FitButton(text="STOP", accent=False)
        self.stop_btn.bind(on_press=self._confirm_stop)
        self.stop_btn.size_hint_x = 0.35
        self.stop_btn.opacity = 0.3
        self.stop_btn.disabled = True
        control_row.add_widget(self.stop_btn)
        self.root_layout.add_widget(control_row)

        # Secondary row: timer controls | set done
        btn_row = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(8))

        # Exercise timer controls (shown during timed exercises)
        self.pause_exercise_btn = FitButton(text="PAUSE", accent=False)
        self.pause_exercise_btn.bind(on_press=self._toggle_exercise_timer)
        self.pause_exercise_btn.opacity = 0
        self.pause_exercise_btn.disabled = True
        self.pause_exercise_btn.size_hint_x = 0.45
        btn_row.add_widget(self.pause_exercise_btn)

        self.restart_exercise_btn = FitButton(text="RESTART", accent=False)
        self.restart_exercise_btn.bind(on_press=self._restart_exercise_timer)
        self.restart_exercise_btn.opacity = 0
        self.restart_exercise_btn.disabled = True
        self.restart_exercise_btn.size_hint_x = 0.45
        btn_row.add_widget(self.restart_exercise_btn)

        # Rest timer controls (shown during rest periods)
        self.pause_rest_btn = FitButton(text="PAUSE REST", accent=False)
        self.pause_rest_btn.bind(on_press=self._toggle_rest_timer)
        self.pause_rest_btn.opacity = 0
        self.pause_rest_btn.disabled = True
        self.pause_rest_btn.size_hint_x = 0.55
        btn_row.add_widget(self.pause_rest_btn)

        self.start_timer_btn = FitButton(text="RESTART REST", accent=False)
        self.start_timer_btn.bind(on_press=self._start_rest_timer)
        self.start_timer_btn.opacity = 0
        self.start_timer_btn.disabled = True
        self.start_timer_btn.size_hint_x = 0.55
        btn_row.add_widget(self.start_timer_btn)

        self.next_btn = FitButton(text="DONE")
        self.next_btn.bind(on_press=self._next)
        self.next_btn.opacity = 0.3
        self.next_btn.disabled = True
        btn_row.add_widget(self.next_btn)
        self.root_layout.add_widget(btn_row)

        self.add_widget(self.root_layout)
        self._refresh_display()

    def _refresh_display(self):
        # Only cancel if not actively running — callers that want to cancel do so explicitly
        if not self.workout_started or self.paused:
            self._cancel_timer()

        if self.phase == 'warmup':
            warmup_list = self.day_data['warmup']
            if self.warmup_idx >= len(warmup_list):
                self._show_warmup_complete()
                return

            item = warmup_list[self.warmup_idx]
            self.phase_label.text = "WARM UP"
            self.phase_label.color = get_color_from_hex('#A78BFA')
            self.ex_name_label.text = item['name']
            self.ex_detail_label.text = item.get('reps', '') or f"{item.get('duration', '')}s"
            self.set_label.text = f"{self.warmup_idx + 1} of {len(warmup_list)}"
            self.weight_label.text = ""
            self.instruction_label.text = item.get('instruction', '')
            self.next_btn.text = "DONE"
            self.start_timer_btn.opacity = 0
            self.start_timer_btn.disabled = True
            self.pause_rest_btn.opacity = 0
            self.pause_rest_btn.disabled = True
            self.pause_exercise_btn.opacity = 0
            self.pause_exercise_btn.disabled = True
            self.restart_exercise_btn.opacity = 0
            self.restart_exercise_btn.disabled = True
            self.timer_box.opacity = 0

            if self.workout_started and not self.paused:
                if item.get('type') == 'timed':
                    self.exercise_timer_paused = False
                    self._start_exercise_timer(item['duration'])
                    self.pause_exercise_btn.text = "PAUSE"
                    self.pause_exercise_btn.opacity = 1
                    self.pause_exercise_btn.disabled = False
                    self.restart_exercise_btn.opacity = 1
                    self.restart_exercise_btn.disabled = False

            total = len(warmup_list)
            self.progress_bar.value = (self.warmup_idx / total) * 30

        else:
            exercises = self.day_data['exercises']
            if self.current_exercise_idx >= len(exercises):
                self._workout_complete()
                return

            ex = exercises[self.current_exercise_idx]
            self.phase_label.text = "WORKOUT"
            self.phase_label.color = get_color_from_hex(self.day_data['color'])
            self.ex_name_label.text = ex['name']
            self.ex_detail_label.text = f"{ex['reps']}"
            self.set_label.text = f"Set {self.current_set} of {ex['sets']}"
            self.weight_label.text = f"{ex.get('weight', '')}"
            self.instruction_label.text = ex.get('instruction', '')
            self.next_btn.text = "SET DONE"

            total_ex = len(exercises)
            warmup_prog = 30
            ex_prog = (self.current_exercise_idx / total_ex) * 70
            self.progress_bar.value = warmup_prog + ex_prog

            if self.workout_started and not self.paused:
                if ex.get('type') == 'timed':
                    self.exercise_timer_paused = False
                    self._start_exercise_timer(ex.get('duration', 30))
                    self.pause_exercise_btn.text = "PAUSE"
                    self.pause_exercise_btn.opacity = 1
                    self.pause_exercise_btn.disabled = False
                    self.restart_exercise_btn.opacity = 1
                    self.restart_exercise_btn.disabled = False
                    self.pause_rest_btn.opacity = 0
                    self.pause_rest_btn.disabled = True
                    self.start_timer_btn.opacity = 0
                    self.start_timer_btn.disabled = True
                else:
                    self.timer_box.opacity = 0
                    self.pause_exercise_btn.opacity = 0
                    self.pause_exercise_btn.disabled = True
                    self.restart_exercise_btn.opacity = 0
                    self.restart_exercise_btn.disabled = True
                    self.pause_rest_btn.opacity = 0
                    self.pause_rest_btn.disabled = True
                    self.start_timer_btn.opacity = 0
                    self.start_timer_btn.disabled = True
            else:
                self.timer_box.opacity = 0
                self.pause_exercise_btn.opacity = 0
                self.pause_exercise_btn.disabled = True
                self.restart_exercise_btn.opacity = 0
                self.restart_exercise_btn.disabled = True
                self.pause_rest_btn.opacity = 0
                self.pause_rest_btn.disabled = True
                self.start_timer_btn.opacity = 0
                self.start_timer_btn.disabled = True

    def _show_warmup_complete(self):
        """Show a full-screen transition banner between warmup and workout."""
        self._cancel_timer()
        self.clear_widgets()

        layout = BoxLayout(orientation='vertical', padding=dp(40), spacing=dp(24))
        with layout.canvas.before:
            Color(*c('bg'))
            layout._bg = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=lambda *a: setattr(layout._bg, 'pos', layout.pos),
                    size=lambda *a: setattr(layout._bg, 'size', layout.size))

        layout.add_widget(Label(text="WARMUP", font_size=sp(72), size_hint_y=None, height=dp(90)))
        layout.add_widget(Label(text="WARM UP COMPLETE",
                                font_size=sp(24), bold=True,
                                color=get_color_from_hex(self.day_data['color'])))
        layout.add_widget(Label(
            text=f"Great work. Your body is ready.\nTime to hit {self.day_data['name']}.",
            font_size=sp(15), color=c('text_dim'),
            halign='center', valign='middle'))

        # Summary of what's coming
        ex_count = len(self.day_data['exercises'])
        total_sets = sum(e['sets'] for e in self.day_data['exercises'])
        summary_box = ColoredBox(bg_color='surface', radius=16, orientation='vertical',
                                  padding=dp(20), spacing=dp(8),
                                  size_hint_y=None, height=dp(100))
        summary_box.add_widget(Label(
            text=f"{ex_count} exercises  •  {total_sets} total sets",
            font_size=sp(16), bold=True, color=c('text')))
        summary_box.add_widget(Label(
            text="Rest timers will auto-start between sets",
            font_size=sp(12), color=c('text_dim')))
        layout.add_widget(summary_box)

        layout.add_widget(Label(size_hint_y=1))  # spacer

        begin_btn = FitButton(text=f"BEGIN {self.day_data['name'].upper()}")

        def begin(instance):
            self.phase = 'workout'
            self.current_exercise_idx = 0
            self.current_set = 1
            self.clear_widgets()
            self._build()

        begin_btn.bind(on_press=begin)
        layout.add_widget(begin_btn)

        self.add_widget(layout)

    def _toggle_start_pause(self, *args):
        if not self.workout_started:
            # First press — START
            self.workout_started = True
            self.paused = False
            self.start_pause_btn.text = "PAUSE"
            self.stop_btn.opacity = 1
            self.stop_btn.disabled = False
            self.next_btn.opacity = 1
            self.next_btn.disabled = False
            self._refresh_display()

        elif not self.paused:
            # Running → PAUSE
            self.paused = True
            self._cancel_timer()
            self.exercise_timer_paused = False
            self.start_pause_btn.text = "RESUME"
            self.next_btn.opacity = 0.3
            self.next_btn.disabled = True
            self.pause_exercise_btn.opacity = 0
            self.pause_exercise_btn.disabled = True
            self.restart_exercise_btn.opacity = 0
            self.restart_exercise_btn.disabled = True
            self.start_timer_btn.opacity = 0
            self.start_timer_btn.disabled = True
            self.pause_rest_btn.opacity = 0
            self.pause_rest_btn.disabled = True
            if self.timer_box.opacity == 1:
                self.timer_sub.text = "paused"

        else:
            # Paused → RESUME
            self.paused = False
            self.start_pause_btn.text = "PAUSE"
            self.next_btn.opacity = 1
            self.next_btn.disabled = False
            if self.active_timer_type == 'exercise':
                self.timer_box.opacity = 1
                self.timer_sub.text = "seconds"
                self.timer_label.color = c('accent')
                self.timer_event = Clock.schedule_interval(self._tick_exercise, 1)
                self.pause_exercise_btn.text = "PAUSE"
                self.pause_exercise_btn.opacity = 1
                self.pause_exercise_btn.disabled = False
                self.restart_exercise_btn.opacity = 1
                self.restart_exercise_btn.disabled = False
            elif self.active_timer_type == 'rest':
                self.timer_box.opacity = 1
                self.timer_sub.text = "rest seconds"
                self.timer_label.color = c('accent2')
                self.timer_event = Clock.schedule_interval(self._tick_rest, 1)
                self.pause_rest_btn.text = "PAUSE REST"
                self.pause_rest_btn.opacity = 1
                self.pause_rest_btn.disabled = False
                self.start_timer_btn.opacity = 1
                self.start_timer_btn.disabled = False

    def _confirm_stop(self, *args):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(16))
        content.add_widget(Label(
            text="Stop this workout?\nYour progress will not be saved.",
            font_size=sp(15), color=c('text'), halign='center'))

        btn_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        cancel_btn = Button(text="Keep Going", background_normal='',
                            background_color=get_color_from_hex('#2ECC71'),
                            color=c('bg'), bold=True, font_size=sp(14))
        stop_confirm_btn = Button(text="Stop Workout", background_normal='',
                                   background_color=c('danger'),
                                   color=c('text'), bold=True, font_size=sp(14))

        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(stop_confirm_btn)
        content.add_widget(btn_row)

        popup = Popup(title="Stop Workout", content=content,
                      size_hint=(0.85, None), height=dp(220),
                      background_color=c('surface'),
                      title_color=c('text'), separator_color=c('accent'))

        cancel_btn.bind(on_press=popup.dismiss)
        stop_confirm_btn.bind(on_press=lambda *a: [popup.dismiss(), self._stop_workout()])
        popup.open()

    def _stop_workout(self, *args):
        self._cancel_timer()
        self.workout_started = False
        self.paused = False
        self.active_timer_type = None
        app = App.get_running_app()
        app.root.transition = SlideTransition(direction='right')
        app.root.current = 'home'

    def _start_exercise_timer(self, duration):
        self._cancel_timer()
        self.active_timer_type = 'exercise'
        self.active_timer_duration = duration
        self.timer_remaining = duration
        self.timer_box.opacity = 1
        self.timer_label.text = str(duration)
        self.timer_label.color = c('accent')
        self.timer_sub.text = "seconds"
        self.timer_event = Clock.schedule_interval(self._tick_exercise, 1)

    def _tick_exercise(self, dt):
        self.timer_remaining -= 1
        self.timer_label.text = str(self.timer_remaining)
        if self.timer_remaining <= 0:
            self._cancel_timer()
            self.active_timer_type = None
            self.exercise_timer_paused = False
            self.timer_label.text = "DONE!"
            self.timer_label.color = c('success')
            self.pause_exercise_btn.opacity = 0
            self.pause_exercise_btn.disabled = True
            self.restart_exercise_btn.opacity = 0
            self.restart_exercise_btn.disabled = True
            return False

    def _toggle_exercise_timer(self, *args):
        """Pause or resume the active exercise timer."""
        if not self.workout_started or self.paused:
            return
        if not self.exercise_timer_paused:
            # Pause it
            self._cancel_timer()
            self.exercise_timer_paused = True
            self.pause_exercise_btn.text = "RESUME"
            self.timer_sub.text = "paused"
        else:
            # Resume it
            self.exercise_timer_paused = False
            self.pause_exercise_btn.text = "PAUSE"
            self.timer_label.color = c('accent')
            self.timer_sub.text = "seconds"
            self.timer_event = Clock.schedule_interval(self._tick_exercise, 1)

    def _toggle_rest_timer(self, *args):
        """Pause or resume the active rest timer."""
        if not self.workout_started or self.paused:
            return
        if self.active_timer_type == 'rest' and self.timer_event:
            # Pause it
            self._cancel_timer()
            self.active_timer_type = 'rest'  # keep type so resume knows what to do
            self.pause_rest_btn.text = "RESUME REST"
            self.timer_sub.text = "paused"
        else:
            # Resume it
            self.pause_rest_btn.text = "PAUSE REST"
            self.timer_label.color = c('accent2')
            self.timer_sub.text = "rest seconds"
            self.timer_event = Clock.schedule_interval(self._tick_rest, 1)

    def _restart_exercise_timer(self, *args):
        if not self.workout_started or self.paused:
            return
        self.exercise_timer_paused = False
        self.pause_exercise_btn.text = "PAUSE"
        if self.phase == 'warmup':
            item = self.day_data['warmup'][self.warmup_idx]
            duration = item.get('duration', 30)
        else:
            ex = self.day_data['exercises'][self.current_exercise_idx]
            duration = ex.get('duration', 30)
        self._start_exercise_timer(duration)

    def _start_rest_timer(self, *args):
        if not self.workout_started or self.paused:
            return
        ex = self.day_data['exercises'][self.current_exercise_idx]
        rest = ex.get('rest', 60)
        self._cancel_timer()
        self.active_timer_type = 'rest'
        self.active_timer_duration = rest
        self.timer_remaining = rest
        self.timer_box.opacity = 1
        self.timer_label.text = str(rest)
        self.timer_label.color = c('accent2')
        self.timer_sub.text = "rest seconds"
        self.timer_event = Clock.schedule_interval(self._tick_rest, 1)
        self.pause_rest_btn.text = "PAUSE REST"
        self.pause_rest_btn.opacity = 1
        self.pause_rest_btn.disabled = False

    def _tick_rest(self, dt):
        self.timer_remaining -= 1
        self.timer_label.text = str(self.timer_remaining)
        if self.timer_remaining <= 0:
            self._cancel_timer()
            self.active_timer_type = None
            self.timer_label.text = "GO!"
            self.timer_label.color = c('accent')
            self.timer_sub.text = "rest complete"
            self.pause_rest_btn.opacity = 0
            self.pause_rest_btn.disabled = True
            self.start_timer_btn.opacity = 0
            self.start_timer_btn.disabled = True
            return False

    def _cancel_timer(self):
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None
        if hasattr(self, 'timer_label'):
            self.timer_label.color = c('accent')
        return True

    def _next(self, *args):
        if not self.workout_started or self.paused:
            return
        self._cancel_timer()
        self.active_timer_type = None
        self.exercise_timer_paused = False

        if self.phase == 'warmup':
            self.warmup_idx += 1
            self._refresh_display()
            return

        exercises = self.day_data['exercises']
        ex = exercises[self.current_exercise_idx]
        self.sets_completed += 1

        if self.current_set < ex['sets']:
            self.current_set += 1
            rest = ex.get('rest', 60)
            self._refresh_display()
            # Auto-start rest timer and show pause + restart rest buttons
            self._start_rest_timer()
            self.start_timer_btn.opacity = 1
            self.start_timer_btn.disabled = False
            self.start_timer_btn.text = f"RESTART ({rest}s)"
        else:
            self.current_exercise_idx += 1
            self.current_set = 1
            self.start_timer_btn.opacity = 0
            self.start_timer_btn.disabled = True
            self.pause_rest_btn.opacity = 0
            self.pause_rest_btn.disabled = True
            self._refresh_display()

    def _workout_complete(self):
        self._cancel_timer()
        progress = load_progress()
        progress['total_workouts'] = progress.get('total_workouts', 0) + 1
        progress['total_sets'] = progress.get('total_sets', 0) + self.sets_completed
        today = str(datetime.date.today())
        last = progress.get('last_date', '')
        yesterday = str(datetime.date.today() - datetime.timedelta(days=1))
        if last == yesterday:
            progress['streak'] = progress.get('streak', 0) + 1
        elif last != today:
            progress['streak'] = 1
        progress['last_date'] = today
        completed = progress.get('completed_workouts', [])
        completed.append({'day': self.day_key, 'date': today, 'sets': self.sets_completed})
        progress['completed_workouts'] = completed[-30:]
        save_progress(progress)

        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=dp(40), spacing=dp(20))
        with layout.canvas.before:
            Color(*c('bg'))
            layout._bg = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=lambda *a: setattr(layout._bg, 'pos', layout.pos),
                    size=lambda *a: setattr(layout._bg, 'size', layout.size))

        layout.add_widget(Label(text="DONE", font_size=sp(64), size_hint_y=None, height=dp(80)))
        layout.add_widget(Label(text="WORKOUT COMPLETE!", font_size=sp(26), bold=True,
                                color=c('accent')))
        layout.add_widget(Label(text=f"{self.day_key}: {self.day_data['name']}",
                                font_size=sp(16), color=c('text_dim')))
        layout.add_widget(Label(text=f"Sets completed: {self.sets_completed}",
                                font_size=sp(18), color=c('text')))
        layout.add_widget(Label(text=f"Streak: {progress.get('streak', 1)}",
                                font_size=sp(18), color=c('accent2')))

        home_btn = FitButton(text="Back to Home")
        home_btn.bind(on_press=self._go_home)
        layout.add_widget(home_btn)
        self.add_widget(layout)

    def _go_back(self, *args):
        self._cancel_timer()
        app = App.get_running_app()
        app.root.transition = SlideTransition(direction='right')
        app.root.current = 'home'

    def _go_home(self, *args):
        app = App.get_running_app()
        app.root.transition = SlideTransition(direction='right')
        app.root.current = 'home'


class StretchScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stretch_idx = 0
        self.timer_event = None
        self.timer_remaining = 0
        self.stretch_timer_paused = False

    def on_enter(self):
        self.clear_widgets()
        self.stretch_idx = 0
        self.stretch_timer_paused = False
        self._build()

    def _build(self):
        self.root_layout = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(14))
        with self.root_layout.canvas.before:
            Color(*c('bg'))
            self._bg = Rectangle(pos=self.root_layout.pos, size=self.root_layout.size)
        self.root_layout.bind(
            pos=lambda *a: setattr(self._bg, 'pos', self.root_layout.pos),
            size=lambda *a: setattr(self._bg, 'size', self.root_layout.size))

        # Top bar
        topbar = BoxLayout(size_hint_y=None, height=dp(50))
        back_btn = Button(text="Back", size_hint_x=None, width=dp(80),
                          background_normal='', background_color=(0,0,0,0),
                          color=c('text_dim'), font_size=sp(14))
        back_btn.bind(on_press=self._go_back)
        topbar.add_widget(back_btn)
        topbar.add_widget(Label(text="Rest Day Stretch", font_size=sp(16),
                                bold=True, color=c('text')))
        self.root_layout.add_widget(topbar)

        # Stretch card
        self.stretch_card = ColoredBox(bg_color='surface', radius=20, orientation='vertical',
                                        padding=dp(24), spacing=dp(14),
                                        size_hint_y=None, height=dp(300))

        self.stretch_name = Label(text="", font_size=sp(22), bold=True,
                                   color=c('text'), halign='center')
        self.stretch_name.bind(size=self.stretch_name.setter('text_size'))
        self.stretch_card.add_widget(self.stretch_name)

        self.sides_label = Label(text="", font_size=sp(12), color=get_color_from_hex('#A78BFA'),
                                  size_hint_y=None, height=dp(20))
        self.stretch_card.add_widget(self.sides_label)

        self.timer_label = Label(text="", font_size=sp(54), bold=True, color=c('accent'),
                                  size_hint_y=None, height=dp(70))
        self.stretch_card.add_widget(self.timer_label)

        self.progress_label = Label(text="", font_size=sp(13), color=c('text_dim'),
                                     size_hint_y=None, height=dp(20))
        self.stretch_card.add_widget(self.progress_label)

        self.root_layout.add_widget(self.stretch_card)

        # Instruction
        inst_scroll = ScrollView(size_hint_y=None, height=dp(100))
        self.inst_label = Label(text="", font_size=sp(13), color=c('text_dim'),
                                 halign='center', valign='top', size_hint_y=None,
                                 padding=(dp(10), dp(6)))
        self.inst_label.bind(texture_size=self.inst_label.setter('size'))
        self.inst_label.bind(width=lambda *a: setattr(
            self.inst_label, 'text_size', (self.inst_label.width, None)))
        inst_scroll.add_widget(self.inst_label)
        self.root_layout.add_widget(inst_scroll)

        self.progress_bar = ProgressBar(max=100, value=0, size_hint_y=None, height=dp(6))
        self.root_layout.add_widget(self.progress_bar)

        btn_row = BoxLayout(size_hint_y=None, height=dp(58), spacing=dp(10))

        self.start_btn = FitButton(text="START", accent=False)
        self.start_btn.bind(on_press=self._start_timer)
        btn_row.add_widget(self.start_btn)

        self.stop_btn = FitButton(text="STOP", accent=False)
        self.stop_btn.bind(on_press=self._stop_timer)
        self.stop_btn.opacity = 0.3
        self.stop_btn.disabled = True
        btn_row.add_widget(self.stop_btn)

        self.next_btn = FitButton(text="NEXT")
        self.next_btn.bind(on_press=self._next)
        btn_row.add_widget(self.next_btn)
        self.root_layout.add_widget(btn_row)

        self.add_widget(self.root_layout)
        self._refresh()

    def _refresh(self):
        if self.stretch_idx >= len(REST_DAY_STRETCHING):
            self._complete()
            return

        s = REST_DAY_STRETCHING[self.stretch_idx]
        self.stretch_name.text = s['name']
        self.sides_label.text = "Both sides" if s.get('sides') else "Centred"
        self.timer_label.text = f"{s['duration']}s"
        self.timer_label.color = c('accent')  # reset from green DONE state
        self.inst_label.text = s.get('instruction', '')
        self.progress_label.text = f"{self.stretch_idx + 1} of {len(REST_DAY_STRETCHING)}"
        self.progress_bar.value = (self.stretch_idx / len(REST_DAY_STRETCHING)) * 100
        self.start_btn.text = "START"
        self.stop_btn.opacity = 0.3
        self.stop_btn.disabled = True
        self.stretch_timer_paused = False

    def _start_timer(self, *args):
        if self.timer_event:
            # Timer is running — PAUSE it
            self.timer_event.cancel()
            self.timer_event = None
            self.stretch_timer_paused = True
            self.start_btn.text = "RESUME"
            self.stop_btn.opacity = 1
            self.stop_btn.disabled = False
        elif self.stretch_timer_paused:
            # Timer is paused — RESUME it
            self.stretch_timer_paused = False
            self.start_btn.text = "PAUSE"
            self.timer_label.color = c('accent')
            self.timer_event = Clock.schedule_interval(self._tick, 1)
        else:
            # Timer not started yet — START it fresh
            s = REST_DAY_STRETCHING[self.stretch_idx]
            self.timer_remaining = s['duration']
            self.timer_label.text = str(self.timer_remaining)
            self.timer_label.color = c('accent')
            self.stretch_timer_paused = False
            self.timer_event = Clock.schedule_interval(self._tick, 1)
            self.start_btn.text = "PAUSE"
            self.stop_btn.opacity = 1
            self.stop_btn.disabled = False

    def _stop_timer(self, *args):
        """Stop and reset — does not advance to next stretch."""
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None
        s = REST_DAY_STRETCHING[self.stretch_idx]
        self.stretch_timer_paused = False
        self.timer_remaining = s['duration']
        self.timer_label.text = f"{s['duration']}s"
        self.timer_label.color = c('accent')
        self.start_btn.text = "START"
        self.stop_btn.opacity = 0.3
        self.stop_btn.disabled = True

    def _tick(self, dt):
        self.timer_remaining -= 1
        self.timer_label.text = str(self.timer_remaining)
        if self.timer_remaining <= 0:
            self.timer_event.cancel()
            self.timer_event = None
            self.stretch_timer_paused = False
            self.timer_label.text = "DONE"
            self.timer_label.color = c('success')
            self.start_btn.text = "RESTART"
            self.stop_btn.opacity = 0.3
            self.stop_btn.disabled = True
            return False

    def _next(self, *args):
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None
        self.stretch_timer_paused = False
        self.stretch_idx += 1
        self._refresh()

    def _complete(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=dp(40), spacing=dp(20))
        with layout.canvas.before:
            Color(*c('bg'))
            layout._bg = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=lambda *a: setattr(layout._bg, 'pos', layout.pos),
                    size=lambda *a: setattr(layout._bg, 'size', layout.size))
        layout.add_widget(Label(text="REST", font_size=sp(64), size_hint_y=None, height=dp(80)))
        layout.add_widget(Label(text="STRETCH COMPLETE!", font_size=sp(24), bold=True,
                                color=get_color_from_hex('#A78BFA')))
        layout.add_widget(Label(text="Great recovery session.\nYour body thanks you.",
                                font_size=sp(15), color=c('text_dim'), halign='center'))
        home_btn = FitButton(text="Back to Home")
        home_btn.bind(on_press=self._go_back)
        layout.add_widget(home_btn)
        self.add_widget(layout)

    def _go_back(self, *args):
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None
        app = App.get_running_app()
        app.root.transition = SlideTransition(direction='right')
        app.root.current = 'home'


# ─────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────

class EquipmentScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        self.owned = load_equipment()
        self.presets = load_presets()
        self._build()

    def _build(self):
        root = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(10))
        with root.canvas.before:
            Color(*c('bg'))
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: setattr(self._bg, 'pos', root.pos),
                  size=lambda *a: setattr(self._bg, 'size', root.size))

        topbar = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        back_btn = Button(text="Back", size_hint_x=None, width=dp(80),
                          background_normal='', background_color=(0,0,0,0),
                          color=c('text_dim'), font_size=sp(14))
        back_btn.bind(on_press=self._go_back)
        topbar.add_widget(back_btn)
        topbar.add_widget(Label(text="My Equipment", font_size=sp(18),
                                bold=True, color=c('text')))
        root.add_widget(topbar)

        root.add_widget(Label(
            text="Load a location preset or toggle items individually.",
            font_size=sp(13), color=c('text_dim'), halign='center',
            size_hint_y=None, height=dp(22)))

        # ── Location presets ──
        preset_label = Label(text="PRESETS", font_size=sp(11), bold=True,
                             color=c('accent'), halign='left', valign='middle',
                             size_hint_y=None, height=dp(24))
        preset_label.bind(size=preset_label.setter('text_size'))
        root.add_widget(preset_label)

        # Store ref so we can rebuild just the preset row on save/delete
        self.preset_scroll_holder = BoxLayout(orientation='vertical',
                                              size_hint_y=None, height=dp(56))
        root.add_widget(self.preset_scroll_holder)
        self._build_preset_row()

        # ── Individual toggles ──
        toggle_label = Label(text="ALL EQUIPMENT", font_size=sp(11), bold=True,
                             color=c('accent'), halign='left', valign='middle',
                             size_hint_y=None, height=dp(24))
        toggle_label.bind(size=toggle_label.setter('text_size'))
        root.add_widget(toggle_label)

        self.scroll = ScrollView()
        self.items_layout = BoxLayout(orientation='vertical', spacing=dp(6),
                                      size_hint_y=None, padding=(0, dp(4)))
        self.items_layout.bind(minimum_height=self.items_layout.setter('height'))
        self.toggle_buttons = {}
        self._populate_toggles()
        self.scroll.add_widget(self.items_layout)
        root.add_widget(self.scroll)

        save_btn = FitButton(text="SAVE EQUIPMENT")
        save_btn.bind(on_press=self._save)
        root.add_widget(save_btn)

        self.add_widget(root)

    def _build_preset_row(self):
        self.preset_scroll_holder.clear_widgets()
        preset_scroll = ScrollView(do_scroll_y=False)
        preset_row = BoxLayout(orientation='horizontal', spacing=dp(8),
                               size_hint_x=None, padding=(0, dp(4)))
        preset_row.bind(minimum_width=preset_row.setter('width'))

        for name, data in self.presets.items():
            preset_row.add_widget(self._make_preset_chip(name, data["keys"]))

        new_btn = Button(
            text="+ New", font_size=sp(11), bold=True,
            size_hint=(None, None), width=dp(80), height=dp(44),
            background_normal='', background_color=(0,0,0,0),
            color=c('accent'))
        with new_btn.canvas.before:
            Color(*c('surface'))
            new_btn._rect = RoundedRectangle(pos=new_btn.pos, size=new_btn.size, radius=[dp(10)])
        new_btn.bind(pos=lambda i, *a: setattr(i._rect, 'pos', i.pos),
                     size=lambda i, *a: setattr(i._rect, 'size', i.size))
        new_btn.bind(on_press=self._new_preset)
        preset_row.add_widget(new_btn)

        preset_scroll.add_widget(preset_row)
        self.preset_scroll_holder.add_widget(preset_scroll)

    def _make_preset_chip(self, name, keys):
        chip = BoxLayout(orientation='horizontal', spacing=dp(0),
                         size_hint=(None, None), width=dp(152), height=dp(44))

        load_btn = Button(
            text=name, font_size=sp(11), bold=True,
            size_hint_x=1, height=dp(44),
            background_normal='', background_color=(0,0,0,0),
            color=c('text'))
        with load_btn.canvas.before:
            Color(*c('surface2'))
            load_btn._rect = RoundedRectangle(pos=load_btn.pos, size=load_btn.size,
                                              radius=[dp(10), dp(2), dp(2), dp(10)])
        load_btn.bind(pos=lambda i, *a: setattr(i._rect, 'pos', i.pos),
                      size=lambda i, *a: setattr(i._rect, 'size', i.size))

        def load_it(instance, preset_keys=keys, btn=load_btn):
            self.owned = set(preset_keys)
            self._rebuild_toggles()
            btn.color = c('accent')
            Clock.schedule_once(lambda *a: setattr(btn, 'color', c('text')), 0.5)

        load_btn.bind(on_press=load_it)
        chip.add_widget(load_btn)

        edit_btn = Button(
            text="...", font_size=sp(13), bold=True,
            size_hint=(None, None), width=dp(32), height=dp(44),
            background_normal='', background_color=(0,0,0,0),
            color=c('text_dim'))
        with edit_btn.canvas.before:
            Color(*c('surface2'))
            edit_btn._rect = RoundedRectangle(pos=edit_btn.pos, size=edit_btn.size,
                                              radius=[dp(2), dp(10), dp(10), dp(2)])
        edit_btn.bind(pos=lambda i, *a: setattr(i._rect, 'pos', i.pos),
                      size=lambda i, *a: setattr(i._rect, 'size', i.size))
        edit_btn.bind(on_press=lambda *a, n=name: self._open_preset_editor(n))
        chip.add_widget(edit_btn)
        return chip

    def _open_preset_editor(self, name):
        from kivy.uix.textinput import TextInput
        preset_data = self.presets.get(name, {"keys": set(), "desc": ""})
        editing_keys = set(preset_data["keys"])

        root = BoxLayout(orientation='vertical', spacing=dp(0))
        with root.canvas.before:
            Color(*c('bg'))
            root._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: setattr(root._bg, 'pos', root.pos),
                  size=lambda *a: setattr(root._bg, 'size', root.size))

        topbar = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(10),
                           padding=[dp(12), dp(8)])
        cancel_btn = Button(text="Cancel", size_hint_x=None, width=dp(72),
                            background_normal='', background_color=(0,0,0,0),
                            color=c('text_dim'), font_size=sp(13))
        title_lbl = Label(text='Edit Preset', font_size=sp(16), bold=True, color=c('text'))
        save_btn = Button(text="Save", size_hint_x=None, width=dp(56),
                          background_normal='', background_color=(0,0,0,0),
                          color=c('accent'), font_size=sp(14), bold=True)
        topbar.add_widget(cancel_btn)
        topbar.add_widget(title_lbl)
        topbar.add_widget(save_btn)
        root.add_widget(topbar)

        name_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10),
                             padding=[dp(12), dp(4)])
        name_input = TextInput(
            text=name, font_size=sp(13), multiline=False,
            background_color=c('surface'), foreground_color=c('text'),
            cursor_color=c('accent'), hint_text_color=c('text_dim'),
            hint_text="Preset name", padding=[dp(10), dp(10)])
        name_row.add_widget(name_input)
        root.add_widget(name_row)

        eq_lbl = Label(text="EQUIPMENT IN THIS PRESET", font_size=sp(10), bold=True,
                       color=c('accent'), halign='left', valign='middle',
                       size_hint_y=None, height=dp(28), padding=[dp(12), 0])
        eq_lbl.bind(size=eq_lbl.setter('text_size'))
        root.add_widget(eq_lbl)

        scroll = ScrollView()
        eq_layout = BoxLayout(orientation='vertical', spacing=dp(2),
                              size_hint_y=None,
                              padding=[dp(12), dp(4), dp(12), dp(12)])
        eq_layout.bind(minimum_height=eq_layout.setter('height'))

        groups = {}
        for key, info in ALL_EQUIPMENT.items():
            groups.setdefault(info['group'], []).append((key, info))

        for group_name, items in groups.items():
            grp_lbl = Label(text=group_name.upper(), font_size=sp(10), bold=True,
                            color=c('text_dim'), halign='left', valign='middle',
                            size_hint_y=None, height=dp(26))
            grp_lbl.bind(size=grp_lbl.setter('text_size'))
            eq_layout.add_widget(grp_lbl)

            for key, info in items:
                in_preset = key in editing_keys
                row = BoxLayout(orientation='horizontal', size_hint_y=None,
                                height=dp(38), spacing=dp(10))
                lbl = Label(text=info['label'], font_size=sp(13), color=c('text'),
                            halign='left', valign='middle')
                lbl.bind(size=lbl.setter('text_size'))

                tog = Button(
                    text="YES" if in_preset else "NO",
                    font_size=sp(11), bold=True,
                    size_hint=(None, None), width=dp(52), height=dp(30),
                    background_normal='', background_color=(0,0,0,0),
                    color=c('accent') if in_preset else c('text_dim'))
                with tog.canvas.before:
                    _color = Color(*(c('surface') if in_preset else c('surface2')))
                    tog._bg = RoundedRectangle(pos=tog.pos, size=tog.size, radius=[dp(8)])
                tog.bind(pos=lambda i, *a: setattr(i._bg, 'pos', i.pos),
                         size=lambda i, *a: setattr(i._bg, 'size', i.size))

                def make_toggle(k, btn, color_instr):
                    def toggle(*a):
                        if k in editing_keys:
                            editing_keys.discard(k)
                            btn.text = "NO"
                            btn.color = c('text_dim')
                            color_instr.rgba = c('surface2')
                        else:
                            editing_keys.add(k)
                            btn.text = "YES"
                            btn.color = c('accent')
                            color_instr.rgba = c('surface')
                    return toggle

                tog.bind(on_press=make_toggle(key, tog, _color))
                row.add_widget(lbl)
                row.add_widget(tog)
                eq_layout.add_widget(row)

        scroll.add_widget(eq_layout)
        root.add_widget(scroll)

        del_btn = Button(
            text="Delete This Preset", font_size=sp(13), bold=True,
            background_normal='', background_color=(0,0,0,0),
            color=c('danger'), size_hint_y=None, height=dp(48))
        root.add_widget(del_btn)

        popup = Popup(title="", content=root, size_hint=(1, 1),
                      background_color=c('bg'),
                      title_color=c('bg'), separator_height=0)

        def do_save(*a):
            new_name = name_input.text.strip()
            if not new_name:
                name_input.hint_text = "Please enter a name"
                return
            if new_name != name and new_name in self.presets:
                name_input.text = ""
                name_input.hint_text = "That name already exists"
                return
            if new_name != name:
                self.presets.pop(name, None)
            self.presets[new_name] = {"keys": set(editing_keys), "desc": ""}
            save_presets(self.presets)
            popup.dismiss()
            self._build_preset_row()

        def do_delete(*a):
            popup.dismiss()
            self._confirm_delete_preset(name)

        cancel_btn.bind(on_press=popup.dismiss)
        save_btn.bind(on_press=do_save)
        name_input.bind(on_text_validate=do_save)
        del_btn.bind(on_press=do_delete)
        popup.open()

    def _new_preset(self, *args):
        from kivy.uix.textinput import TextInput
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        content.add_widget(Label(text="New preset name:", font_size=sp(14),
                                 color=c('text'), size_hint_y=None, height=dp(28)))
        name_input = TextInput(
            hint_text="e.g. My Garage, Airbnb...",
            font_size=sp(14), multiline=False,
            background_color=c('surface2'), foreground_color=c('text'),
            cursor_color=c('accent'), hint_text_color=c('text_dim'),
            size_hint_y=None, height=dp(42), padding=[dp(10), dp(10)])
        content.add_widget(name_input)

        content.add_widget(Label(text="Start with:", font_size=sp(12),
                                 color=c('text_dim'), size_hint_y=None, height=dp(20)))
        seed_row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        seed_current = Button(text="Current selection", font_size=sp(12), bold=True,
                              background_normal='', background_color=c('accent'),
                              color=c('bg'))
        seed_blank = Button(text="Blank (nothing)", font_size=sp(12), bold=True,
                            background_normal='', background_color=c('surface2'),
                            color=c('text_dim'))
        seed_row.add_widget(seed_current)
        seed_row.add_widget(seed_blank)
        content.add_widget(seed_row)

        btn_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(10))
        cancel_btn = Button(text="Cancel", background_normal='',
                            background_color=c('surface2'), color=c('text'),
                            bold=True, font_size=sp(13))
        create_btn = Button(text="Create & Edit", background_normal='',
                            background_color=c('accent'), color=c('bg'),
                            bold=True, font_size=sp(13))
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(create_btn)
        content.add_widget(btn_row)

        seed_choice = [set(self.owned)]

        def pick_current(*a):
            seed_choice[0] = set(self.owned)
            seed_current.background_color = c('accent')
            seed_current.color = c('bg')
            seed_blank.background_color = c('surface2')
            seed_blank.color = c('text_dim')

        def pick_blank(*a):
            seed_choice[0] = set()
            seed_blank.background_color = c('accent')
            seed_blank.color = c('bg')
            seed_current.background_color = c('surface2')
            seed_current.color = c('text_dim')

        seed_current.bind(on_press=pick_current)
        seed_blank.bind(on_press=pick_blank)

        popup = Popup(title="New Preset", content=content,
                      size_hint=(0.90, None), height=dp(290),
                      background_color=c('surface'),
                      title_color=c('text'), separator_color=c('accent'))
        cancel_btn.bind(on_press=popup.dismiss)

        def do_create(*a):
            name = name_input.text.strip()
            if not name:
                name_input.hint_text = "Please enter a name"
                return
            if name in self.presets:
                name_input.text = ""
                name_input.hint_text = "That name already exists"
                return
            self.presets[name] = {"keys": seed_choice[0], "desc": ""}
            save_presets(self.presets)
            popup.dismiss()
            self._build_preset_row()
            Clock.schedule_once(lambda *a: self._open_preset_editor(name), 0.15)

        create_btn.bind(on_press=do_create)
        name_input.bind(on_text_validate=do_create)
        popup.open()
        Clock.schedule_once(lambda *a: setattr(name_input, 'focus', True), 0.2)

    def _confirm_delete_preset(self, name):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(14))
        content.add_widget(Label(text=f'Delete "{name}"?', font_size=sp(14),
                                 color=c('text'), halign='center',
                                 size_hint_y=None, height=dp(32)))
        btn_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(10))
        cancel_btn = Button(text="Cancel", background_normal='',
                            background_color=c('surface2'), color=c('text'),
                            bold=True, font_size=sp(13))
        del_btn = Button(text="Delete", background_normal='',
                         background_color=c('danger'), color=c('text'),
                         bold=True, font_size=sp(13))
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(del_btn)
        content.add_widget(btn_row)
        popup = Popup(title="Delete Preset", content=content,
                      size_hint=(0.82, None), height=dp(190),
                      background_color=c('surface'),
                      title_color=c('text'), separator_color=c('danger'))
        cancel_btn.bind(on_press=popup.dismiss)

        def do_delete(*a):
            self.presets.pop(name, None)
            save_presets(self.presets)
            popup.dismiss()
            self._build_preset_row()

        del_btn.bind(on_press=do_delete)
        popup.open()

    def _populate_toggles(self):
        self.items_layout.clear_widgets()
        self.toggle_buttons = {}
        groups = {}
        for key, info in ALL_EQUIPMENT.items():
            groups.setdefault(info['group'], []).append((key, info))
        for group_name, items in groups.items():
            header = Label(text=group_name.upper(), font_size=sp(11), bold=True,
                           color=c('accent'), halign='left', valign='middle',
                           size_hint_y=None, height=dp(26))
            header.bind(size=header.setter('text_size'))
            self.items_layout.add_widget(header)
            for key, info in items:
                self.items_layout.add_widget(self._make_toggle_row(key, info))

    def _rebuild_toggles(self):
        """Refresh all toggle rows after a preset load without full screen rebuild."""
        self._populate_toggles()

    def _make_toggle_row(self, key, info):
        is_owned = key in self.owned
        row = ColoredBox(
            bg_color='surface' if is_owned else 'surface2',
            radius=12, orientation='horizontal',
            size_hint_y=None, height=dp(54),
            padding=dp(14), spacing=dp(12))
        row.equipment_key = key

        row.add_widget(Label(text=info['label'], font_size=sp(14),
                              color=c('text') if is_owned else c('text_dim'),
                              halign='left', valign='middle'))

        status = Label(
            text="+ HAVE IT" if is_owned else "- DON'T HAVE",
            font_size=sp(11), bold=True,
            color=c('accent') if is_owned else c('text_dim'),
            size_hint_x=None, width=dp(90), halign='right')
        row.add_widget(status)

        self.toggle_buttons[key] = (row, status)

        def on_tap(instance, touch, k=key):
            if instance.collide_point(*touch.pos):
                if k in self.owned:
                    self.owned.discard(k)
                else:
                    self.owned.add(k)
                r, s = self.toggle_buttons[k]
                owned_now = k in self.owned
                s.text = "+ HAVE IT" if owned_now else "- DON'T HAVE"
                s.color = c('accent') if owned_now else c('text_dim')
                r.bg_color = 'surface' if owned_now else 'surface2'
                r._update()
                return True

        row.bind(on_touch_down=on_tap)
        return row

    def _save(self, *args):
        save_equipment(self.owned)
        self._go_back()

    def _go_back(self, *args):
        app = App.get_running_app()
        app.root.transition = SlideTransition(direction='right')
        app.root.current = 'home'


class MenuScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        self._build()

    def _build(self):
        root = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(0))
        with root.canvas.before:
            Color(*c('bg'))
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: setattr(self._bg, 'pos', root.pos),
                  size=lambda *a: setattr(self._bg, 'size', root.size))

        # ── Top bar ──
        topbar = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(10))
        back_btn = Button(text="Back", size_hint_x=None, width=dp(80),
                          background_normal='', background_color=(0,0,0,0),
                          color=c('text_dim'), font_size=sp(14))
        back_btn.bind(on_press=self._go_back)
        topbar.add_widget(back_btn)
        topbar.add_widget(Label(text="Menu", font_size=sp(20), bold=True, color=c('text')))
        root.add_widget(topbar)

        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=dp(12),
                            size_hint_y=None, padding=(0, dp(8)))
        content.bind(minimum_height=content.setter('height'))

        # ── App info card ──
        info_card = ColoredBox(bg_color='surface', radius=16, orientation='vertical',
                               padding=dp(20), spacing=dp(6),
                               size_hint_y=None, height=dp(110))
        info_card.add_widget(Label(text="FITFORGE", font_size=sp(22), bold=True,
                                   color=c('accent')))
        info_card.add_widget(Label(text="Version {}".format(APP_VERSION),
                                   font_size=sp(13), color=c('text_dim')))
        info_card.add_widget(Label(
            text="Built for your training. Adapts to your gear.",
            font_size=sp(12), color=c('text_dim'), halign='center'))
        content.add_widget(info_card)

        # ── Menu items ──
        menu_items = [
            ("Equipment Manager",  "Manage your gear & load location presets", self._go_equipment, c('accent2')),
            ("Changelog",          "What's new in each version",              self._show_changelog, c('accent')),
            ("Reset Progress",     "Clear all workout history and streak",    self._confirm_reset,  c('danger')),
            ("Exit App",           "Close FitForge",                          self._exit_app,       c('danger')),
        ]

        for label, desc, action, color in menu_items:
            row = ColoredBox(bg_color='surface', radius=14, orientation='horizontal',
                             size_hint_y=None, height=dp(72),
                             padding=dp(16), spacing=dp(12))

            left = BoxLayout(orientation='vertical', spacing=dp(2))
            left.add_widget(Label(text=label, font_size=sp(16), bold=True,
                                  color=color, halign='left', valign='middle'))
            left.add_widget(Label(text=desc, font_size=sp(11), color=c('text_dim'),
                                  halign='left', valign='middle'))
            row.add_widget(left)
            row.add_widget(Label(text=">", font_size=sp(20), bold=True, color=c('text_dim'),
                                 size_hint_x=None, width=dp(20)))

            def make_tap(fn):
                def on_tap(instance, touch):
                    if instance.collide_point(*touch.pos) and touch.grab_current is None:
                        fn()
                        return True
                return on_tap

            row.bind(on_touch_up=make_tap(action))
            content.add_widget(row)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def _go_back(self, *args):
        app = App.get_running_app()
        app.root.transition = SlideTransition(direction='right')
        app.root.current = 'home'

    def _go_equipment(self):
        app = App.get_running_app()
        app.root.transition = SlideTransition(direction='left')
        app.root.current = 'equipment'

    def _show_changelog(self):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
        with root.canvas.before:
            Color(*c('bg'))
            Rectangle(pos=root.pos, size=root.size)

        topbar = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(10))
        back_btn = Button(text="Menu", size_hint_x=None, width=dp(80),
                          background_normal='', background_color=(0,0,0,0),
                          color=c('text_dim'), font_size=sp(14))
        back_btn.bind(on_press=lambda *a: self.on_enter())
        topbar.add_widget(back_btn)
        topbar.add_widget(Label(text="Changelog", font_size=sp(20), bold=True,
                                color=c('text')))
        root.add_widget(topbar)

        scroll = ScrollView()
        log_layout = BoxLayout(orientation='vertical', spacing=dp(14),
                               size_hint_y=None, padding=(0, dp(4)))
        log_layout.bind(minimum_height=log_layout.setter('height'))

        for entry in CHANGELOG:
            # ── Card with dynamic height ──
            card = ColoredBox(bg_color='surface', radius=14, orientation='vertical',
                              size_hint_y=None, padding=dp(16), spacing=dp(8))
            card.bind(minimum_height=card.setter('height'))

            header_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(32))
            header_row.add_widget(Label(
                text="v{}".format(entry['version']), font_size=sp(16), bold=True,
                color=c('accent'), size_hint_x=None, width=dp(60)))
            header_row.add_widget(Label(
                text=entry['date'], font_size=sp(13), color=c('text_dim'),
                halign='left', valign='middle'))
            card.add_widget(header_row)

            for change in entry['changes']:
                # ── FIX: Label auto-sizes its height based on rendered texture ──
                change_label = Label(
                    text="•  " + change, font_size=sp(12), color=c('text'),
                    halign='left', valign='top', size_hint_y=None)
                change_label.bind(
                    width=lambda lbl, w: setattr(lbl, 'text_size', (w, None)),
                    texture_size=lambda lbl, ts: setattr(lbl, 'height', ts[1]))
                card.add_widget(change_label)

            log_layout.add_widget(card)

        scroll.add_widget(log_layout)
        root.add_widget(scroll)
        self.add_widget(root)

    def _confirm_reset(self):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(16))
        content.add_widget(Label(
            text="Reset all progress?\nThis clears your streak, workout\nhistory, and set counts.",
            font_size=sp(14), color=c('text'), halign='center'))
        btn_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        cancel = Button(text="Cancel", background_normal='',
                        background_color=c('surface2'), color=c('text'),
                        bold=True, font_size=sp(14))
        confirm = Button(text="Reset Everything", background_normal='',
                         background_color=c('danger'), color=c('text'),
                         bold=True, font_size=sp(14))
        btn_row.add_widget(cancel)
        btn_row.add_widget(confirm)
        content.add_widget(btn_row)
        popup = Popup(title="Reset Progress", content=content,
                      size_hint=(0.88, None), height=dp(240),
                      background_color=c('surface'),
                      title_color=c('text'), separator_color=c('danger'))
        cancel.bind(on_press=popup.dismiss)
        def do_reset(*a):
            save_progress({"completed_workouts": [], "total_sets": 0,
                           "total_workouts": 0, "streak": 0, "last_date": ""})
            popup.dismiss()
        confirm.bind(on_press=do_reset)
        popup.open()

    def _exit_app(self):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(16))
        content.add_widget(Label(text="Exit FitForge?", font_size=sp(16),
                                 color=c('text'), halign='center'))
        btn_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        cancel = Button(text="Stay", background_normal='',
                        background_color=c('surface2'), color=c('text'),
                        bold=True, font_size=sp(14))
        confirm = Button(text="Exit", background_normal='',
                         background_color=c('danger'), color=c('text'),
                         bold=True, font_size=sp(14))
        btn_row.add_widget(cancel)
        btn_row.add_widget(confirm)
        content.add_widget(btn_row)
        popup = Popup(title="Exit App", content=content,
                      size_hint=(0.8, None), height=dp(200),
                      background_color=c('surface'),
                      title_color=c('text'), separator_color=c('danger'))
        cancel.bind(on_press=popup.dismiss)
        confirm.bind(on_press=lambda *a: App.get_running_app().stop())
        popup.open()


class FitForgeApp(App):
    current_day = StringProperty("Day 1")

    def build(self):
        Window.clearcolor = c('bg')
        self.title = "FitForge"

        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(WorkoutScreen(name='workout'))
        sm.add_widget(StretchScreen(name='stretch'))
        sm.add_widget(EquipmentScreen(name='equipment'))
        sm.add_widget(MenuScreen(name='menu'))
        return sm


if __name__ == '__main__':
    FitForgeApp().run()
