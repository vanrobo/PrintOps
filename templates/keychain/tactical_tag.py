from build123d import *

# Define parameters for the automator UI
PARAMS = {
    "text": {"desc": "Label Text", "default": "VIBE", "type": str},
    "font_size": {"desc": "Font Size", "default": 10, "type": int},
    "thickness": {"desc": "Base Thickness", "default": 4, "type": float},
    "emboss": {"desc": "Text Height", "default": 1.5, "type": float},
}

def generate(path, **kwargs):
    # Extract parameters with defaults
    txt_str = kwargs.get("text", "VIBE")
    f_size = kwargs.get("font_size", 10)
    base_h = kwargs.get("thickness", 4)
    txt_h = kwargs.get("emboss", 1.5)
    
    # 1. Create the text first to calculate its bounding box
    # This allows the plate to "auto-size"
    with BuildSketch() as txt_sketch:
        Text(txt_str, font_size=f_size, font_style=FontStyle.BOLD)
    
    # Calculate dimensions based on text size
    # text_width + padding for the hole + padding for the right side
    text_width = txt_sketch.sketch.bounding_box().size.X
    padding = 8
    hole_area = 12
    base_width = text_width + padding + hole_area
    base_height = f_size + padding
    
    with BuildPart() as obj:
        # 2. Generate the Base Plate
        with BuildSketch() as base_sketch:
            # Center the rectangle
            Rectangle(base_width, base_height)
            # Round the corners
            fillet(base_sketch.vertices(), radius=base_height/4)
            
            # 3. Create the Keyring Hole
            # Positioned relative to the left edge
            with Locations((-base_width/2 + hole_area/2 + 2, 0)):
                Circle(3, mode=Mode.SUBTRACT)
        
        extrude(amount=base_h)
        
        # 4. Add the Text
        # We select the top face and filter for the highest flat surface
        top_face = obj.faces().filter_by(GeomType.PLANE).sort_by(Axis.Z)[-1]
        
        with BuildSketch(top_face):
            # Center text in the area to the right of the hole
            text_center_x = (hole_area / 2)
            with Locations((text_center_x, 0)):
                add(txt_sketch)
                
        extrude(amount=txt_h)

    # 5. Export
    export_stl(obj.part, path)

if __name__ == "__main__":
    # Test run
    generate("keychain.stl", text="BUILD123D", font_size=12)