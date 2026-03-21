from build123d import *

def generate(text: str, path: str):
    """Generates a high-end Cyber-Monolith award."""
    # We define our dimensions up front
    base_h = 15
    pillar_h = 80
    
    with BuildPart() as trophy:
        # 1. THE BASE (Layer 1)
        with BuildSketch() as base_sk:
            Rectangle(100, 60)
            fillet(base_sk.vertices(), radius=10)
        extrude(amount=base_h)
        
        # 2. THE PILLAR (Layer 2)
        # Instead of searching for the top face, we know it's at Z = base_h
        with BuildSketch(Plane.XY.offset(base_h)) as pillar_sk:
            Rectangle(40, 25)
            fillet(pillar_sk.vertices(), radius=5)
        # We use a smaller taper (3 degrees) to keep it stable
        extrude(amount=pillar_h, taper=3)

        # 3. THE NAME PLATE (The 'Edit' spot)
        # We know the front of the trophy is at Y = -30 (half of base width)
        # We create a plane sitting right there
        plaque_plane = Plane(origin=(0, -22, base_h + (pillar_h/2)), z_dir=(0, -1, 0))
        
        with BuildPart(plaque_plane) as plaque:
            with BuildSketch():
                Rectangle(70, 30)
                # Cool angled corners for a 'hacker' look
                chamfer(vertices(), length=5)
            extrude(amount=4) # Plaque thickness

            # 4. THE ENGRAVING (The variable part)
            # Draw on the front of the plaque we just made
            with BuildSketch(plaque.faces().sort_by(Axis.Z)[-1]):
                # Make the text uppercase for that 'Award' feel
                Text(text.upper(), font_size=8, font_style=FontStyle.BOLD)
            
            # Carve it in!
            extrude(amount=-1.5, mode=Mode.SUBTRACT)

    export_stl(trophy.part, path)