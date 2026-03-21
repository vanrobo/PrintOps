import time
start_time = time.perf_counter()

import typer
import os
import importlib
import subprocess
import shutil
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.theme import Theme
from rich.prompt import Prompt, Confirm
from rich.progress import track
from rich.panel import Panel

# Local Engine Imports
from engine import config_manager, slicer_engine, project_manager

# --- UI CONSTANTS ---
cust_theme = {"primary": "orange1", "gray": "#D4D4D4", "darker": "#454545"}
console = Console(theme=Theme(cust_theme))
line, dot = "│", "[bold gray]◇[/bold gray]"

large_text=r'''│  _____  _____  _____ _   _ _______ ____  _____   _____ 
│ |  __ \|  __ \|_   _| \ | |__   __/ __ \|  __ \ / ____|
│ | |__) | |__) | | | |  \| |  | | | |  | | |__) | (___  
│ |  ___/|  _  /  | | | . ` |  | | | |  | |  ___/ \___ \ 
│ | |    | | \ \ _| |_| |\  |  | | | |__| | |     ____) |
│ |_|    |_|  \_\_____|_| \_|  |_|  \____/|_|    |_____/ '''

# --- HEAVY IMPORTS (Done in background) ---
from build123d import *

# --- TYPER APP INSTANCE ---
app = typer.Typer(help="PrintOps Sovereign - Industrial Hardware Agent")

# ==========================================
# CORE HELPERS
# ==========================================

