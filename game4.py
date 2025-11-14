from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# Ground
ground = Entity(model='plane', collider='box', scale=100, color=color.green)

# Sky
Sky()

# Lighting
DirectionalLight().look_at(Vec3(1, -1, -1))
AmbientLight(color=color.rgba(255, 255, 255, 0.5))

# Player
player = FirstPersonController(y=3, speed=5)
player.cursor.visible = True
player.gravity = 1

# Simple object
cube = Entity(model='cube', color=color.azure, collider='box', position=(5,0.5,5))

app.run()
