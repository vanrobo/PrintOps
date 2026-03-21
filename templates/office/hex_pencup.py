from build123d import *

PARAMS = {
    "text": {"desc": "Label", "default": "PENS", "type": str},
    "height": {"desc": "Cup Height (mm)", "default": 90.0, "type": float},
    "radius": {"desc": "Radius (mm)", "default": 35.0, "type": float}
}

def generate(path: str, **kwargs):
    txt, h, r = kwargs.get("text", "PENS"), kwargs.get("height", 90.0), kwargs.get("radius", 35.0)

    with BuildPart() as obj:
        # Solid Hexagon
        with BuildSketch():
            RegularPolygon(radius=r, side_count=6)
        extrude(amount=h)
        
        # Hollow it out (leave 3mm walls and 3mm floor)
        bottom_face = obj.faces().sort_by(Axis.Z)[0]
        offset(amount=-3, openings=[obj.faces().sort_by(Axis.Z)[-1]])

        # Create a drawing plane on the Front face (Y-min)
        front_y = -(r * 0.866) # Math for flat edge of hexagon
        text_plane = Plane(origin=(0, front_y, h/2), z_dir=(0, -1, 0))
        
        with BuildSketch(text_plane):
            Text(txt, font_size=r*0.35, font_style=FontStyle.BOLD)
        extrude(amount=2)

    export_stl(obj.part, path)