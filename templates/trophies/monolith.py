from build123d import *

PARAMS = {
    "text": {"desc": "Winner", "default": "CHAMPION", "type": str},
    "height": {"desc": "Height (mm)", "default": 100.0, "type": float}
}

def generate(path: str, **kwargs):
    txt, h = kwargs.get("text", "CHAMPION"), kwargs.get("height", 100.0)

    with BuildPart() as obj:
        # Bottom Base
        Box(80, 50, 10)
        # Pillar
        with BuildSketch(Plane.XY.offset(10)):
            Rectangle(40, 30)
        extrude(amount=h-10)

        # Create a plaque on the front (Y = -15 is the front of the 30mm pillar)
        plaque_plane = Plane(origin=(0, -15, h/2), z_dir=(0, -1, 0))
        with BuildPart(plaque_plane) as p:
            with BuildSketch():
                Rectangle(50, 30)
            extrude(amount=3) # Plaque thickness
            
            # Text on top of plaque
            with BuildSketch(p.faces().sort_by(Axis.Z)[-1]):
                Text(txt.upper(), font_size=8, font_style=FontStyle.BOLD)
            extrude(amount=1.5)

    export_stl(obj.part, path)