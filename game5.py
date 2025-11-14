# npc_example.py
# Requires: pip install ursina
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import math, random

app = Ursina()

# ---------- World ----------
Sky()
ground = Entity(model='plane', collider='box', scale=100, color=color.lime)
DirectionalLight().look_at(Vec3(1, -1, -1))
AmbientLight(color=color.rgb(255, 255, 255))

player = FirstPersonController(y=3, speed=5)
player.gravity = 1
player.cursor.visible = True

# ---------- Simple NPC Asset ----------
# ---------- Simple NPC Asset ----------
class NPC(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            model='AI NPC High poly.obj',  # <-- Replace with your .obj file path
            scale=.8,                 # Adjust scale as needed
            collider='mesh',          # You can change this to 'mesh' for more accurate collisions
            origin_y=-.5,
            position=(5,0,5),
        )
        self.walk_speed = 2
        self.dialogue_box = None
        for k,v in kwargs.items(): setattr(self,k,v)

    def update(self):
        if distance(self, player) < 8:
            self.look_at_2d(player.position, 'y')
        self.x += math.sin(time.time() * 0.5) * 0.02
        self.z += math.cos(time.time() * 0.5) * 0.02

    def interact(self):
        if self.dialogue_box:
            destroy(self.dialogue_box)
            self.dialogue_box = None
            return
        self.dialogue_box = Text(
            text=random.choice([
                "Hello traveler!",
                "Nice day for a walk.",
                "Stay safe out there!",
                "You have the aura of a hero."
            ]),
            origin=(0,0),
            y=0.35,
            background=True,
            color=color.black,
            scale=1.2
        )

npc = NPC()


# ---------- Input ----------
def input(key):
    if key == 'e':
        if distance(player, npc) < 3:
            npc.interact()

# ---------- HUD ----------
Text("WASD to move • Mouse to look • E to talk", origin=(0,0), y=.45, scale=1.1)

app.run()
