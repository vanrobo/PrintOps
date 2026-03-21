from build123d import *

PARAMS = {
    "text": {"desc": "Text", "default": "VIBES", "type": str},
    "font": {"desc": "Font Name", "default": "Arial", "type": str},
    "width": {"desc": "Width (mm)", "default": 85.0, "type": float},
}

def generate(path: str, **kwargs):
    text = kwargs.get("text", "VIBES")
    fnt = kwargs.get("font", "Arial")
    w = kwargs.get("width", 85.0)

    with BuildPart() as obj:
        with BuildSketch():
            Rectangle(w, 25)
            fillet(vertices(), radius=min(12, w*0.3))
            with Locations((-w/2 + 8, 0)): 
                Circle(radius=3.5, mode=Mode.SUBTRACT)
        extrude(amount=3)
        
        with BuildSketch(obj.faces().sort_by(Axis.Z)[-1]):
            Text(text, font=fnt, font_size=10, font_style=FontStyle.BOLD)
        extrude(amount=1.5)
        
    export_stl(obj.part, path)