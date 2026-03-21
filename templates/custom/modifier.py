from build123d import *
import os

PARAMS = {
    "file": {"desc": "Base model path (.step/.stl)", "default": "base.stl", "type": str},
    "text": {"desc": "Text to Add", "default": "CUSTOM", "type": str},
    "size": {"desc": "Font Size", "default": 10.0, "type": float},
    "x": {"desc": "X Position", "default": 0.0, "type": float},
    "y": {"desc": "Y Position", "default": 0.0, "type": float},
    "z": {"desc": "Z Position", "default": 20.0, "type": float},
    "rot_x": {"desc": "X Tilt (Pitch)", "default": 0.0, "type": float},
    "rot_y": {"desc": "Y Tilt (Roll)", "default": 0.0, "type": float},
    "rot_z": {"desc": "Z Spin", "default": 0.0, "type": float},
    "depth": {"desc": "Extrude Amount (+ to pop out, - to engrave)", "default": 1.5, "type": float},
}

def generate(path: str, **kwargs):
    file_path = kwargs.get("file", "base.stl").strip('"').strip("'")
    txt = kwargs.get("text", "CUSTOM")
    size = kwargs.get("size", 10.0)
    x, y, z = kwargs.get("x", 0.0), kwargs.get("y", 0.0), kwargs.get("z", 20.0)
    rx, ry, rz = kwargs.get("rot_x", 0.0), kwargs.get("rot_y", 0.0), kwargs.get("rot_z", 0.0)
    depth = kwargs.get("depth", 1.5)

    is_stl = file_path.lower().endswith(".stl")

    if is_stl:
            # ==========================================
            # STL BYPASS MODE (Prevents C++ Crash)
            # ==========================================
            print(f"\n[dim]Detected STL. Using Slicer-Merge bypass...[/dim]")

            # 1. Load the base mesh
            base_shape = import_stl(file_path)

            # 2. Build the text completely independently
            with BuildPart() as text_maker:
                custom_plane = Plane(origin=(x, y, z)) * Rot(rx, ry, rz)
                with BuildSketch(custom_plane):
                    Text(txt, font_size=size, font_style=FontStyle.BOLD)

                if depth < 0:
                    print(f"[yellow]WARNING: Cannot engrave an STL. Forcing text to pop out.[/yellow]")
                extrude(amount=abs(depth))

            # 3. Group them into a Compound (no math required) and export!
            combined_shape = Compound(children=[base_shape, text_maker.part])
            export_stl(combined_shape, path)

    else:
        # ==========================================
        # STEP MODE (True Solid Math)
        # ==========================================
        print(f"\n[dim]Detected STEP. Using True Solid Math...[/dim]")
        
        base_shape = import_step(file_path)
        with BuildPart() as final_part:
            add(base_shape)
            custom_plane = Plane(origin=(x, y, z)) * Rot(rx, ry, rz)
            with BuildSketch(custom_plane):
                Text(txt, font_size=size, font_style=FontStyle.BOLD)
            
            if depth > 0: 
                extrude(amount=depth, mode=Mode.ADD)
            else: 
                extrude(amount=abs(depth), mode=Mode.SUBTRACT)

        export_stl(final_part.part, path)

def calibrate(file_path: str, txt: str, size: float):
    # Live 3D GUI Calibrator
    try:
        from vedo import Mesh, Plotter, Text2D
    except ImportError:
        print("Error: 'vedo' library missing. Run: pip install vedo")
        return None

    print("\nDEBUG: Preparing Live GUI...")
    temp_base_path = file_path
    if file_path.lower().endswith(('.step', '.stp')):
        temp_base_path = os.path.abspath("preview_base.stl")
        export_stl(import_step(file_path), temp_base_path)

    temp_text_path = os.path.abspath("preview_text.stl")

    with BuildPart() as text_maker:
        with BuildSketch():
            Text(txt, font_size=size, font_style=FontStyle.BOLD)
        extrude(amount=5, both=True) 
    export_stl(text_maker.part, temp_text_path)

    plt = Plotter(axes=1, bg="black", title="PrintOps: Drag Sliders -> Close Window to Save")
    base_mesh = Mesh(temp_base_path).color("gray").alpha(0.4)
    active_text = Mesh(temp_text_path).color("red").alpha(1.0)
    plt.add([base_mesh, active_text])

    coords = {"x": 0.0, "y": 0.0, "z": 20.0, "rot_x": 0.0, "rot_y": 0.0, "rot_z": 0.0}

    def update_mesh():
        nonlocal active_text
        plt.remove(active_text)
        active_text = Mesh(temp_text_path).color("red").alpha(1.0)
        active_text.rotate_x(coords["rot_x"]).rotate_y(coords["rot_y"]).rotate_z(coords["rot_z"])
        active_text.pos(coords["x"], coords["y"], coords["z"])
        plt.add(active_text)

    def sx(w, e): coords["x"] = w.value; update_mesh()
    def sy(w, e): coords["y"] = w.value; update_mesh()
    def sz(w, e): coords["z"] = w.value; update_mesh()
    def srx(w, e): coords["rot_x"] = w.value; update_mesh()
    def sry(w, e): coords["rot_y"] = w.value; update_mesh()
    def srz(w, e): coords["rot_z"] = w.value; update_mesh()

    plt.add_slider(sx, -150, 150, value=0, pos=[(0.05, 0.1), (0.35, 0.1)], title="X Position")
    plt.add_slider(sy, -150, 150, value=0, pos=[(0.05, 0.16), (0.35, 0.16)], title="Y Position")
    plt.add_slider(sz, -50, 200, value=20, pos=[(0.05, 0.22), (0.35, 0.22)], title="Z Position")
    plt.add_slider(srx, -180, 180, value=0, pos=[(0.6, 0.1), (0.9, 0.1)], title="X Tilt")
    plt.add_slider(sry, -180, 180, value=0, pos=[(0.6, 0.16), (0.9, 0.16)], title="Y Tilt")
    plt.add_slider(srz, -180, 180, value=0, pos=[(0.6, 0.22), (0.9, 0.22)], title="Z Spin")

    instructions = Text2D("Drag sliders to align text.\nClose window [x] to save.", pos="top-center", c="white", s=1.0)
    plt.add(instructions)

    update_mesh()
    plt.show(interactive=True).close()
    
    if os.path.exists(temp_text_path): os.remove(temp_text_path)
    if temp_base_path == os.path.abspath("preview_base.stl") and os.path.exists(temp_base_path): os.remove(temp_base_path)

    return coords