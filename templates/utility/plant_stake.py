from build123d import *

PARAMS = {
    "plant": {"desc": "Plant Name", "default": "BASIL", "type": str},
    "length": {"desc": "Spike Length (mm)", "default": 100.0, "type": float}
}

def generate(path: str, **kwargs):
    p, l = kwargs.get("plant", "BASIL"), kwargs.get("length", 100.0)

    with BuildPart() as obj:
        # The Spike
        with BuildSketch():
            Polygon([(-3,0), (3,0), (0, l)])
        extrude(amount=2)
        
        # The Label Plate (Tilted 45 degrees for easy reading)
        plate_plane = Plane(origin=(0, 0, 0), x_dir=(1,0,0), y_dir=(0,-0.707,0.707))
        with BuildPart(plate_plane):
            with BuildSketch():
                Rectangle(60, 20)
                fillet(vertices(), radius=3)
            extrude(amount=2, both=True)
            
            with BuildSketch(Plane(origin=(0,-14.14,14.14), z_dir=(0,-0.707,-0.707))):
                Text(p, font_size=10, font_style=FontStyle.BOLD)
            extrude(amount=1)

    export_stl(obj.part, path)