from build123d import *
import math

PARAMS = {
    "name": {"desc": "Person's Name", "default": "JANE DOE", "type": str},
    "title": {"desc": "Job Title", "default": "Creative Director", "type": str},
    "font_size_name": {"desc": "Name Font Size", "default": 12, "type": int},
    "font_size_title": {"desc": "Title Font Size", "default": 6, "type": int},
    "plate_height": {"desc": "Total Height", "default": 35, "type": float},
}

def generate(path, **kwargs):
    # 1. Parameter Extraction
    name_str = str(kwargs.get("name", "JANE DOE"))
    title_str = str(kwargs.get("title", "Creative Director"))
    name_fs = float(kwargs.get("font_size_name", 12))
    title_fs = float(kwargs.get("font_size_title", 6))
    height = float(kwargs.get("plate_height", 35))
    
    # 2. Measure Text for Dynamic Expansion
    # We use Align.CENTER so the text is centered on (0,0)
    name_obj = Text(name_str, font_size=name_fs, font_style=FontStyle.BOLD, align=(Align.CENTER, Align.CENTER))
    title_obj = Text(title_str, font_size=title_fs, align=(Align.CENTER, Align.CENTER))
    
    # Calculate required plate width (Max text width + 30mm for padding)
    max_w = max(name_obj.bounding_box().size.X, title_obj.bounding_box().size.X)
    plate_width = max_w + 30.0 
    
    # 3. Geometry Logic (Side view of the wedge)
    angle = 60.0
    depth = height * 0.9
    slant_offset = height / math.tan(math.radians(angle))
    top_x = depth - slant_offset

    with BuildPart() as obj:
        # 4. Create the Wedge Profile on YZ Plane
        with BuildSketch(Plane.YZ) as profile:
            Polygon([
                (0.0, 0.0),
                (depth, 0.0),
                (top_x, height),
                (0.0, height)
            ])
            fillet(profile.vertices(), radius=2.0)
        
        # Extrude along X-axis. Using both=True ensures the center is at X=0
        extrude(amount=plate_width / 2.0, both=True)
        
        # 5. FIND THE SLANTED FACE
        # We find the face that points forward (+Y)
        target_face = obj.faces().filter_by(GeomType.PLANE).sort_by(Axis.Y)[-1]
        
        # 6. FORCE TEXT ORIENTATION
        # We define a custom plane:
        # - origin: the center of the face
        # - x_dir: (1, 0, 0) -> THIS FORCES TEXT TO RUN ALONG THE PLATE LENGTH
        # - z_dir: the normal of the face (pointing out)
        custom_plane = Plane(
            origin=target_face.center(), 
            x_dir=(1, 0, 0), 
            z_dir=target_face.normal_at()
        )
        
        with BuildSketch(custom_plane) as text_sk:
            # Name at top (Y+ 5)
            with Locations((0, name_fs/1.5)):
                add(name_obj)
            # Title at bottom (Y- 5)
            with Locations((0, -title_fs/1.5)):
                add(title_obj)
                
        # 7. Emboss Text
        extrude(amount=1.5)

    export_stl(obj.part, path)

if __name__ == "__main__":
    # Test with very long name to check expansion
    generate("office_nameplate.stl", name="DR. BARTHOLOMEW J. STRINGFELLOW", title="Senior Research Associate")