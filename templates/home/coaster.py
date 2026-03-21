from build123d import *

PARAMS = {
    "text": {"desc": "Name on Bottom", "default": "VIBE", "type": str},
    "diameter": {"desc": "Coaster Diameter", "default": 100, "type": float},
    "font_size": {"desc": "Font Size", "default": 15, "type": int},
    "thickness": {"desc": "Base Thickness", "default": 4, "type": float},
}

def generate(path, **kwargs):
    # 1. Clean and Cast Parameters
    txt_str = str(kwargs.get("text", "VIBE"))
    dia = float(kwargs.get("diameter", 100))
    f_size = float(kwargs.get("font_size", 15))
    thick = float(kwargs.get("thickness", 4))
    
    # Engrave depth (How deep the text goes into the bottom)
    engrave_depth = 1.0 

    with BuildPart() as obj:
        # 2. Create the main coaster body
        with BuildSketch() as coaster_sk:
            Circle(dia / 2)
        extrude(amount=thick)
        
        # 3. Add a professional "Rim" on the top (optional, makes it look like a coaster)
        top_face = obj.faces().filter_by(GeomType.PLANE).sort_by(Axis.Z)[-1]
        with BuildSketch(top_face) as rim_sk:
            # Create a ring/border
            Circle(dia / 2)
            Circle(dia / 2 - 3, mode=Mode.SUBTRACT)
        extrude(amount=1.5) # Raised rim
        
        # 4. ENGRAVE TEXT ON THE UNDERSIDE
        # We select the lowest face (Z-axis minimum)
        bottom_face = obj.faces().filter_by(GeomType.PLANE).sort_by(Axis.Z)[0]
        
        # When looking at the bottom of a print, we need to ensure the text 
        # is oriented correctly. Plane(bottom_face) works perfectly.
        with BuildSketch(Plane(bottom_face)) as text_sk:
            Text(
                txt_str, 
                font_size=f_size, 
                font_style=FontStyle.BOLD, 
                align=(Align.CENTER, Align.CENTER)
            )
            
        # We use Mode.SUBTRACT and a negative amount to cut INTO the bottom
        extrude(amount=-engrave_depth, mode=Mode.SUBTRACT)

    # 5. Final Export
    export_stl(obj.part, path)

if __name__ == "__main__":
    generate("coaster.stl", text="RELAX", diameter=90)