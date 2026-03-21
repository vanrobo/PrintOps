import json
import os
from pathlib import Path

PREFS_FILE = "user_preferences.json"

# Hardware Registry - All these use the Universal .ini method
SUPPORTED_PRINTERS = {
    "1": {"name": "Bambu Lab A1", "profile": "profiles/a1_standard.ini"},
    "2": {"name": "Bambu Lab A1 Mini", "profile": "profiles/a1_mini.ini"},
    "3": {"name": "Prusa MK4 / MK3S", "profile": "profiles/prusa_mk4.ini"},
}

def load_prefs():
    if os.path.exists(PREFS_FILE):
        with open(PREFS_FILE, "r") as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_pref(key, value):
    prefs = load_prefs()
    prefs[key] = value
    with open(PREFS_FILE, "w") as f:
        json.dump(prefs, f, indent=4)

def get_slicer_path():
    prefs = load_prefs()
    if "slicer_path" in prefs and os.path.exists(prefs["slicer_path"]):
        return prefs["slicer_path"]
    
    # Auto-Discovery (Hunts for the specific Console version of PrusaSlicer)
    common_spots = [
        r"C:\Program Files\Prusa3D\PrusaSlicer\prusa-slicer-console.exe",
        "/Applications/PrusaSlicer.app/Contents/MacOS/PrusaSlicer",
    ]
    
    for spot in common_spots:
        if os.path.exists(spot):
            save_pref("slicer_path", spot)
            return spot
            
    return None

def get_current_printer():
    p_id = load_prefs().get("printer_id")
    return SUPPORTED_PRINTERS.get(p_id)