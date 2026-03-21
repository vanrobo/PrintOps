import subprocess
import os
import json
import pathlib

COMMON_PATHS = [
    r"C:\Program Files\Prusa3D\PrusaSlicer\prusa-slicer-console.exe",
    r"C:\Program Files\OrcaSlicer\orca-slicer.exe",
    "/Applications/PrusaSlicer.app/Contents/MacOS/PrusaSlicer"
]

def find_slicer():
    if os.path.exists("user_preferences.json"):
        with open("user_preferences.json", "r") as f:
            try:
                prefs = json.load(f)
                if "slicer_path" in prefs and os.path.exists(prefs["slicer_path"]):
                    return prefs["slicer_path"]
            except: pass
    for path in COMMON_PATHS:
        if os.path.exists(path): return path
    return None

def run_slicer(slicer_path: str, stl_path: str, config_path: str):
    stl = pathlib.Path(stl_path).absolute()
    gcode = stl.with_suffix(".gcode")
    config = pathlib.Path(config_path).absolute()
    
    command =[
        slicer_path,
        "--load", str(config),       # 1. Load the printer profile first
        "--export-gcode", str(stl),  # 2. Tell it to slice the STL
        "--output", str(gcode)       # 3. Define the output destination
    ]
    
    subprocess.run(command, capture_output=True, text=True, check=True)
    return gcode

def parse_gcode(gcode_path: str):
    """
    Tank-Grade Parser: Hunts for numbers in the G-code footer.
    Handles the '0.00g' bug by calculating mass from cm3 volume.
    """
    stats = {"weight": "Unknown", "time": "Unknown"}
    
    target = pathlib.Path(gcode_path).absolute()
    
    if not target.exists():
        return stats

    try:
        with open(target, "r", encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            search_area = lines[-1000:]
            
            volume_cm3 = 0.0

            for line in search_area:
                l = line.strip().lower()

                if "estimated printing time" in l and "mode" in l:
                    if "=" in l:
                        stats["time"] = l.split("=")[1].strip()

                if "filament used [cm3]" in l:
                    try:
                        val = l.split("=")[1].strip()
                        volume_cm3 = float(val)
                    except: pass


                if "total filament used [g]" in l:
                    try:
                        val = l.split("=")[1].strip()
                        if val != "0.00":
                            stats["weight"] = val + "g"
                    except: pass


            if (stats["weight"] == "Unknown") and volume_cm3 > 0:
                calculated_mass = round(volume_cm3 * 1.24, 2)
                stats["weight"] = f"{calculated_mass}g (est.)"

    except Exception as e:
        pass

    return stats