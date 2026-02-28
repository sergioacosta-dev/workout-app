"""
FitForge - Full Body Workout App v1.5.0
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
from kivy.core.audio import SoundLoader
from kivy.metrics import dp, sp
from kivy.properties import StringProperty
import json
import os
import datetime

COLORS = {
    'bg':       '#0D0F14',
    'surface':  '#161A24',
    'surface2': '#1E2433',
    'accent':   '#E8FF47',
    'accent2':  '#47FFD4',
    'danger':   '#FF4757',
    'text':     '#F0F4FF',
    'text_dim': '#7A8599',
    'card':     '#1A1F2E',
    'success':  '#2ECC71',
}

def c(key):
    return get_color_from_hex(COLORS[key])


WORKOUT_PLAN = {
    "Day 1": {
        "name": "Push + Core", "color": "#E8FF47",
        "warmup": [
            {"name": "Jump Rope", "duration": 300, "type": "timed",
             "instruction": "Easy pace, focus on rhythm. Land softly on the balls of your feet. Keep elbows close to your sides. Gets your heart rate up and primes the whole body."},
            {"name": "Arm Circles — Forward", "duration": 30, "type": "timed",
             "instruction": "Arms straight out, make big slow forward circles. Progressively wider. Opens the shoulder joint before pressing work."},
            {"name": "Arm Circles — Backward", "duration": 30, "type": "timed",
             "instruction": "Same motion, reverse direction. You'll feel the rear deltoid and rotator cuff engage. Keep your neck relaxed."},
            {"name": "Hip Circles", "reps": "10 each direction", "type": "reps",
             "instruction": "Hands on hips, feet shoulder-width. Big slow circles — forward 10, backward 10. Loosens hip flexors and lower back."},
            {"name": "Walkouts", "reps": "5 reps", "type": "reps",
             "instruction": "Hinge forward, walk hands to plank, hold 2 seconds, walk back. Warms up shoulders, hamstrings, and core all at once."},
            {"name": "Lateral Lunges", "reps": "10 per side", "type": "reps",
             "instruction": "Step wide, sink hips down, reach opposite arm across toward foot. Hold 1 second at bottom. Opens groin and hip flexors."},
            {"name": "Shoulder Rotations", "reps": "10 per direction", "type": "reps",
             "instruction": "Hold a band wide with both hands, arms straight. Bring overhead and behind back if mobility allows. Reverse. Primes shoulder for pressing."},
            {"name": "Push-Up Plank Hold", "duration": 20, "type": "timed",
             "instruction": "Get into push-up position and hold. Straight line head to heels, core tight, glutes squeezed. Activates everything before your first working set."},
        ],
        "exercises": [],
    },
    "Day 2": {
        "name": "Pull + Biceps", "color": "#47FFD4",
        "warmup": [
            {"name": "Jump Rope", "duration": 120, "type": "timed",
             "instruction": "Easy pace to get blood flowing. Relaxed shoulders, light landings. 2 minutes primes the system before pull work."},
            {"name": "Arm Circles — Forward", "duration": 30, "type": "timed",
             "instruction": "Big slow forward circles. Opens the shoulder capsule and rotator cuff — essential before pulling movements."},
            {"name": "Arm Circles — Backward", "duration": 30, "type": "timed",
             "instruction": "Reverse direction. Targets the rear deltoids and external rotators you'll be using heavily today."},
            {"name": "Band Pull-Aparts", "reps": "20 reps", "type": "reps",
             "instruction": "Hold band at chest width, arms straight. Pull apart until band touches chest, squeezing shoulder blades. Your single best pre-pull warm-up movement."},
            {"name": "Hip Circles", "reps": "10 each direction", "type": "reps",
             "instruction": "Big slow circles both ways. Loosens the hip joint and lower back before the bent-over rowing position."},
            {"name": "Dead Hang — Short", "duration": 15, "type": "timed",
             "instruction": "Hang from the bar for 15 seconds. Let shoulders decompress and grip wake up. Activation set before the real pull-up work."},
            {"name": "Scapular Pull-Ups", "reps": "8 reps", "type": "reps",
             "instruction": "Hang from bar, straight arms. Without bending elbows, retract shoulder blades — you'll rise just a couple inches. Isolates lat activation."},
            {"name": "Walkouts", "reps": "5 reps", "type": "reps",
             "instruction": "Hinge forward, walk hands to plank, hold 2 seconds, walk back. Warms up the posterior chain loaded during bent-over rows."},
        ],
        "exercises": [],
    },
    "Day 3": {
        "name": "Legs + Glutes", "color": "#FF6B9D",
        "warmup": [
            {"name": "Jump Rope", "duration": 120, "type": "timed",
             "instruction": "2 minutes easy. Warms up ankles and calves which take a beating in squats and lunges. Land softly and rhythmically."},
            {"name": "Leg Swings — Forward & Back", "reps": "10 per leg", "type": "reps",
             "instruction": "Hold wall for balance. Swing one leg forward and back like a pendulum, increasing range. 10 reps per leg. Loosens hip flexor and hamstring."},
            {"name": "Leg Swings — Side to Side", "reps": "10 per leg", "type": "reps",
             "instruction": "Same wall hold. Swing leg across body and out to the side. 10 reps per leg. Targets adductors and outer hip."},
            {"name": "Hip Circles", "reps": "10 each direction", "type": "reps",
             "instruction": "Feet wide, big slow circles both ways. Opens the hip joint before goblet squat and RDL loading."},
            {"name": "Lateral Lunges", "reps": "10 per side", "type": "reps",
             "instruction": "Bodyweight only. Sink as deep as you can, hold 1 second at bottom. Adductor stretch is your best prep for goblet squat depth."},
            {"name": "Glute Bridges — Bodyweight", "reps": "15 reps", "type": "reps",
             "instruction": "No weights. Drive hips up, squeeze glutes hard at top. Glute activation warm-up — if glutes don't fire, your lower back takes the load instead."},
            {"name": "Bodyweight Squat", "reps": "10 reps", "type": "reps",
             "instruction": "Full depth, chest tall, pause 1 second at bottom. Pure movement prep — slow and controlled to open ankle and hip."},
            {"name": "Hip Flexor Stretch", "duration": 20, "type": "timed",
             "instruction": "Kneel on one knee, other foot forward. Push hips forward until you feel stretch in front of back-leg hip. 20 seconds per side. Tight hip flexors are the #1 reason squats go wrong."},
        ],
        "exercises": [],
    },
    "Day 4": {
        "name": "Full Body + Conditioning", "color": "#FF8C42",
        "warmup": [
            {"name": "Jump Rope", "duration": 180, "type": "timed",
             "instruction": "3 minutes — start easy, build pace in the last minute. Highest intensity day so this warm-up matters most. Don't skip a second of it."},
            {"name": "Arm Circles — Forward", "duration": 30, "type": "timed",
             "instruction": "Big forward circles, progressively wider. Today hits chest, back, and shoulders all in one session — this opens everything at once."},
            {"name": "Arm Circles — Backward", "duration": 30, "type": "timed",
             "instruction": "Reverse direction. Pay attention to any shoulder tightness — today's pressing and pulling in the same circuit puts extra demand on the joint."},
            {"name": "Hip Circles", "reps": "10 each direction", "type": "reps",
             "instruction": "Big slow circles both ways. Full body day means full body warm-up — the hips are the hinge of everything."},
            {"name": "Walkouts", "reps": "5 reps", "type": "reps",
             "instruction": "Slow and deliberate. Warms up shoulders, hamstrings, and core simultaneously. Pause 2 seconds in the plank."},
            {"name": "Lateral Lunges", "reps": "10 per side", "type": "reps",
             "instruction": "Get hips and adductors ready. Reach opposite arm across as you lunge. Today's circuit is relentless — walk in ready."},
            {"name": "Bodyweight Squat", "reps": "10 reps", "type": "reps",
             "instruction": "Full depth, slow, controlled. Primes the pattern for dumbbell thrusters. Focus on sitting back, not just bending your knees."},
            {"name": "Push-Up Plank Hold", "duration": 20, "type": "timed",
             "instruction": "Final activation. Straight plank, core braced hard. You are about to work — this is your last moment of stillness."},
        ],
        "exercises": [],
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
     "instruction": "On all fours, slide one arm under body along the floor. Rotate upper back. Targets thoracic spine and rear shoulder."},
    {"name": "Neck Stretch", "duration": 30, "sides": True,
     "instruction": "Drop one ear toward shoulder. Then look down toward your armpit. Never force — let gravity do the work."},
    {"name": "Pigeon Pose", "duration": 90, "sides": True,
     "instruction": "From plank, bring one knee forward toward wrist. Sink hips down. 90 seconds per side — your most important stretch."},
    {"name": "Lying Hamstring Stretch", "duration": 45, "sides": True,
     "instruction": "Loop band around foot. Lie on back, keep leg straight, gently pull toward you. Breathe and let the muscle release."},
    {"name": "Butterfly Stretch", "duration": 60, "sides": False,
     "instruction": "Soles of feet together, press knees toward floor, hinge forward at hips. Opens inner groin and hips."},
    {"name": "Child's Pose", "duration": 90, "sides": False,
     "instruction": "Arms extended or alongside body. Focus on lower back decompressing. Breathe deeply — exhale and sink further each breath."},
    {"name": "Supine Spinal Twist", "duration": 45, "sides": True,
     "instruction": "On your back, bring one knee across body, look the opposite direction. Feel the rotation through your entire spine."},
]

BAG_WARMUP = [
    {"name": "Footwork Ladder Drill", "duration": 60, "type": "timed",
     "instruction": "Stay on the balls of your feet. Practice in-out, side-to-side, and pivot steps in front of the bag. Hands up in guard. No punching yet — build rhythm and weight transfer."},
    {"name": "Shadow Boxing — Movement Only", "duration": 60, "type": "timed",
     "instruction": "Move around an imaginary opponent. No punches — just footwork, head movement, and slipping. Stay loose, knees slightly bent, chin tucked."},
    {"name": "Jab Only — Bag Work", "duration": 60, "type": "timed",
     "instruction": "Step in, throw a crisp jab, step out. Focus on extension and retraction — snap it back as fast as you throw it. Rear hand stays at your chin."},
    {"name": "Jab / Cross Combos", "duration": 60, "type": "timed",
     "instruction": "1-2 combinations at 60% power. Step forward on the jab, drive hips through the cross. Return to guard immediately. Breathe out sharply on every punch."},
    {"name": "Shadow Boxing — Full Combos", "duration": 60, "type": "timed",
     "instruction": "String together 3–5 punch combinations in the air. Add head movement between combos — slip left, slip right, roll under. Stay light on your feet."},
    {"name": "Footwork — Circle & Cut", "duration": 45, "type": "timed",
     "instruction": "Circle the bag continuously, cutting angles every few steps. Pivot off your lead foot to change direction. A moving target is harder to hit."},
    {"name": "Timed Round — Bag Work", "duration": 180, "type": "timed",
     "instruction": "3-minute round at full intensity. Mix jabs, crosses, body shots, and movement. Work the whole bag — high, mid, and low. By the end you should be fully warmed up and winded."},
    {"name": "Shake Out & Breathe", "duration": 30, "type": "timed",
     "instruction": "Drop your hands, shake out arms and shoulders, roll your neck gently. Breathe deeply — in through nose, out through mouth. Let heart rate settle."},
]


PROGRESS_FILE = "workout_progress.json"
EQUIPMENT_FILE = "equipment.json"
PRESETS_FILE = "presets.json"
APP_VERSION = "1.5.0"

CHANGELOG = [
    {"version": "1.5.0", "date": "Feb 2026", "changes": [
        "Equipment selection now fully drives the workout — every exercise slot has variations",
        "All exercises route through the variation resolver — no more hardcoded static exercises",
        "Workout buttons redesigned to a clean single row: Pause | Stop | Done",
        "Pause button label updates contextually for exercise timer vs rest timer",
    ]},
    {"version": "1.4.0", "date": "Feb 2026", "changes": [
        "Added Punching Bag to equipment — detects ownership automatically",
        "Bag warmup mode: 8 rounds of footwork, combos, shadow boxing, and timed rounds",
        "Warmup choice popup appears at the start of any workout when punching bag is selected",
    ]},
    {"version": "1.3.0", "date": "Feb 2026", "changes": [
        "Expanded equipment library to 60+ items covering every training environment",
        "Added location presets (Home, Gym, Park, Office)",
        "Added app menu with exit, version info, and changelog",
        "Equipment screen now grouped and scrollable with preset quick-load",
    ]},
    {"version": "1.2.0", "date": "Feb 2026", "changes": [
        "Full equipment system — exercises auto-adapt to what you own",
        "13 exercise types each with 4–6 variations from full equipment to bodyweight",
        "Equipment saved to disk and loaded on every workout start",
    ]},
    {"version": "1.1.0", "date": "Feb 2026", "changes": [
        "Expanded warmup routines — 8 movements per day, specifically chosen per workout",
        "Warmup complete transition screen before workout begins",
        "Start / Pause / Stop workout controls with confirmation dialog",
        "Rest timers auto-start between sets with restart button",
    ]},
    {"version": "1.0.0", "date": "Feb 2026", "changes": [
        "Initial release with 4-day workout split + rest day stretching",
        "Exercise instructions for every movement",
        "Workout progress tracking with streak counter",
        "Dark theme UI with per-day accent colours",
    ]},
]

ALL_EQUIPMENT = {
    "jump_rope":          {"label": "Jump Rope",                "group": "Cardio"},
    "punching_bag":       {"label": "Punching Bag",             "group": "Cardio"},
    "treadmill":          {"label": "Treadmill",                "group": "Cardio"},
    "stationary_bike":    {"label": "Stationary Bike",          "group": "Cardio"},
    "rowing_machine":     {"label": "Rowing Machine",           "group": "Cardio"},
    "stair_climber":      {"label": "Stair Climber",            "group": "Cardio"},
    "elliptical":         {"label": "Elliptical",               "group": "Cardio"},
    "assault_bike":       {"label": "Assault / Air Bike",       "group": "Cardio"},
    "pull_up_bar":        {"label": "Pull-Up Bar",              "group": "Bars & Rigs"},
    "dip_bars":           {"label": "Dip Bars / Parallel Bars", "group": "Bars & Rigs"},
    "barbell":            {"label": "Barbell",                  "group": "Bars & Rigs"},
    "ez_curl_bar":        {"label": "EZ Curl Bar",              "group": "Bars & Rigs"},
    "squat_rack":         {"label": "Squat Rack / Power Rack",  "group": "Bars & Rigs"},
    "smith_machine":      {"label": "Smith Machine",            "group": "Bars & Rigs"},
    "push_up_handles":    {"label": "Rotating Push-Up Handles", "group": "Push"},
    "push_up_board":      {"label": "Push-Up Board",            "group": "Push"},
    "bench_flat":         {"label": "Flat Bench",               "group": "Push"},
    "bench_adjustable":   {"label": "Adjustable Bench",         "group": "Push"},
    "dumbbells_light":    {"label": "Dumbbells 3–10 lb",        "group": "Dumbbells"},
    "dumbbells_medium":   {"label": "Dumbbells 12–25 lb",       "group": "Dumbbells"},
    "dumbbells_heavy":    {"label": "Dumbbells 30–50 lb",       "group": "Dumbbells"},
    "dumbbell_25":        {"label": "Single 25 lb Dumbbell",    "group": "Dumbbells"},
    "dumbbell_35":        {"label": "Single 35 lb Dumbbell",    "group": "Dumbbells"},
    "adjustable_dumbbell":{"label": "Adjustable Dumbbells",     "group": "Dumbbells"},
    "kettlebell_light":   {"label": "Kettlebell 8–16 kg",       "group": "Kettlebells"},
    "kettlebell_heavy":   {"label": "Kettlebell 20–32 kg",      "group": "Kettlebells"},
    "bands_light":        {"label": "Light Resistance Band",    "group": "Bands"},
    "bands_medium":       {"label": "Medium Resistance Band",   "group": "Bands"},
    "bands_heavy":        {"label": "Heavy Resistance Band",    "group": "Bands"},
    "bands_loop":         {"label": "Loop / Booty Bands",       "group": "Bands"},
    "cable_machine":      {"label": "Cable Machine",            "group": "Bands"},
    "weight_vest":        {"label": "Weight Vest",              "group": "Weighted Gear"},
    "arm_weights":        {"label": "Arm Weights",              "group": "Weighted Gear"},
    "leg_weights":        {"label": "Leg Weights",              "group": "Weighted Gear"},
    "weight_plates":      {"label": "Weight Plates",            "group": "Weighted Gear"},
    "leg_press":          {"label": "Leg Press Machine",        "group": "Machines"},
    "leg_curl":           {"label": "Leg Curl Machine",         "group": "Machines"},
    "leg_extension":      {"label": "Leg Extension Machine",    "group": "Machines"},
    "lat_pulldown":       {"label": "Lat Pulldown Machine",     "group": "Machines"},
    "seated_row":         {"label": "Seated Row Machine",       "group": "Machines"},
    "chest_fly_machine":  {"label": "Chest Fly / Pec Deck",     "group": "Machines"},
    "shoulder_press_mach":{"label": "Shoulder Press Machine",   "group": "Machines"},
    "hack_squat":         {"label": "Hack Squat Machine",       "group": "Machines"},
    "ab_crunch_machine":  {"label": "Ab Crunch Machine",        "group": "Machines"},
    "yoga_mat":           {"label": "Yoga / Exercise Mat",      "group": "Floor & Stability"},
    "foam_roller":        {"label": "Foam Roller",              "group": "Floor & Stability"},
    "stability_ball":     {"label": "Stability / Swiss Ball",   "group": "Floor & Stability"},
    "bosu_ball":          {"label": "BOSU Ball",                "group": "Floor & Stability"},
    "ab_wheel":           {"label": "Ab Wheel",                 "group": "Floor & Stability"},
    "balance_board":      {"label": "Balance Board",            "group": "Floor & Stability"},
    "parallettes":        {"label": "Parallettes",              "group": "Floor & Stability"},
    "trx":                {"label": "TRX / Suspension Trainer", "group": "Suspension"},
    "gymnastic_rings":    {"label": "Gymnastic Rings",          "group": "Suspension"},
    "stairs":             {"label": "Stairs / Steps",           "group": "Environment"},
    "outdoor_park":       {"label": "Outdoor Park / Playground","group": "Environment"},
    "swimming_pool":      {"label": "Swimming Pool",            "group": "Environment"},
    "open_floor":         {"label": "Open Floor Space",         "group": "Environment"},
    "wall":               {"label": "Sturdy Wall",              "group": "Environment"},
    "chair_or_bench":     {"label": "Chair or Sturdy Surface",  "group": "Environment"},
    "sandbag":            {"label": "Sandbag",                  "group": "Environment"},
    "sled":               {"label": "Push / Pull Sled",         "group": "Environment"},
    "battle_ropes":       {"label": "Battle Ropes",             "group": "Environment"},
    "medicine_ball":      {"label": "Medicine Ball",            "group": "Environment"},
}

DEFAULT_EQUIPMENT = set(ALL_EQUIPMENT.keys())

LOCATION_PRESETS = {
    "Home (Minimal)": {"keys": {"open_floor", "chair_or_bench", "wall"}, "desc": "Home with minimal gear"},
    "Commercial Gym":  {"keys": {"barbell","squat_rack","bench_flat","bench_adjustable","dumbbells_light","dumbbells_medium","dumbbells_heavy","adjustable_dumbbell","kettlebell_light","kettlebell_heavy","cable_machine","lat_pulldown","seated_row","leg_press","leg_curl","leg_extension","chest_fly_machine","shoulder_press_mach","hack_squat","ab_crunch_machine","pull_up_bar","dip_bars","bands_light","bands_medium","bands_heavy","bands_loop","treadmill","stationary_bike","rowing_machine","stair_climber","elliptical","assault_bike","yoga_mat","foam_roller","stability_ball","ab_wheel","open_floor"}, "desc": "Full commercial gym"},
    "Outdoor / Park":  {"keys": {"outdoor_park", "stairs", "open_floor", "wall"}, "desc": "Park or outdoor gym"},
    "Office Break":    {"keys": {"chair_or_bench", "wall"}, "desc": "Bodyweight only"},
}

def load_equipment():
    try:
        if os.path.exists(EQUIPMENT_FILE):
            with open(EQUIPMENT_FILE, 'r') as f:
                data = json.load(f)
                return set(data.get("owned", list(DEFAULT_EQUIPMENT)))
    except Exception:
        pass
    return set(DEFAULT_EQUIPMENT)

def save_equipment(owned_set):
    try:
        with open(EQUIPMENT_FILE, 'w') as f:
            json.dump({"owned": list(owned_set)}, f)
    except IOError:
        pass

def load_presets():
    try:
        if os.path.exists(PRESETS_FILE):
            with open(PRESETS_FILE, 'r') as f:
                data = json.load(f)
                return {name: {"keys": set(v["keys"]), "desc": v.get("desc", "")}
                        for name, v in data.items()}
    except Exception:
        pass
    return {name: {"keys": set(v["keys"]), "desc": v["desc"]}
            for name, v in LOCATION_PRESETS.items()}

def save_presets(presets):
    try:
        with open(PRESETS_FILE, 'w') as f:
            json.dump({name: {"keys": list(v["keys"]), "desc": v.get("desc", "")}
                       for name, v in presets.items()}, f, indent=2)
    except IOError:
        pass

def load_progress():
    try:
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return {"completed_workouts": [], "total_sets": 0, "total_workouts": 0, "streak": 0, "last_date": ""}

def save_progress(data):
    try:
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(data, f)
    except IOError:
        pass


# ─────────────────────────────────────────────
# EXERCISE VARIATION LIBRARY
# Every slot routes through here. Last entry always has requires=set() as fallback.
# ─────────────────────────────────────────────
EXERCISE_VARIATIONS = {
    "chest_press": [
        # Barbell + bench (best)
        {"requires": {"barbell", "bench_adjustable", "squat_rack"}, "name": "Barbell Bench Press", "weight": "Working weight",
         "instruction": "Lie on adjustable bench, grip just wider than shoulders. Lower bar to mid-chest with control, press back up to full lockout. Keep feet flat, shoulder blades retracted and depressed throughout."},
        {"requires": {"barbell", "bench_flat", "squat_rack"}, "name": "Barbell Bench Press", "weight": "Working weight",
         "instruction": "Lie on flat bench, grip just wider than shoulders. Lower bar to mid-chest with control, drive up to full lockout. Keep shoulder blades squeezed together and feet flat on the floor."},
        {"requires": {"barbell", "bench_flat"}, "name": "Barbell Bench Press", "weight": "Working weight",
         "instruction": "Flat bench, grip just wider than shoulders. Lower bar to mid-chest, press to lockout. Have a spotter or use a power rack with safeties if going heavy."},
        {"requires": {"barbell", "squat_rack"}, "name": "Barbell Floor Press", "weight": "Working weight",
         "instruction": "Lie on the floor under the bar set in the rack at a low height. Lower to elbows touching floor, press back up. Great chest and tricep builder with a natural range-of-motion limit."},
        # Dumbbells + bench
        {"requires": {"dumbbells_heavy", "bench_flat"}, "name": "Dumbbell Bench Press", "weight": "30–50 lb each",
         "instruction": "Lie on flat bench, dumbbells at chest level. Press up to lockout, slight arc inward at the top. Full range of motion — lower until elbows are just below bench level."},
        {"requires": {"dumbbells_heavy", "bench_adjustable"}, "name": "Dumbbell Bench Press", "weight": "30–50 lb each",
         "instruction": "Adjustable bench flat or slightly inclined. Press dumbbells up to lockout. The slight incline variation shifts more load to the upper chest."},
        {"requires": {"dumbbells_medium", "bench_flat"}, "name": "Dumbbell Bench Press", "weight": "12–25 lb each",
         "instruction": "Lie on flat bench. Press dumbbells up to lockout, slight arc inward at the top. Full range of motion every rep."},
        {"requires": {"dumbbells_medium", "bench_adjustable"}, "name": "Dumbbell Bench Press", "weight": "12–25 lb each",
         "instruction": "Flat or slight incline. Press up to lockout, control the descent. Elbows at about 75° — not flared all the way out."},
        # Dumbbells only (floor press)
        {"requires": {"dumbbells_heavy"}, "name": "Dumbbell Floor Press", "weight": "30–50 lb each",
         "instruction": "Lie on the floor, dumbbells at chest level. Press up to lockout. The floor stops your range at the natural end point — heavier weight, less shoulder strain."},
        {"requires": {"dumbbells_medium"}, "name": "Dumbbell Floor Press", "weight": "12–25 lb each",
         "instruction": "Lie on floor, press dumbbells up to lockout. Full press at the top, elbows just touch the floor at the bottom."},
        {"requires": {"dumbbell_35"}, "name": "Single-Arm Floor Press", "weight": "35 lb",
         "instruction": "Lie on your back, press one arm at a time. Brace your core against the rotation. Drive through your chest."},
        {"requires": {"dumbbell_25"}, "name": "Single-Arm Floor Press", "weight": "25 lb",
         "instruction": "Lie on your back, press one arm at a time. The uneven load forces anti-rotation core work. Drive through your chest."},
        # Bodyweight options
        {"requires": {"push_up_handles"}, "name": "Rotating Push-Up Handles", "weight": "Bodyweight",
         "instruction": "Let handles rotate naturally as you push up. Reduces wrist strain and deepens chest activation. Rigid plank throughout."},
        {"requires": {"bands_medium"}, "name": "Band Push-Up", "weight": "Medium Band",
         "instruction": "Loop band across your upper back, hold ends in each hand. Push-up as normal — band adds resistance at the top."},
        {"requires": set(), "name": "Push-Ups", "weight": "Bodyweight",
         "instruction": "Hands slightly wider than shoulders. Lower chest to within an inch of the floor. Full lockout at the top."},
    ],
    "shoulder_press": [
        # Barbell
        {"requires": {"barbell", "bench_adjustable"}, "name": "Seated Barbell Overhead Press", "weight": "Working weight",
         "instruction": "Set bench to 90°. Grip just outside shoulder width, press bar overhead to full lockout. Lower to chin height. Keep core braced — don't hyperextend your lower back."},
        {"requires": {"barbell", "squat_rack"}, "name": "Standing Barbell Overhead Press", "weight": "Working weight",
         "instruction": "Grip just outside shoulders, bar resting on upper chest. Brace your whole body and press straight overhead to lockout. Lower under control. Feet shoulder-width."},
        {"requires": {"barbell"}, "name": "Standing Barbell Overhead Press", "weight": "Working weight",
         "instruction": "Grip just outside shoulders, press straight overhead to lockout. Keep ribs down and core tight — don't lean back to grind reps."},
        # Dumbbells + bench
        {"requires": {"dumbbells_heavy", "bench_adjustable"}, "name": "Seated Dumbbell Shoulder Press", "weight": "30–50 lb each",
         "instruction": "Set bench to 90°. Press dumbbells overhead to lockout from ear level. Lower until elbows are just below shoulder height. Seated removes the temptation to use leg drive."},
        {"requires": {"dumbbells_medium", "bench_adjustable"}, "name": "Seated Dumbbell Shoulder Press", "weight": "12–25 lb each",
         "instruction": "Bench at 90°. Press overhead to lockout. Keep shoulder blades pulled back against the bench. Don't let the dumbbells drift forward."},
        # Dumbbells standing
        {"requires": {"dumbbells_heavy"}, "name": "Standing Dumbbell Shoulder Press", "weight": "30–50 lb each",
         "instruction": "Stand, press both dumbbells overhead simultaneously. Brace your core to avoid arching your lower back. Full lockout at the top."},
        {"requires": {"dumbbells_medium"}, "name": "Standing Dumbbell Shoulder Press", "weight": "12–25 lb each",
         "instruction": "Stand, press overhead to lockout. Keep your ribs down and core braced. Don't use a push from your legs — strict press."},
        {"requires": {"dumbbell_35"}, "name": "Single-Arm Shoulder Press", "weight": "35 lb",
         "instruction": "Sit for stability. Drive through the heel of your palm. Core must stay rigid to protect the lower back."},
        {"requires": {"dumbbell_25"}, "name": "Single-Arm Shoulder Press", "weight": "25 lb",
         "instruction": "Stand or sit. Brace your core hard to resist leaning to the side. Press straight up, don't flare the elbow out too wide."},
        {"requires": {"dumbbells_light"}, "name": "Single-Arm Shoulder Press", "weight": "8–10 lb",
         "instruction": "Lighter load — focus on full range of motion. Elbow at 90° at bottom, full lockout at top. Higher reps."},
        {"requires": {"bands_medium"}, "name": "Band Overhead Press", "weight": "Medium Band",
         "instruction": "Stand on the band, hold at shoulder height, press overhead. Ascending resistance — hardest at the top."},
        {"requires": set(), "name": "Pike Push-Ups", "weight": "Bodyweight",
         "instruction": "Hands on floor, hips high in an inverted V. Lower your head toward the floor bending at the elbows. Targets the shoulder."},
    ],
    "lateral_raise": [
        {"requires": {"dumbbells_medium"}, "name": "Alternating Lateral Raises", "weight": "12–15 lb",
         "instruction": "Slight bend in the elbow, raise to shoulder height only. Don't shrug. These add up fast — don't go too heavy."},
        {"requires": {"dumbbells_light"}, "name": "Alternating Lateral Raises", "weight": "5–10 lb",
         "instruction": "Slight bend in the elbow, raise to shoulder height only. Don't shrug. Lighter is smarter here."},
        {"requires": {"bands_light"}, "name": "Band Lateral Raises", "weight": "Light Band",
         "instruction": "Stand on band, one end in each hand. Raise arms out to sides. Tension increases as you raise — squeeze at the top."},
        {"requires": set(), "name": "Bodyweight Lateral Raises", "weight": "Bodyweight",
         "instruction": "No weight — focus on squeezing the lateral deltoid. 20–25 reps, slow and deliberate."},
    ],
    "tricep_ext": [
        # Cable machine (best)
        {"requires": {"cable_machine"}, "name": "Cable Tricep Pushdowns (Rope)", "weight": "Light–Moderate",
         "instruction": "Rope attachment, set cable high. Elbows pinned to sides, push rope down and flare hands out at the bottom. Full extension and squeeze every rep."},
        # Barbell
        {"requires": {"barbell", "bench_flat"}, "name": "Skull Crushers (EZ or Straight Bar)", "weight": "Light–Moderate",
         "instruction": "Lie on bench, arms extended over your chest. Lower bar toward your forehead bending only at the elbows. Upper arms stay vertical. Press back to full extension."},
        {"requires": {"barbell"}, "name": "Skull Crushers (Floor)", "weight": "Light–Moderate",
         "instruction": "Lie on the floor, arms extended over chest. Lower bar toward forehead, upper arms stay vertical. Press back up. Floor limits range slightly — keep it controlled."},
        # Dumbbells
        {"requires": {"dumbbells_heavy", "bench_flat"}, "name": "Dumbbell Skull Crushers", "weight": "20–35 lb each",
         "instruction": "Lie on bench, arms extended over chest. Lower dumbbells toward your temples bending only at the elbows. Press back to lockout. Keep upper arms perfectly vertical."},
        {"requires": {"dumbbells_medium"}, "name": "Two-Arm Overhead Tricep Extension", "weight": "12–25 lb",
         "instruction": "Hold one dumbbell with both hands overhead. Lower behind head, elbows pointing forward. Full extension at the top. Good stretch at the bottom."},
        {"requires": {"bands_medium"}, "name": "Band Tricep Pushdowns", "weight": "Medium Band",
         "instruction": "Anchor band overhead. Keep elbows pinned to your sides and push down until arms fully extended. Squeeze at the bottom."},
        {"requires": {"dumbbell_25"}, "name": "Single-Arm Overhead Tricep Extension", "weight": "25 lb",
         "instruction": "Hold dumbbell overhead, lower behind head by bending elbow. Keep upper arm still and vertical. Extend back up fully."},
        {"requires": {"dumbbells_light"}, "name": "Two-Arm Overhead Tricep Extension", "weight": "8–10 lb",
         "instruction": "Hold one dumbbell with both hands overhead. Lower behind head, elbows pointing forward. Full extension at the top."},
        {"requires": {"bands_light"}, "name": "Band Tricep Pushdowns", "weight": "Light Band",
         "instruction": "Anchor band overhead. Elbows pinned to sides, push straight down. Full extension and squeeze at the bottom."},
        {"requires": set(), "name": "Diamond Push-Ups", "weight": "Bodyweight",
         "instruction": "Hands close together forming a diamond shape under your chest. Elbows track back along your sides. Intense tricep isolation."},
    ],
    "plank": [
        {"requires": {"ab_wheel"}, "name": "Ab Wheel Rollouts", "weight": "Bodyweight", "type": "reps", "reps_override": "8–10",
         "instruction": "Kneel, grip ab wheel with both hands. Roll forward slowly until nearly parallel to floor. Pull back using your core. Don't let lower back sag."},
        {"requires": {"stability_ball"}, "name": "Stability Ball Plank", "weight": "Bodyweight", "type": "timed", "duration": 45,
         "instruction": "Forearms on stability ball, body in straight plank line. Unstable surface forces your core to work twice as hard. Hold perfectly still."},
        {"requires": set(), "name": "Plank", "weight": "Bodyweight", "type": "timed", "duration": 45,
         "instruction": "Forearms or hands. Keep hips level — don't let them sag or pike up. Squeeze glutes and abs throughout."},
    ],
    "dead_bug": [
        {"requires": {"dumbbells_light"}, "name": "Dead Bugs with Dumbbells", "weight": "3–5 lb",
         "instruction": "Hold light dumbbells pointing to ceiling. Lying on back, lower opposite arm and leg slowly. Added weight increases anti-rotation demand."},
        {"requires": set(), "name": "Dead Bugs", "weight": "Bodyweight",
         "instruction": "Lying on back, arms up, knees at 90°. Lower opposite arm and leg slowly while pressing lower back into the floor. Exhale as you lower."},
    ],
    "crunch": [
        {"requires": {"ab_crunch_machine"}, "name": "Ab Crunch Machine", "weight": "Light–Medium",
         "instruction": "Controlled tempo — 2 seconds down, 1 second up. Don't use momentum. Feel the contraction at the top of every rep."},
        {"requires": {"stability_ball"}, "name": "Stability Ball Crunches", "weight": "Bodyweight",
         "instruction": "Sit on ball, walk feet forward until lower back supported by ball. Crunch up. Curved surface increases the range of motion vs floor crunches."},
        {"requires": set(), "name": "Bicycle Crunches", "weight": "Bodyweight",
         "instruction": "Slow and controlled. Rotate your shoulder toward the knee, not just your elbow. Keep lower back pressed down."},
    ],
    "pull_up": [
        {"requires": {"pull_up_bar", "bands_heavy"}, "name": "Assisted Pull-Ups (Heavy Band)", "weight": "Band Assisted",
         "instruction": "Loop heavy band over bar, kneel or stand in loop. Full dead hang at bottom, chin over bar at top. Band reduces bodyweight load significantly."},
        {"requires": {"pull_up_bar", "bands_medium"}, "name": "Assisted Pull-Ups (Medium Band)", "weight": "Band Assisted",
         "instruction": "Medium band assist — you're doing more of the work. Good for the transition to unassisted."},
        {"requires": {"pull_up_bar"}, "name": "Pull-Ups", "weight": "Bodyweight",
         "instruction": "Full dead hang at bottom, chin over bar at top. Don't kip — strict reps only. If you can't complete a rep, do a slow 5-second negative."},
        {"requires": {"lat_pulldown"}, "name": "Lat Pulldown Machine", "weight": "Moderate",
         "instruction": "Grip slightly wider than shoulder width. Pull bar to upper chest, squeezing lats at bottom. Controlled return."},
        {"requires": {"bands_heavy"}, "name": "Band Pull-Downs", "weight": "Heavy Band",
         "instruction": "Anchor band above your head. Kneel and pull down to chest, driving elbows toward your hips. Mimics the pull-up pattern."},
        {"requires": {"trx"}, "name": "TRX Rows", "weight": "Bodyweight",
         "instruction": "Lean back holding TRX handles. Pull chest to hands squeezing shoulder blades. The more horizontal your body, the harder it is."},
        {"requires": set(), "name": "Inverted Rows (Table)", "weight": "Bodyweight",
         "instruction": "Lie under a sturdy table, grip the edge, pull chest up to it. Straight body like a reverse plank. One of the best pull-up substitutes."},
    ],
    "chin_up": [
        {"requires": {"pull_up_bar", "bands_heavy"}, "name": "Assisted Chin-Ups (Heavy Band)", "weight": "Band Assisted",
         "instruction": "Underhand grip, loop heavy band over bar. Full range of motion — dead hang to chin over bar."},
        {"requires": {"pull_up_bar", "bands_medium"}, "name": "Assisted Chin-Ups (Medium Band)", "weight": "Band Assisted",
         "instruction": "Underhand grip, medium band assist. You're doing most of the work. Focus on the bicep at the top."},
        {"requires": {"pull_up_bar"}, "name": "Chin-Ups", "weight": "Bodyweight",
         "instruction": "Underhand grip (easier than pull-ups). Full range of motion. Use band assist if needed to complete all reps with good form."},
        {"requires": {"lat_pulldown"}, "name": "Underhand Lat Pulldown", "weight": "Moderate",
         "instruction": "Underhand (supinated) grip at shoulder width. Pull to upper chest. More bicep involvement than overhand pulldown."},
        {"requires": set(), "name": "Negative Chin-Up Holds", "weight": "Bodyweight",
         "instruction": "Jump to top position (chin over bar) and lower yourself as slowly as possible — aim for 5–8 seconds. Excellent strength builder."},
    ],
    "bent_over_row": [
        # Barbell (best)
        {"requires": {"barbell", "squat_rack"}, "name": "Barbell Bent-Over Row", "weight": "Working weight",
         "instruction": "Hinge to about 45°, overhand grip just outside shoulders. Pull bar to your lower chest, driving elbows back. Lower under control. Keep back flat throughout — don't round."},
        {"requires": {"barbell"}, "name": "Barbell Bent-Over Row", "weight": "Working weight",
         "instruction": "Hinge to 45°, pull bar to lower chest. Drive elbows back and squeeze shoulder blades at the top. This is the single best back mass builder — own it."},
        # Dumbbells + bench
        {"requires": {"dumbbells_heavy", "bench_flat"}, "name": "Chest-Supported Dumbbell Row", "weight": "30–50 lb each",
         "instruction": "Set bench to low incline, lie face-down. Row both dumbbells up simultaneously. Chest supported means no cheating — pure back work."},
        {"requires": {"dumbbells_medium", "bench_flat"}, "name": "Chest-Supported Dumbbell Row", "weight": "12–25 lb each",
         "instruction": "Bench to low incline, lie face-down. Row both dumbbells up. Squeeze shoulder blades at the top. The support removes lower back fatigue entirely."},
        # Dumbbells only
        {"requires": {"dumbbells_heavy"}, "name": "Dumbbell Bent-Over Row", "weight": "30–50 lb each",
         "instruction": "Hinge forward, back flat. Row both dumbbells simultaneously to your lower ribs. Drive elbows back. Squeeze at the top."},
        {"requires": {"dumbbell_35"}, "name": "Single-Arm Bent-Over Row", "weight": "35 lb",
         "instruction": "Brace one hand on a chair or bench. Keep your back flat and parallel to floor. Drive your elbow back, not up. Squeeze at the top."},
        {"requires": {"dumbbell_25"}, "name": "Single-Arm Bent-Over Row", "weight": "25 lb",
         "instruction": "Brace one hand for support. Full range of motion — dead hang at bottom, elbow past torso at top. Focus on lat engagement."},
        {"requires": {"dumbbells_light"}, "name": "Single-Arm Bent-Over Row", "weight": "8–10 lb",
         "instruction": "Lighter weight — focus on movement pattern and lat squeeze. Higher reps (15 per side) to compensate."},
        {"requires": {"seated_row"}, "name": "Seated Cable Row", "weight": "Moderate",
         "instruction": "Sit upright, pull handle to lower chest. Lead with your elbows. Squeeze shoulder blades together at the end of every rep."},
        {"requires": {"bands_medium"}, "name": "Band Bent-Over Row", "weight": "Medium Band",
         "instruction": "Stand on band, hinge forward, row both ends up simultaneously. Drive elbows back and squeeze at the top."},
        {"requires": set(), "name": "Bodyweight Superman Rows", "weight": "Bodyweight",
         "instruction": "Lie face down, arms extended. Lift chest and arms simultaneously squeezing the back. Hold 2 seconds at top. Lower and repeat."},
    ],
    "face_pull": [
        {"requires": {"cable_machine"}, "name": "Cable Face Pulls", "weight": "Light",
         "instruction": "Cable at face height with rope attachment. Pull toward your forehead, elbows flaring high. Your most important posture exercise."},
        {"requires": {"bands_light"}, "name": "Band Face Pulls", "weight": "Light Band",
         "instruction": "Anchor band at face height. Pull toward your forehead, elbows flaring up and out. Don't skip this one."},
        {"requires": {"bands_medium"}, "name": "Band Face Pulls", "weight": "Medium Band",
         "instruction": "Anchor band at face height. Pull toward your forehead with elbows high. More resistance — focus on controlled reps."},
        {"requires": set(), "name": "Prone Y-T-W Raises", "weight": "Bodyweight",
         "instruction": "Lie face down. Raise arms into Y (overhead), T (out to sides), W (bent elbows near ears). Each letter is one rep cycle. Same muscles as face pulls."},
    ],
    "pull_apart": [
        {"requires": {"bands_light"}, "name": "Band Pull-Aparts", "weight": "Light Band",
         "instruction": "Hold band at chest width, arms straight. Pull apart until band touches chest, squeezing shoulder blades. Controlled return."},
        {"requires": {"bands_medium"}, "name": "Band Pull-Aparts", "weight": "Medium Band",
         "instruction": "More resistance — keep movement strict. Pull apart until band touches chest, full rear delt squeeze at the end."},
        {"requires": set(), "name": "Prone T Raises", "weight": "Bodyweight",
         "instruction": "Lie face down, arms out to sides in a T shape. Lift arms off floor squeezing shoulder blades. Hold 2 seconds at top. Same muscles as pull-aparts."},
    ],
    "bicep_curl": [
        {"requires": {"dumbbell_35"}, "name": "Alternating Dumbbell Curls", "weight": "35 lb",
         "instruction": "Heavy load — strict form is critical. No swinging. Supinate the wrist as you curl up, full extension at the bottom."},
        {"requires": {"dumbbell_25"}, "name": "Alternating Dumbbell Curls", "weight": "25 lb",
         "instruction": "Supinate (rotate) the wrist as you curl up. Don't swing — upper arms pinned to your sides. Full extension at the bottom."},
        {"requires": {"dumbbells_light"}, "name": "Alternating Dumbbell Curls", "weight": "8–10 lb",
         "instruction": "Full range of motion. Squeeze at top, controlled descent. Higher reps (15 per side) to compensate for lighter weight."},
        {"requires": {"ez_curl_bar"}, "name": "EZ Bar Curls", "weight": "Light–Moderate",
         "instruction": "Angled grip reduces wrist strain. Keep elbows pinned to your sides. Full extension at bottom, squeeze at top."},
        {"requires": {"bands_medium"}, "name": "Band Bicep Curls", "weight": "Medium Band",
         "instruction": "Stand on band, curl both ends up simultaneously. Constant tension — there's no easy spot in the range of motion."},
        {"requires": set(), "name": "Isometric Towel Curls", "weight": "Bodyweight",
         "instruction": "Loop a towel under your foot. Pull with both hands like a curl, resisting with your foot. Zero equipment bicep work."},
    ],
    "hammer_curl": [
        {"requires": {"dumbbell_25"}, "name": "Alternating Hammer Curls", "weight": "25 lb",
         "instruction": "Neutral grip (thumbs up). Targets the brachialis — the muscle under the bicep that adds width. Same strict form as regular curls."},
        {"requires": {"dumbbells_light"}, "name": "Alternating Hammer Curls", "weight": "8–10 lb",
         "instruction": "Neutral grip through full range of motion. Focus on the brachialis contraction."},
        {"requires": {"bands_medium"}, "name": "Band Hammer Curls", "weight": "Medium Band",
         "instruction": "Stand on band, curl with a neutral grip (palms facing each other). Elbows pinned to sides throughout."},
        {"requires": set(), "name": "Neutral-Grip Towel Curls", "weight": "Bodyweight",
         "instruction": "Towel under your foot, curl with a neutral grip (thumbs up). Targets the same brachialis muscle as hammer curls."},
    ],
    "dead_hang": [
        {"requires": {"pull_up_bar"}, "name": "Dead Hangs", "weight": "Bodyweight", "type": "timed", "duration": 25,
         "instruction": "Full grip on the bar, let your body hang completely. Builds grip strength and decompresses your spine. Breathe slowly."},
        {"requires": {"gymnastic_rings"}, "name": "Ring Dead Hangs", "weight": "Bodyweight", "type": "timed", "duration": 25,
         "instruction": "Hang from the rings with straight arms. Instability recruits more shoulder stabilisers than a fixed bar. Let the shoulders decompress."},
        {"requires": set(), "name": "Band Pull-Aparts (Finisher)", "weight": "Light Band",
         "instruction": "Hold band at chest width, pull apart until band touches chest. Great grip and rear delt finisher when no bar is available."},
    ],
    "goblet_squat": [
        # Barbell back squat (best)
        {"requires": {"barbell", "squat_rack"}, "name": "Barbell Back Squat", "weight": "Working weight",
         "instruction": "Bar on upper traps (high bar) or lower (low bar). Feet shoulder-width, toes out slightly. Squat to depth — hip crease below the knee. Drive through your whole foot back to lockout."},
        {"requires": {"barbell"}, "name": "Barbell Front Squat", "weight": "Working weight",
         "instruction": "Bar resting on front delts, elbows high. Squat deep, chest tall throughout. More upright torso than back squat — excellent quad and core builder."},
        # Dumbbells
        {"requires": {"dumbbells_heavy"}, "name": "Dumbbell Goblet Squat", "weight": "30–50 lb",
         "instruction": "Hold heaviest dumbbell at chest height in both hands. Squat deep, chest tall. Drive knees out over toes."},
        {"requires": {"dumbbell_35"}, "name": "Goblet Squat", "weight": "35 lb",
         "instruction": "Hold dumbbell at chest height in both hands. Feet shoulder-width, toes slightly out. Squat deep, keeping chest tall. Drive knees out over toes."},
        {"requires": {"dumbbell_25"}, "name": "Goblet Squat", "weight": "25 lb",
         "instruction": "Hold dumbbell at chest height. Focus on depth and chest position. Heels flat, drive knees out. Full range of motion every rep."},
        {"requires": {"kettlebell_light"}, "name": "Kettlebell Goblet Squat", "weight": "8–16 kg",
         "instruction": "Hold kettlebell by the horns at chest height. The counterbalance actually helps you sit back further. Chest tall throughout."},
        {"requires": {"weight_vest"}, "name": "Weighted Squat (Vest)", "weight": "Weight Vest",
         "instruction": "Vest on, hands clasped at chest. Squat as deep as mobility allows. The vest loads your spine — keep it absolutely upright."},
        {"requires": {"bands_heavy"}, "name": "Banded Squat", "weight": "Heavy Band",
         "instruction": "Band across upper back, held at shoulders. Squat to depth. Band adds resistance at the top where bodyweight squats get too easy."},
        {"requires": set(), "name": "Bodyweight Squat", "weight": "Bodyweight",
         "instruction": "Arms out front for balance. Squat as deep as possible, chest tall. Slow 3-second descent to increase difficulty."},
    ],
    "romanian_deadlift": [
        # Barbell (best)
        {"requires": {"barbell"}, "name": "Barbell Romanian Deadlift", "weight": "Working weight",
         "instruction": "Overhand grip just outside hips. Hinge at the hips, pushing them back as the bar slides down your legs. Feel the hamstring stretch at the bottom. Drive hips forward to return. Back flat throughout."},
        # Dumbbells + bench
        {"requires": {"dumbbells_heavy"}, "name": "Dumbbell Romanian Deadlift", "weight": "30–50 lb each",
         "instruction": "Hold dumbbells in front of thighs. Hinge at hips, lowering dumbbells along your legs. Feel the hamstring stretch. Drive hips forward to stand. Keep back flat."},
        {"requires": {"dumbbell_35"}, "name": "Single-Leg Romanian Deadlift", "weight": "35 lb",
         "instruction": "Hold dumbbell in opposite hand to working leg. Hinge at hip, free leg trails back. Back flat. Feel the hamstring stretch at the bottom."},
        {"requires": {"dumbbell_25"}, "name": "Single-Leg Romanian Deadlift", "weight": "25 lb",
         "instruction": "Opposite hand holds weight. Hinge slowly — balance is the challenge. If unstable, lightly touch free toe to floor."},
        {"requires": {"kettlebell_light"}, "name": "Single-Leg Kettlebell RDL", "weight": "8–16 kg",
         "instruction": "Kettlebell in opposite hand to working leg. Hinge at hip, trail the free leg back. KB shape helps you stay tight through the movement."},
        {"requires": {"dumbbells_light"}, "name": "Single-Leg Romanian Deadlift", "weight": "8–10 lb",
         "instruction": "Light weight — focus on the hamstring stretch and hip hinge pattern. Touch the dumbbell to the floor if mobility allows."},
        {"requires": {"leg_curl"}, "name": "Leg Curl Machine", "weight": "Moderate",
         "instruction": "Full extension at start, curl to full flexion, squeeze the hamstring. Slow 3-second lowering phase."},
        {"requires": set(), "name": "Single-Leg Hip Hinge", "weight": "Bodyweight",
         "instruction": "Arms out for balance. Hinge forward on one leg, free leg trails back. Touch fingers to floor if possible. Hamstring and glute still get a strong stimulus."},
    ],
    "reverse_lunge": [
        {"requires": {"weight_vest"}, "name": "Reverse Lunges (Weight Vest)", "weight": "Weight Vest",
         "instruction": "Step back, lower back knee toward floor. Keep front shin vertical. Drive through the front heel to return. Control the descent."},
        {"requires": {"dumbbell_35"}, "name": "Dumbbell Reverse Lunges", "weight": "35 lb",
         "instruction": "Hold a dumbbell in each hand at your sides. Step back, lower back knee toward floor. Front shin stays vertical."},
        {"requires": {"dumbbell_25"}, "name": "Single-Arm Reverse Lunge", "weight": "25 lb",
         "instruction": "Hold dumbbell in one hand, alternate sides. Offset load challenges your core and balance on top of the leg work."},
        {"requires": {"dumbbells_light"}, "name": "Dumbbell Reverse Lunges", "weight": "8–10 lb",
         "instruction": "Dumbbells at sides. Step back, controlled descent. Focus on front glute and quad driving you back up."},
        {"requires": {"bands_medium"}, "name": "Banded Reverse Lunges", "weight": "Medium Band",
         "instruction": "Band around thighs above knees. Step back into lunge — band forces front knee to stay in line with your foot. Great for glute activation."},
        {"requires": set(), "name": "Reverse Lunges", "weight": "Bodyweight",
         "instruction": "Step back, lower back knee toward floor. Front shin stays vertical. Slow 3-second descent to maximize time under tension."},
    ],
    "glute_bridge": [
        {"requires": {"leg_weights"}, "name": "Glute Bridges (Leg Weights)", "weight": "Leg Weights",
         "instruction": "Lie on back, feet flat, leg weights strapped on. Drive hips up squeezing glutes hard. Hold at top for 1 second. Lower slowly."},
        {"requires": {"dumbbell_35"}, "name": "Dumbbell Glute Bridge", "weight": "35 lb",
         "instruction": "Rest dumbbell across your hips. Drive hips up and squeeze hard at the top."},
        {"requires": {"dumbbell_25"}, "name": "Dumbbell Glute Bridge", "weight": "25 lb",
         "instruction": "Rest 25 lb dumbbell across hips. Drive hips up and squeeze hard at the top."},
        {"requires": {"bands_loop"}, "name": "Banded Glute Bridge", "weight": "Loop Band",
         "instruction": "Loop band just above knees, push knees out against it. Bridge up and hold — band forces glutes to work harder to keep knees apart."},
        {"requires": {"bands_medium"}, "name": "Banded Glute Bridge", "weight": "Medium Band",
         "instruction": "Band across hips anchored by your hands. Band adds resistance at the top where glutes are most engaged."},
        {"requires": set(), "name": "Glute Bridges", "weight": "Bodyweight",
         "instruction": "Drive hips up, hold 2 seconds at top, lower slowly. Higher reps (25–30) to compensate for no external load. Squeeze hard every rep."},
    ],
    "donkey_kick": [
        {"requires": {"leg_weights"}, "name": "Donkey Kicks (Leg Weights)", "weight": "Leg Weights",
         "instruction": "On all fours. Keep 90° bend in knee and kick straight up toward ceiling. Squeeze glute at top. Hips stay level."},
        {"requires": {"bands_loop"}, "name": "Banded Donkey Kicks", "weight": "Loop Band",
         "instruction": "Loop band around thighs above knees. On all fours, kick back and up against band resistance. Adds load at the peak contraction."},
        {"requires": set(), "name": "Donkey Kicks", "weight": "Bodyweight",
         "instruction": "On all fours. Keep 90° bend in knee, kick straight up squeezing glute at top. Hips stay perfectly level. Higher reps (20 per side)."},
    ],
    "lateral_walk": [
        {"requires": {"bands_loop"}, "name": "Banded Lateral Walks", "weight": "Loop Band",
         "instruction": "Band around thighs just above knees. Slight squat position, stay low throughout. Step side to side maintaining band tension. Burns the gluteus medius."},
        {"requires": {"bands_medium"}, "name": "Banded Lateral Walks", "weight": "Medium Band",
         "instruction": "Band around thighs above knees. Slight squat position, step side to side maintaining tension. Burns the outer glute."},
        {"requires": set(), "name": "Lateral Walks", "weight": "Bodyweight",
         "instruction": "Stay in a half-squat, step side to side with controlled movement. Slow pace maximises glute activation. Don't stand up between steps."},
    ],
    "thruster": [
        {"requires": {"barbell", "squat_rack"}, "name": "Barbell Thruster", "weight": "Working weight",
         "instruction": "Bar in front rack position. Squat to depth, drive up explosively and press overhead to lockout in one fluid motion. Re-rack at shoulder height and repeat."},
        {"requires": {"barbell"}, "name": "Barbell Push Press", "weight": "Working weight",
         "instruction": "Bar on upper chest, slight knee dip then drive through hips and legs as you press overhead. More weight than strict press — use the leg drive to initiate."},
        {"requires": {"dumbbells_heavy"}, "name": "Dumbbell Thrusters", "weight": "30–50 lb each",
         "instruction": "Dumbbells at shoulder height. Squat down, drive up and press overhead in one explosive motion. Land the dumbbells back at shoulders softly."},
        {"requires": {"dumbbell_35"}, "name": "Single-Arm Dumbbell Thruster", "weight": "35 lb",
         "instruction": "Squat to press combined. Hold dumbbell at shoulder, squat down, drive up and press overhead in one fluid motion. Alternate sides each rep."},
        {"requires": {"dumbbell_25"}, "name": "Single-Arm Dumbbell Thruster", "weight": "25 lb",
         "instruction": "Squat to press combined. Hold dumbbell at shoulder, squat down, drive up and press overhead. Alternate sides each rep."},
        {"requires": {"kettlebell_light"}, "name": "Kettlebell Thruster", "weight": "8–16 kg",
         "instruction": "Clean kettlebell to rack position, squat down, drive up pressing overhead. One fluid motion. KB shape forces better wrist and elbow positioning."},
        {"requires": {"dumbbells_light"}, "name": "Dumbbell Thruster", "weight": "8–10 lb",
         "instruction": "Lighter load — focus on the fluid squat-to-press connection. Higher reps (10 per side) to compensate."},
        {"requires": {"bands_medium"}, "name": "Band Thruster", "weight": "Medium Band",
         "instruction": "Stand on band, hold at shoulders. Squat down, drive up and press overhead. Bands make the top half hardest — push through it."},
        {"requires": set(), "name": "Jump Squat to Overhead Reach", "weight": "Bodyweight",
         "instruction": "Squat down, explode up into a jump reaching both arms overhead. Land soft. Full-body power movement — pure conditioning with no equipment."},
    ],
    "cardio_finisher": [
        {"requires": {"jump_rope"}, "name": "Jump Rope", "weight": "Bodyweight", "type": "timed", "duration": 30,
         "instruction": "Push the pace. This is conditioning. Breathe rhythmically and try to maintain form even when tired."},
        {"requires": {"assault_bike"}, "name": "Assault Bike Sprint", "weight": "Bodyweight", "type": "timed", "duration": 30,
         "instruction": "Sprint at maximum effort. Arms and legs driving hard. Your round finisher — give everything."},
        {"requires": {"rowing_machine"}, "name": "Rowing Sprint", "weight": "Bodyweight", "type": "timed", "duration": 30,
         "instruction": "Full power rowing stroke — legs drive first, hips open, then arms pull. Maximum effort for the full interval."},
        {"requires": set(), "name": "High Knees", "weight": "Bodyweight", "type": "timed", "duration": 30,
         "instruction": "Drive knees up to hip height, arms pumping. Same cardio stimulus as jump rope with no equipment needed."},
    ],
}


def resolve_exercise(exercise_key, owned_equipment, sets, reps, rest):
    """Pick the best variation of an exercise based on owned equipment."""
    variations = EXERCISE_VARIATIONS.get(exercise_key, [])
    for variation in variations:
        if variation["requires"].issubset(owned_equipment):
            result = {
                "name":        variation["name"],
                "sets":        sets,
                "reps":        reps,
                "rest":        rest,
                "weight":      variation["weight"],
                "instruction": variation["instruction"],
            }
            if "type" in variation:
                result["type"] = variation["type"]
            if "duration" in variation:
                result["duration"] = variation["duration"]
            return result
    # Fallback to last entry (always has requires=set())
    fallback = variations[-1] if variations else {}
    result = {
        "name":        fallback.get("name", exercise_key),
        "sets":        sets,
        "reps":        reps,
        "rest":        rest,
        "weight":      fallback.get("weight", "Bodyweight"),
        "instruction": fallback.get("instruction", ""),
    }
    if "type" in fallback:
        result["type"] = fallback["type"]
    if "duration" in fallback:
        result["duration"] = fallback["duration"]
    return result


def build_workout_for_equipment(day_key, owned):
    """Return a fully resolved exercise list. Every slot routes through the variation resolver."""
    if day_key == "Day 1":
        return [
            resolve_exercise("chest_press",    owned, 3, "8–12 per side",  60),
            resolve_exercise("chest_press",    owned, 3, "10–15",          60),
            resolve_exercise("shoulder_press", owned, 3, "8–10 per side",  60),
            resolve_exercise("lateral_raise",  owned, 3, "12–15 per side", 45),
            resolve_exercise("tricep_ext",     owned, 3, "15",             45),
            resolve_exercise("tricep_ext",     owned, 3, "10–12 per side", 45),
            resolve_exercise("plank",          owned, 3, "45 sec",         30),
            resolve_exercise("dead_bug",       owned, 3, "10 per side",    30),
            resolve_exercise("crunch",         owned, 3, "20",             30),
        ]
    elif day_key == "Day 2":
        return [
            resolve_exercise("pull_up",       owned, 3, "6–10",            90),
            resolve_exercise("bent_over_row", owned, 3, "10–12 per side",  60),
            resolve_exercise("face_pull",     owned, 3, "15",              45),
            resolve_exercise("pull_apart",    owned, 3, "20",              30),
            resolve_exercise("bicep_curl",    owned, 3, "10–12 per side",  45),
            resolve_exercise("hammer_curl",   owned, 3, "10 per side",     45),
            resolve_exercise("dead_hang",     owned, 3, "20–30 sec",       45),
        ]
    elif day_key == "Day 3":
        return [
            resolve_exercise("goblet_squat",      owned, 3, "12–15",             60),
            resolve_exercise("romanian_deadlift", owned, 3, "8–10 per side",     60),
            resolve_exercise("reverse_lunge",     owned, 3, "12 per leg",        60),
            resolve_exercise("glute_bridge",      owned, 3, "20",                45),
            resolve_exercise("donkey_kick",       owned, 3, "15 per side",       30),
            resolve_exercise("lateral_walk",      owned, 3, "15 steps each way", 30),
            resolve_exercise("cardio_finisher",   owned, 5, "30s on / 15s off",  15),
        ]
    elif day_key == "Day 4":
        return [
            resolve_exercise("chest_press",       owned, 4, "10",         15),
            resolve_exercise("chin_up",           owned, 4, "8",          15),
            resolve_exercise("thruster",          owned, 4, "5 per side", 15),
            resolve_exercise("romanian_deadlift", owned, 4, "5 per side", 15),
            resolve_exercise("glute_bridge",      owned, 4, "15",         15),
            resolve_exercise("cardio_finisher",   owned, 4, "30 seconds", 60),
        ]
    return []

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

        rest_btn = self._make_rest_card()
        days_layout.add_widget(rest_btn)

        scroll.add_widget(days_layout)
        root.add_widget(scroll)

        self.add_widget(root)

    def _make_day_card(self, day_key, day_data):
        card = ColoredBox(bg_color='card', radius=16, orientation='horizontal',
                          size_hint_y=None, height=dp(88), padding=dp(16), spacing=dp(12))

        with card.canvas.before:
            Color(*get_color_from_hex(day_data['color']))
            card._accent_bar = Rectangle()

        def update_bar(*args):
            card._accent_bar.pos = (card.x, card.y + dp(12))
            card._accent_bar.size = (dp(4), card.height - dp(24))
        card.bind(pos=update_bar, size=update_bar)

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
        card.add_widget(Label(text=">", font_size=sp(20), bold=True, color=c('text_dim'),
                               size_hint_x=None, width=dp(20)))

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
        self.phase = 'warmup'
        self.warmup_idx = 0
        self.sets_completed = 0
        self.workout_started = False
        self.paused = False
        self.active_timer_type = None  # 'exercise' | 'rest' | None

    def on_enter(self):
        self.clear_widgets()
        app = App.get_running_app()
        self.day_key = app.current_day
        self.owned = load_equipment()
        base = WORKOUT_PLAN[self.day_key]
        self.day_data = {
            "name":      base["name"],
            "color":     base["color"],
            "warmup":    list(base["warmup"]),
            "exercises": build_workout_for_equipment(self.day_key, self.owned),
        }
        self.current_exercise_idx = 0
        self.current_set = 1
        self.phase = 'warmup'
        self.warmup_idx = 0
        self.sets_completed = 0
        self.workout_started = False
        self.paused = False
        self.active_timer_type = None
        self._build()
        if 'punching_bag' in self.owned:
            Clock.schedule_once(self._show_warmup_choice, 0.3)

    def _show_warmup_choice(self, *args):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(14))
        content.add_widget(Label(
            text="Punching bag detected!\nHow do you want to warm up?",
            font_size=sp(15), color=c('text'), halign='center',
            size_hint_y=None, height=dp(56)))
        regular_box = ColoredBox(bg_color='surface2', radius=10, orientation='vertical',
                                  padding=dp(12), size_hint_y=None, height=dp(54))
        regular_box.add_widget(Label(text="Regular Warmup", font_size=sp(14), bold=True, color=c('text')))
        regular_box.add_widget(Label(text=f"{len(self.day_data['warmup'])} movements — mobility & activation",
                                      font_size=sp(11), color=c('text_dim')))
        content.add_widget(regular_box)
        bag_box = ColoredBox(bg_color='surface2', radius=10, orientation='vertical',
                              padding=dp(12), size_hint_y=None, height=dp(54))
        bag_box.add_widget(Label(text="Bag Warmup", font_size=sp(14), bold=True, color=c('accent')))
        bag_box.add_widget(Label(text=f"{len(BAG_WARMUP)} rounds — footwork, combos & shadow boxing",
                                  font_size=sp(11), color=c('text_dim')))
        content.add_widget(bag_box)
        btn_row = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(10))
        regular_btn = Button(text="Regular", background_normal='', background_color=c('surface2'),
                             color=c('text'), bold=True, font_size=sp(14))
        bag_btn = Button(text="Bag Warmup", background_normal='', background_color=c('accent'),
                         color=c('bg'), bold=True, font_size=sp(14))
        btn_row.add_widget(regular_btn)
        btn_row.add_widget(bag_btn)
        content.add_widget(btn_row)
        popup = Popup(title="Choose Warmup", content=content, size_hint=(0.90, None), height=dp(330),
                      background_color=c('surface'), title_color=c('text'), separator_color=c('accent'))
        regular_btn.bind(on_press=lambda *a: popup.dismiss())
        def pick_bag(*a):
            popup.dismiss()
            self.day_data['warmup'] = list(BAG_WARMUP)
        bag_btn.bind(on_press=pick_bag)
        popup.open()

    def _build(self):
        self.root_layout = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(10))
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
        self.day_label = Label(text=f"{self.day_key}: {self.day_data['name']}",
                               font_size=sp(16), bold=True, color=c('text'))
        topbar.add_widget(self.day_label)
        self.root_layout.add_widget(topbar)

        # Phase indicator
        self.phase_label = Label(text="WARM UP", font_size=sp(11), bold=True,
                                  color=get_color_from_hex(self.day_data['color']),
                                  size_hint_y=None, height=dp(18))
        self.root_layout.add_widget(self.phase_label)

        # Exercise card
        self.exercise_card = ColoredBox(bg_color='surface', radius=20, orientation='vertical',
                                         padding=dp(20), spacing=dp(10),
                                         size_hint_y=None, height=dp(260))
        self.ex_name_label = Label(text="", font_size=sp(20), bold=True,
                                    color=c('text'), halign='center', valign='middle')
        self.ex_name_label.bind(size=self.ex_name_label.setter('text_size'))
        self.exercise_card.add_widget(self.ex_name_label)

        self.ex_detail_label = Label(text="", font_size=sp(14), color=c('accent'),
                                      halign='center', valign='middle',
                                      size_hint_y=None, height=dp(26))
        self.exercise_card.add_widget(self.ex_detail_label)

        self.set_label = Label(text="", font_size=sp(26), bold=True,
                                color=c('accent'), size_hint_y=None, height=dp(36))
        self.exercise_card.add_widget(self.set_label)

        self.weight_label = Label(text="", font_size=sp(13), color=c('text_dim'),
                                   size_hint_y=None, height=dp(20))
        self.exercise_card.add_widget(self.weight_label)
        self.root_layout.add_widget(self.exercise_card)

        # Instruction scroll
        self.instruction_scroll = ScrollView(size_hint_y=None, height=dp(90))
        self.instruction_label = Label(text="", font_size=sp(13), color=c('text_dim'),
                                        halign='center', valign='top',
                                        size_hint_y=None, padding=(dp(10), dp(4)))
        self.instruction_label.bind(texture_size=self.instruction_label.setter('size'))
        self.instruction_label.bind(width=lambda *a: setattr(
            self.instruction_label, 'text_size', (self.instruction_label.width, None)))
        self.instruction_scroll.add_widget(self.instruction_label)
        self.root_layout.add_widget(self.instruction_scroll)

        # Timer display
        self.timer_box = ColoredBox(bg_color='surface2', radius=16, orientation='vertical',
                                     padding=dp(10), size_hint_y=None, height=dp(72))
        self.timer_label = Label(text="", font_size=sp(34), bold=True, color=c('accent'))
        self.timer_sub = Label(text="", font_size=sp(11), color=c('text_dim'),
                                size_hint_y=None, height=dp(16))
        self.timer_box.add_widget(self.timer_label)
        self.timer_box.add_widget(self.timer_sub)
        self.root_layout.add_widget(self.timer_box)
        self.timer_box.opacity = 0

        # Progress bar
        self.progress_bar = ProgressBar(max=100, value=0, size_hint_y=None, height=dp(5))
        self.root_layout.add_widget(self.progress_bar)

        # START button — visible before workout begins
        self.start_btn = FitButton(text="START WORKOUT", accent=True)
        self.start_btn.bind(on_press=self._start_workout)
        self.root_layout.add_widget(self.start_btn)

        # ── Single clean row: Pause | Stop | Done ──
        # Only visible after workout has started
        self.action_row = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(10))

        self.pause_btn = FitButton(text="PAUSE", accent=False)
        self.pause_btn.bind(on_press=self._on_pause_btn)

        self.stop_btn_w = FitButton(text="STOP", accent=False)
        self.stop_btn_w.bind(on_press=self._confirm_stop)
        self.stop_btn_w.size_hint_x = 0.35

        self.done_btn = FitButton(text="DONE", accent=True)
        self.done_btn.bind(on_press=self._next)

        self.action_row.add_widget(self.pause_btn)
        self.action_row.add_widget(self.stop_btn_w)
        self.action_row.add_widget(self.done_btn)
        self.action_row.opacity = 0
        self.action_row.disabled = True
        self.root_layout.add_widget(self.action_row)

        self.add_widget(self.root_layout)
        self._refresh_display()

    # ── BUTTON STATE ──────────────────────────
    def _update_buttons(self):
        """Single method that sets all button states based on current app state."""
        if not self.workout_started:
            self.start_btn.opacity = 1
            self.start_btn.disabled = False
            self.action_row.opacity = 0
            self.action_row.disabled = True
            return

        # Workout is running — hide start, show action row
        self.start_btn.opacity = 0
        self.start_btn.disabled = True
        self.action_row.opacity = 1
        self.action_row.disabled = False

        # Done button label
        if self.phase == 'warmup':
            self.done_btn.text = "DONE"
        else:
            ex = self.day_data['exercises']
            if self.current_exercise_idx < len(ex) and ex[self.current_exercise_idx].get('type') == 'timed':
                self.done_btn.text = "SKIP"
            else:
                self.done_btn.text = "SET DONE"

        # Pause button — label reflects what is currently running
        if self.paused:
            self.pause_btn.text = "RESUME"
        elif self.active_timer_type == 'rest':
            self.pause_btn.text = "PAUSE REST"
        elif self.active_timer_type == 'exercise':
            self.pause_btn.text = "PAUSE"
        else:
            self.pause_btn.text = "PAUSE"

    def _on_pause_btn(self, *args):
        """Route pause button press to the right timer."""
        if self.paused:
            self._resume()
        elif self.active_timer_type == 'rest':
            self._toggle_rest_timer()
        elif self.active_timer_type == 'exercise':
            self._toggle_exercise_timer()
        else:
            self._toggle_start_pause()

    # ── WORKOUT FLOW ──────────────────────────
    def _start_workout(self, *args):
        self.workout_started = True
        self.paused = False
        self._update_buttons()
        self._refresh_display()

    def _toggle_start_pause(self, *args):
        if not self.workout_started:
            self.workout_started = True
            self.paused = False
        elif self.paused:
            self._resume()
            return
        else:
            self.paused = True
            self._cancel_timer()
        self._update_buttons()
        self._refresh_display()

    def _resume(self):
        self.paused = False
        self._update_buttons()
        self._refresh_display()

    def _refresh_display(self):
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
            self.timer_box.opacity = 0

            if self.workout_started and not self.paused:
                if item.get('type') == 'timed':
                    self.active_timer_type = 'exercise'
                    self._start_exercise_timer(item['duration'])

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
            self.timer_box.opacity = 0

            total_ex = len(exercises)
            self.progress_bar.value = 30 + (self.current_exercise_idx / total_ex) * 70

            if self.workout_started and not self.paused:
                if ex.get('type') == 'timed':
                    self.active_timer_type = 'exercise'
                    self._start_exercise_timer(ex.get('duration', 30))

        self._update_buttons()

    # ── TIMERS ────────────────────────────────
    def _start_exercise_timer(self, duration):
        self._cancel_timer()
        self.active_timer_type = 'exercise'
        self.timer_remaining = duration
        self.timer_box.opacity = 1
        self.timer_sub.text = "Exercise Timer"
        self._tick_exercise(0)
        self.timer_event = Clock.schedule_interval(self._tick_exercise, 1)
        self._update_buttons()

    def _tick_exercise(self, dt):
        if self.timer_remaining <= 0:
            self._cancel_timer()
            self.active_timer_type = None
            self._next()
            return
        mins, secs = divmod(self.timer_remaining, 60)
        self.timer_label.text = f"{mins}:{secs:02d}"
        self.timer_remaining -= 1

    def _toggle_exercise_timer(self, *args):
        if self.timer_event:
            self._cancel_timer()
            self.active_timer_type = None
        else:
            self._start_exercise_timer(self.timer_remaining)
        self._update_buttons()

    def _start_rest_timer(self, duration):
        self._cancel_timer()
        self.active_timer_type = 'rest'
        self.timer_remaining = duration
        self.timer_box.opacity = 1
        self.timer_sub.text = "Rest Timer"
        self._tick_rest(0)
        self.timer_event = Clock.schedule_interval(self._tick_rest, 1)
        self._update_buttons()

    def _tick_rest(self, dt):
        if self.timer_remaining <= 0:
            self._cancel_timer()
            self.active_timer_type = None
            self._update_buttons()
            return
        mins, secs = divmod(self.timer_remaining, 60)
        self.timer_label.text = f"{mins}:{secs:02d}"
        self.timer_remaining -= 1

    def _toggle_rest_timer(self, *args):
        if self.timer_event:
            self._cancel_timer()
            self.active_timer_type = None
        else:
            self._start_rest_timer(self.timer_remaining)
        self._update_buttons()

    def _cancel_timer(self):
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None

    # ── NAVIGATION ────────────────────────────
    def _next(self, *args):
        self._cancel_timer()
        self.active_timer_type = None

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
            self._start_rest_timer(rest)
            self._refresh_display()
        else:
            self.current_exercise_idx += 1
            self.current_set = 1
            if self.current_exercise_idx < len(exercises):
                rest = ex.get('rest', 60)
                self._start_rest_timer(rest)
            self._refresh_display()

    def _show_warmup_complete(self):
        self._cancel_timer()
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=dp(40), spacing=dp(24))
        with layout.canvas.before:
            Color(*c('bg'))
            self._wc_bg = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=lambda *a: setattr(self._wc_bg, 'pos', layout.pos),
                    size=lambda *a: setattr(self._wc_bg, 'size', layout.size))

        layout.add_widget(Label(text="Warm Up Complete!", font_size=sp(26), bold=True, color=c('accent')))
        layout.add_widget(Label(text="Time to work.", font_size=sp(16), color=c('text_dim')))

        start_btn = FitButton(text="START WORKOUT", accent=True)
        def begin(*a):
            self.phase = 'workout'
            self.current_exercise_idx = 0
            self.current_set = 1
            self._build()
            self._start_workout()
        start_btn.bind(on_press=begin)
        layout.add_widget(start_btn)
        self.add_widget(layout)

    def _workout_complete(self):
        self._cancel_timer()
        prog = load_progress()
        prog['total_sets'] = prog.get('total_sets', 0) + self.sets_completed
        prog['total_workouts'] = prog.get('total_workouts', 0) + 1
        today = datetime.date.today().isoformat()
        last = prog.get('last_date', '')
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        if last == yesterday or last == today:
            prog['streak'] = prog.get('streak', 0) + 1
        else:
            prog['streak'] = 1
        prog['last_date'] = today
        save_progress(prog)

        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=dp(40), spacing=dp(24))
        with layout.canvas.before:
            Color(*c('bg'))
            self._done_bg = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=lambda *a: setattr(self._done_bg, 'pos', layout.pos),
                    size=lambda *a: setattr(self._done_bg, 'size', layout.size))

        layout.add_widget(Label(text="Workout Complete!", font_size=sp(26), bold=True, color=c('accent')))
        layout.add_widget(Label(text=f"{self.sets_completed} sets done", font_size=sp(16), color=c('text_dim')))
        layout.add_widget(Label(text=f"Streak: {prog['streak']} days", font_size=sp(14), color=c('accent2')))

        home_btn = FitButton(text="BACK TO HOME", accent=True)
        home_btn.bind(on_press=self._go_back)
        layout.add_widget(home_btn)
        self.add_widget(layout)

    def _confirm_stop(self, *args):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(16))
        content.add_widget(Label(text="Stop this workout?\nProgress will not be saved.",
                                  font_size=sp(14), color=c('text'), halign='center'))
        btn_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        cancel = Button(text="Keep Going", background_normal='', background_color=c('surface2'),
                        color=c('text'), bold=True, font_size=sp(14))
        confirm = Button(text="Stop", background_normal='', background_color=c('danger'),
                         color=c('text'), bold=True, font_size=sp(14))
        btn_row.add_widget(cancel)
        btn_row.add_widget(confirm)
        content.add_widget(btn_row)
        popup = Popup(title="Stop Workout", content=content, size_hint=(0.88, None), height=dp(220),
                      background_color=c('surface'), title_color=c('text'), separator_color=c('danger'))
        cancel.bind(on_press=popup.dismiss)
        confirm.bind(on_press=lambda *a: [popup.dismiss(), self._go_back()])
        popup.open()

    def _go_back(self, *args):
        self._cancel_timer()
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

        topbar = BoxLayout(size_hint_y=None, height=dp(50))
        back_btn = Button(text="Back", size_hint_x=None, width=dp(80),
                          background_normal='', background_color=(0,0,0,0),
                          color=c('text_dim'), font_size=sp(14))
        back_btn.bind(on_press=self._go_back)
        topbar.add_widget(back_btn)
        topbar.add_widget(Label(text="Rest Day Stretch", font_size=sp(16),
                                bold=True, color=c('text')))
        self.root_layout.add_widget(topbar)

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
        self.timer_label.color = c('accent')
        self.inst_label.text = s.get('instruction', '')
        self.progress_label.text = f"{self.stretch_idx + 1} of {len(REST_DAY_STRETCHING)}"
        self.progress_bar.value = (self.stretch_idx / len(REST_DAY_STRETCHING)) * 100
        self.start_btn.text = "START"
        self.stop_btn.opacity = 0.3
        self.stop_btn.disabled = True
        self.stretch_timer_paused = False

    def _start_timer(self, *args):
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None
            self.stretch_timer_paused = True
            self.start_btn.text = "RESUME"
            self.stop_btn.opacity = 1
            self.stop_btn.disabled = False
        elif self.stretch_timer_paused:
            self.stretch_timer_paused = False
            self.start_btn.text = "PAUSE"
            self.timer_label.color = c('accent')
            self.timer_event = Clock.schedule_interval(self._tick, 1)
        else:
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

        preset_label = Label(text="PRESETS", font_size=sp(11), bold=True,
                             color=c('accent'), halign='left', valign='middle',
                             size_hint_y=None, height=dp(24))
        preset_label.bind(size=preset_label.setter('text_size'))
        root.add_widget(preset_label)

        self.preset_scroll_holder = BoxLayout(orientation='vertical',
                                              size_hint_y=None, height=dp(56))
        root.add_widget(self.preset_scroll_holder)
        self._build_preset_row()

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