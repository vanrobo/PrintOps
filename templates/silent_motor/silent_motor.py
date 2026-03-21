from build123d import *
def generate(text, path):
    with BuildPart() as obj:
        Cylinder(radius=40, height=15)
        Cylinder(radius=11, height=15, mode=Mode.SUBTRACT) # Bearing hole
        top = obj.faces().sort_by(Axis.Z)[-1]
        with BuildSketch(top):
            with PolarLocations(radius=40, count=12):
                with Locations((0, -7.5)): SlotCenterToCenter(15, 9, rotation=90)
        extrude(amount=-15, mode=Mode.SUBTRACT)
    export_stl(obj.part, path)