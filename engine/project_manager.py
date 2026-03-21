import json
import os
from pathlib import Path

PROJECTS_DIR = Path("saved_projects")
PROJECTS_DIR.mkdir(exist_ok=True)

def save_custom_project(project_name, config_data):
    """Saves a modification 'recipe' to a JSON file."""
    file_path = PROJECTS_DIR / f"{project_name}.json"
    with open(file_path, "w") as f:
        json.dump(config_data, f, indent=4)
    return file_path

def list_saved_projects():
    """Lists all .json project files."""
    return [f.stem for f in PROJECTS_DIR.glob("*.json")]

def load_project_config(project_name):
    """Loads the settings for a saved project."""
    file_path = PROJECTS_DIR / f"{project_name}.json"
    with open(file_path, "r") as f:
        return json.load(f)