def get_output_dir() -> Path:
    """Fetches the user's preferred output directory, defaulting to 'outputs'."""
    prefs = config_manager.load_prefs()
    out_dir = prefs.get("output_dir", "outputs")
    path = Path(out_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path

def show_header():
    """Renders the branded CLI header and exact boot time."""
    duration_ms = round((time.perf_counter() - start_time) * 1000)
    console.print(line)
    console.print(f"[primary]{dot}\n{large_text}\n{dot}[/primary]")
    console.print(line)
    console.print(dot, f"[bold][primary]PrintOps Terminal Agent[/primary][/bold] [gray]ready in[/gray]", f"[white]{duration_ms}[/white]ms")
    console.print(line, "[dim][darker]Architected by @vanrobo[/dim][/darker]")
    console.print(line)

def setup_hardware():
    """Blocks execution until a valid Slicer and Printer are configured."""
    s_path = config_manager.get_slicer_path()
    if not s_path:
        console.print(Panel("[bold white]Slicer Engine Required[/bold white]\nPlease paste the path to your Slicer executable (e.g. prusa-slicer-console.exe)", border_style="yellow"))
        s_path = Prompt.ask(f"{line} [primary]Paste Path[/primary]").strip('"').strip("'")
        config_manager.save_pref("slicer_path", s_path)

    printer = config_manager.get_current_printer()
    while not printer:
        console.print(dot, "[bold yellow]Hardware Setup Wizard[/bold yellow]")
        for k, v in config_manager.SUPPORTED_PRINTERS.items():
            console.print(f"{line}   {k}. [white]{v['name']}[/white]")
        p_choice = Prompt.ask(f"{line} [primary]Select Printer[/primary]", choices=list(config_manager.SUPPORTED_PRINTERS.keys()))
        config_manager.save_pref("printer_id", p_choice)
        printer = config_manager.SUPPORTED_PRINTERS.get(p_choice)
    
    return s_path, printer

def run_pipeline(module, user_args, printer_profile, slicer_path, final_name, batch_mode=False, batch_folder_name=None):
    """Handles Forging, Previewing, and Slicing."""
    try:
        base_out = get_output_dir()
        
        # FOLDER LOGIC: Group into a single batch folder if requested, else individual folders
        if batch_folder_name:
            output_dir = base_out / batch_folder_name
        else:
            output_dir = base_out / final_name
            
        output_dir.mkdir(parents=True, exist_ok=True)
        stl_path = output_dir / f"{final_name}.stl"

        # FORGING LOOP (Allows previewing and reconfiguring)
        while True:
            if not batch_mode:
                with console.status(f"{line} [dim]Forging {final_name}...[/dim]"):
                    module.generate(str(stl_path), **user_args)
            else:
                module.generate(str(stl_path), **user_args)

            if batch_mode:
                break 

            console.print(dot, "[bold yellow]Forge Complete.[/bold yellow]")
            action = Prompt.ask(f"{line} [white][V]iew | [S]lice | [R]econfigure[/white]", choices=["V", "S", "R"], default="S").upper()

            if action == "V":
                os.startfile(stl_path) if os.name == 'nt' else subprocess.run(["open", str(stl_path)])
                continue
            elif action == "R":
                for p_name, info in module.PARAMS.items():
                    val = Prompt.ask(f"{line} [primary]{info['desc']}[/primary]", default=str(user_args[p_name]))
                    user_args[p_name] = info['type'](val)
                continue
            elif action == "S":
                break

        # SLICING
        if not batch_mode:
            console.print(dot, f"[bold]Slicing Engine[/bold] [darker]--Target: {printer_profile['name']}[/darker]")
            for _ in track(range(1), description=f"{line} [dim]Computing Machine Code...[/dim]", console=console):
                gcode = slicer_engine.run_slicer(slicer_path, str(stl_path), printer_profile["profile"])
        else:
            gcode = slicer_engine.run_slicer(slicer_path, str(stl_path), printer_profile["profile"])
        
        # REPORTING
        stats = slicer_engine.parse_gcode(gcode)
        if not batch_mode:
            console.print(line)
            console.print(dot, f"[bold green]SUCCESS:[/bold green] [white]{final_name}[/white]")
            console.print(line, f"[darker]Mass   :[/darker] {stats.get('weight', 'N/A')} | [darker]Time:[/darker] {stats.get('time', 'N/A')}")
            console.print(line, f"[darker]Folder :[/darker] [primary]{output_dir.absolute()}[/primary]")
            console.print(line)
            
        return stats

    except Exception as e:
        console.print(line, f"[bold red]Pipeline Failure on {final_name}:[/bold red] {e}")
        return None

# ==========================================
# BATCH PROCESSING
# ==========================================

def generate_example_batch():
    example = """# PRINTOPS MASS PRODUCTION BATCH FILE
#[GLOBAL SETTINGS]
width = 90
font = Impact

# [THE JOBS]
VANROBO
CEO

# [CUSTOM JOBS]
VIBESLAYER | font = Arial | width = 120
"""
    with open("example_batch.txt", "w") as f: f.write(example)
    console.print(Panel("[bold green]Example file created![/bold green]\nOpen [cyan]example_batch.txt[/cyan] to see how it works.", border_style="green"))

def run_batch_processor(filepath, module, printer, s_path, display_name):
    if not os.path.exists(filepath):
        console.print(line, f"[bold red]File not found: {filepath}[/bold red]")
        return

    jobs, globals_params =[], {}
    with open(filepath, "r") as f:
        for text_line in f:
            text_line = text_line.strip()
            if not text_line or text_line.startswith("#"): continue
            
            if "|" in text_line:
                parts = text_line.split("|")
                job_args = {}
                for p in parts[1:]:
                    if "=" in p:
                        k, v = p.split("=", 1) 
                        job_args[k.strip()] = v.strip()
                jobs.append({"text": parts[0].strip(), "args": job_args})
            elif "=" in text_line and len(jobs) == 0:
                k, v = text_line.split("=")
                globals_params[k.strip()] = v.strip()
            else:
                jobs.append({"text": text_line, "args": {}})

    master_batch_folder = f"BATCH_RUN_{display_name}_{time.strftime('%H%M%S')}"
    base_out = get_output_dir()

    console.print(dot, f"[bold]Batch Initialized:[/bold] Found {len(jobs)} items.")
    console.print(line, f"[dim]Target Directory: {base_out}/{master_batch_folder}[/dim]")
    
    for i, job in enumerate(jobs, 1):
        console.print(dot, f"[dim]Processing {i}/{len(jobs)}:[/dim] [white]{job['text']}[/white]")
        current_args = {}
        for p_name, info in module.PARAMS.items():
            raw_val = job['args'].get(p_name, globals_params.get(p_name, info['default']))
            if p_name in ['text', 'name']: raw_val = job['text']
            current_args[p_name] = info['type'](raw_val)

        ident = job['text'].replace(" ", "_")
        final_name = f"{display_name}_{ident}_{i}" 
        
        stats = run_pipeline(module, current_args, printer, s_path, final_name, batch_mode=True, batch_folder_name=master_batch_folder)
        
        if stats: 
            console.print(line, f"[darker]↳ Mass: {stats.get('weight','N/A')} | Time: {stats.get('time','N/A')}[/darker]")

    console.print(line)
    console.print(dot, f"[bold green]Batch Complete![/bold green] All outputs saved to [primary]{base_out}/{master_batch_folder}[/primary]")

# ==========================================
# INTERACTIVE MENU (DEFAULT ROUTER)
# ==========================================

@app.callback(invoke_without_command=True)
def main_router(ctx: typer.Context):
    """If no subcommand is passed, run the Interactive Menu."""
    if ctx.invoked_subcommand is None:
        interactive_menu()

def interactive_menu():
    show_header()
    s_path, printer = setup_hardware()

    console.print(dot, "[bold]Operational Mode[/bold]")
    console.print(f"{line}   1. Standard Single Template")
    console.print(f"{line}   2. Custom Model Modifier")
    console.print(f"{line}   3. Load Saved Recipe")
    console.print(f"{line}   4. Mass Production [yellow](Batch .txt)[/yellow]")
    mode = Prompt.ask(f"{line} [primary]Choice[/primary]", choices=["1", "2", "3", "4"], default="1")

    module = None
    display_name = ""

    if mode in ["1", "4"]:
        root = Path("templates")
        cats =[d.name for d in root.iterdir() if d.is_dir() and d.name not in["__pycache__", "custom"]]
        console.print(dot, "[bold]Category[/bold]")
        for i, c in enumerate(cats, 1): console.print(f"{line}   {i}.[white]{c.capitalize()}[/white]")
        selected_cat = cats[int(Prompt.ask(f"{line} [primary]Choice[/primary]", choices=[str(i) for i in range(1, len(cats)+1)])) - 1]

        mods =[f.stem for f in (root / selected_cat).glob("*.py") if f.name != "__init__.py"]
        console.print(dot, "[bold]Model[/bold]")
        for i, m in enumerate(mods, 1): console.print(f"{line}   {i}. [white]{m.capitalize()}[/white]")
        selected_mod = mods[int(Prompt.ask(f"{line} [primary]Choice[/primary]", choices=[str(i) for i in range(1, len(mods)+1)])) - 1]
        
        module = importlib.import_module(f"templates.{selected_cat}.{selected_mod}")
        display_name = selected_mod.capitalize()

    elif mode == "2":
        module = importlib.import_module("templates.custom.modifier")
        display_name = "Modified"

    elif mode == "3":
        saved = project_manager.list_saved_projects()
        if not saved: 
            console.print(line, "[bold red]No saved recipes found.[/bold red]")
            return
        console.print(dot, "[bold]Saved Recipes[/bold]")
        for i, p in enumerate(saved, 1): console.print(f"{line}   {i}. [white]{p}[/white]")
        p_name = saved[int(Prompt.ask(f"{line}[primary]Choice[/primary]", choices=[str(i) for i in range(1, len(saved)+1)])) - 1]
        
        user_args = project_manager.load_project_config(p_name)
        module = importlib.import_module("templates.custom.modifier")
        
        txt_key = 'text' if 'text' in user_args else 'name'
        user_args[txt_key] = Prompt.ask(f"{line} [primary]Update Text[/primary]", default=user_args.get(txt_key, 'job'))
        
        ident = user_args.get(txt_key, 'job').replace(" ", "_")
        final_name = f"{p_name}_{ident}_{time.strftime('%H%M')}"
        run_pipeline(module, user_args, printer, s_path, final_name)
        return

    if mode == "4":
        console.print(line)
        batch_file = Prompt.ask(f"{line} [primary]Enter path to batch .txt file (or type 'help')[/primary]")
        if batch_file.lower() == 'help':
            generate_example_batch()
            return
        run_batch_processor(batch_file.strip('"').strip("'"), module, printer, s_path, display_name)
        return

    user_args = {}
    if hasattr(module, 'PARAMS'):
        console.print(dot, "[bold]Configuration[/bold]")
        if mode == "2":
            for p in['file', 'text', 'size']:
                val = Prompt.ask(f"{line} [primary]{module.PARAMS[p]['desc']}[/primary]", default=str(module.PARAMS[p]['default']))
                user_args[p] = module.PARAMS[p]['type'](val)
            user_args['file'] = user_args['file'].strip('"').strip("'")
            
            if Confirm.ask(f"{line} [bold yellow]Open Visual GUI Calibrator?[/bold yellow]"):
                console.print(f"{line} [dim]Launching 3D Window...[/dim]")
                final_coords = module.calibrate(user_args['file'], user_args['text'], user_args['size'])
                if final_coords: 
                    user_args.update(final_coords)
                    console.print(f"{line} [green]Coordinates locked successfully.[/green]")
                else:
                    console.print(f"{line} [red]Calibration aborted.[/red]")
                    return
            else:
                for p in['x', 'y', 'z', 'rot_x', 'rot_y', 'rot_z']:
                    val = Prompt.ask(f"{line} [primary]{module.PARAMS[p]['desc']}[/primary]", default=str(module.PARAMS[p]['default']))
                    user_args[p] = module.PARAMS[p]['type'](val)
            
            val = Prompt.ask(f"{line}[primary]{module.PARAMS['depth']['desc']}[/primary]", default=str(module.PARAMS['depth']['default']))
            user_args['depth'] = module.PARAMS['depth']['type'](val)
        else:
            for p_name, info in module.PARAMS.items():
                val = Prompt.ask(f"{line} [primary]{info['desc']}[/primary]", default=str(info['default']))
                user_args[p_name] = info['type'](val)

    ident = user_args.get('text', user_args.get('name', 'job')).replace(" ", "_")
    final_name = f"{display_name}_{ident}_{time.strftime('%H%M')}"

    if mode == "2" and Confirm.ask(f"{line} [yellow]Save recipe?[/yellow]"):
        p_name = Prompt.ask(f"{line} [primary]Recipe Name[/primary]", default=ident.lower())
        path = project_manager.save_custom_project(p_name, user_args)
        console.print(f"{line} [dim]Saved to {path}[/dim]")

    run_pipeline(module, user_args, printer, s_path, final_name)


# ==========================================
# CLI POWER-USER COMMANDS
# ==========================================

@app.command(name="build")
def cli_build(
    category: str = typer.Argument(..., help="The folder name (e.g., keychain, trophies, office)"),
    model: str = typer.Argument(..., help="The file name without .py (e.g., tactical_tag)"),
    text: str = typer.Argument(..., help="The text to apply to the model")
):
    """Directly forge ANY model from your templates folder via CLI."""
    show_header()
    s_path, printer = setup_hardware()
    
    try:
        module = importlib.import_module(f"templates.{category}.{model}")
    except ImportError:
        console.print(f"[bold red]Error: Could not find 'templates/{category}/{model}.py'[/bold red]")
        console.print(f"[dim]Check your spelling and ensure the folder/file exists.[/dim]")
        return

    user_args = {}
    if hasattr(module, 'PARAMS'):
        for p_name, info in module.PARAMS.items():
            user_args[p_name] = info['default']
    
    txt_key = 'text' if 'text' in user_args else 'name'
    user_args[txt_key] = text
    
    final_name = f"{category.capitalize()}_{model.capitalize()}_{text.replace(' ', '_')}_{time.strftime('%H%M')}"
    run_pipeline(module, user_args, printer, s_path, final_name)


@app.command(name="list")
def cli_list():
    """List all available manufacturing categories and templates."""
    console.print(line)
    console.print(dot, "[bold]Available Template Library[/bold]")
    
    root = Path("templates")
    if not root.exists():
        console.print(f"{line}[red]No templates folder found.[/red]")
        return

    cats =[d for d in root.iterdir() if d.is_dir() and d.name not in ["__pycache__", "custom"]]
    
    for cat in cats:
        console.print(f"{line}   [bold primary]📁 {cat.name.capitalize()}[/bold primary]")
        mods =[f.stem for f in cat.glob("*.py") if f.name != "__init__.py"]
        for i, m in enumerate(mods):
            branch = "└──" if i == len(mods) - 1 else "├──"
            console.print(f"{line}   {branch} ⚙️ {m}")
            
    console.print(line)


@app.command(name="batch")
def cli_batch(
    filepath: str = typer.Argument(..., help="Path to the .txt batch file"),
    category: str = typer.Argument(..., help="Category folder (e.g., keychain)"),
    model: str = typer.Argument(..., help="Model file (e.g., tactical_tag)")
):
    """Run a mass-production batch job directly from a text file."""
    show_header()
    s_path, printer = setup_hardware()
    
    try:
        module = importlib.import_module(f"templates.{category}.{model}")
    except ImportError:
        console.print(f"[bold red]Error: Could not find templates/{category}/{model}.py[/bold red]")
        return
        
    display_name = model.capitalize()
    run_batch_processor(filepath, module, printer, s_path, display_name)


@app.command(name="config")
def cli_config(
    reset: bool = typer.Option(False, "--reset", help="Wipes the current hardware configuration"),
    set_outdir: Optional[str] = typer.Option(None, "--set-outdir", help="Change the default output directory path")
):
    """View, reset, or update your system configurations."""
    console.print(line)
    
    # 1. Handle Reset Flag
    if reset:
        if os.path.exists("user_preferences.json"):
            os.remove("user_preferences.json")
        console.print(dot, "[bold green]Configuration wiped.[/bold green] You will be prompted to set it up on your next run.")
        console.print(line)
        return

    # 2. Handle Directory Override Flag
    if set_outdir:
        config_manager.save_pref("output_dir", set_outdir)
        console.print(dot, f"[bold green]Output directory updated to:[/bold green][white]{set_outdir}[/white]")
        console.print(line)
        return

    # 3. View Current Config
    prefs = config_manager.load_prefs()
    console.print(dot, "[bold]Current Hardware Configuration[/bold]")
    
    s_path = prefs.get('slicer_path', 'Not Configured')
    console.print(f"{line}   [darker]Slicer Engine:[/darker] [white]{s_path}[/white]")
    
    p_id = prefs.get('printer_id')
    if p_id and p_id in config_manager.SUPPORTED_PRINTERS:
        p_name = config_manager.SUPPORTED_PRINTERS[p_id]['name']
    else:
        p_name = "Not Configured"
    console.print(f"{line}   [darker]Target Printer:[/darker] [primary]{p_name}[/primary]")
    
    out_dir = prefs.get('output_dir', 'outputs (Default)')
    console.print(f"{line}   [darker]Output Directory:[/darker] [primary]{out_dir}[/primary]")
    
    console.print(line)


@app.command(name="clean")
def cli_clean(
    force: bool = typer.Option(False, "--force", "-f", help="Bypass the confirmation prompt")
):
    """Deletes all generated files in your current outputs directory."""
    output_dir = get_output_dir()
    
    if not output_dir.exists() or not any(output_dir.iterdir()):
        console.print(f"{line}\n{dot}[dim]Output directory ({output_dir}) is already empty.[/dim]\n{line}")
        return

    if not force:
        if not Confirm.ask(f"{line} [bold red]WARNING: This will delete all generated STLs and G-code in '{output_dir}'. Continue?[/bold red]"):
            console.print(f"{line} [dim]Clean aborted.[/dim]\n{line}")
            return

    shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True) 
    
    console.print(f"{line}\n{dot} [bold green]Outputs directory '{output_dir}' cleaned successfully.[/bold green]\n{line}")

if __name__ == "__main__":
    app()