# main.py
# Simple desktop first-person traversable environment using Ursina
# Install: pip install ursina

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import math

# ---------- Config ----------
WINDOW_TITLE = "Traversable 3D Environment - Ursina"
WORLD_SIZE = 100           # half-size; world spans roughly -WORLD_SIZE..WORLD_SIZE
NUM_OBSTACLES = 120
GROUND_TILE_SCALE = 1.0
# ----------------------------

def make_ground():
    # large tiled ground so player can walk far
    ground = Entity(
        model='plane',
        collider='box',
        scale=(WORLD_SIZE*2, 1, WORLD_SIZE*2),
        texture='white_cube',
        texture_scale=(WORLD_SIZE*2*GROUND_TILE_SCALE, WORLD_SIZE*2*GROUND_TILE_SCALE),
        color=color.rgb(30,120,40)
    )
    ground.y = -1
    return ground

def scattering_obstacles(n=100):
    obstacles = []
    for i in range(n):
        x = random.uniform(-WORLD_SIZE+5, WORLD_SIZE-5)
        z = random.uniform(-WORLD_SIZE+5, WORLD_SIZE-5)
        sx = random.uniform(1.0, 4.0)
        sy = random.uniform(1.0, 6.0)
        sz = random.uniform(1.0, 4.0)

        choice = random.random()
        if choice < 0.75:
            # Box-type obstacles
            ent = Entity(model='cube',
                         position=(x, sy/2 - 0.5, z),
                         scale=(sx, sy, sz),
                         collider='box',
                         color=color.hsv(random.random()*360, 0.6, 0.95),
                         texture='white_cube')
        else:
            # Replace 'cylinder' with 'cone' (available by default)
            ent = Entity(model='cone',
                         position=(x, sy/2 - 0.5, z),
                         scale=(sx*0.8, sy, sz*0.8),
                         collider='box',
                         color=color.rgb(100,90,85),
                         texture='white_cube')
        obstacles.append(ent)
    return obstacles


def make_lighting():
    # directional "sun"
    sun = DirectionalLight()
    sun.look_at(Vec3(1, -1, 1))
    sun.shadow_size = 1024
    sun.light_color = color.rgb(255, 244, 214)
    # ambient fill
    ambient = AmbientLight(color=color.rgb(80,80,90))

def spawn_sky_and_foliage():
    Sky()  # ursina Sky
    # optional distant "trees": simple billboards (low poly)
    for i in range(60):
        angle = random.uniform(0, 2*math.pi)
        r = random.uniform(WORLD_SIZE*0.7, WORLD_SIZE*0.95)
        x = math.cos(angle) * r
        z = math.sin(angle) * r
        trunk = Entity(model='cube', scale=(0.5, random.uniform(2.5,4.5),0.5), position=(x,0.5,z), color=color.rgb(95,60,30), collider=None)
        foliage = Entity(model='sphere', scale=(random.uniform(2.5,4.0)), position=(x,2.5,z), color=color.green, collider=None)

def create_hud(player):
    # basic HUD showing speed, position and tips
    hud_text = Text(f'WASD to move • Mouse to look • Shift to sprint • Space to jump', origin=(0,0), y=0.45, scale=1.25)
    hud_text.background = True
    hud_stats = Text('', origin=(-0.95,0.45), scale=1.0)
    def update_hud():
        hud_stats.text = f'FPS: {application.fps:.0f}   Speed: {player.speed:.1f}   Pos: ({player.x:.1f},{player.y:.1f},{player.z:.1f})'
    hud_stats.update = update_hud
    return hud_text, hud_stats

def main():
    app = Ursina()
    window.title = WINDOW_TITLE
    window.borderless = False
    window.fullscreen = False
    window.exit_button.visible = False
    window.fps_counter.enabled = False  # we'll show custom FPS in HUD

    # Player setup: FirstPersonController provided by ursina
    player = FirstPersonController()
    player.cursor.visible = True
    player.gravity = 1.2          # strength of gravity
    player.jump_height = 2.0
    player.speed = 5              # walking speed
    player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))  # tighter collider

    # Create world
    make_ground()
    obstacles = scattering_obstacles(NUM_OBSTACLES)
    spawn_sky_and_foliage()
    make_lighting()

    # interactive box example (press E to interact)
    interactive_box = Entity(model='cube', position=(5,0.5,5), scale=(1,1,1), color=color.azure, collider='box')
    interaction_text = Text('', origin=(0,-0.45), scale=1.2)

    hud_tip, hud_stats = create_hud(player)

    # optional: mouse sensitivity control
    mouse_sensitivity = 40  # lower = slower look; ursina's default uses mouse.sensitivity
    mouse.sensitivity = mouse_sensitivity

    # Controls: sprint when left shift, toggle cursor with Tab
    def input(key):
        nonlocal player
        if key == 'left shift' or key == 'right shift':
            # handled in update for continuous sprint
            pass
        if key == 'tab':
            window.borderless = not window.borderless
            mouse.locked = not mouse.locked
        if key == 'e' or key == 'E':
            # simple interact: change color
            if distance(player.position, interactive_box.position) < 3:
                interactive_box.color = color.random_color()

    def update():
        # sprint: hold shift
        if held_keys['left shift'] or held_keys['right shift']:
            player.speed = 9
        else:
            player.speed = 5

        # interaction hint
        if distance(player.position, interactive_box.position) < 3:
            interaction_text.text = 'Press E to interact'
        else:
            interaction_text.text = ''

        # keep HUD updated (hud_stats.update was set)
        hud_stats.update()

    # simple debug: spawn more obstacles with key
    def input_key_press(key):
        if key == 'o':
            scattering_obstacles(10)

    # assign handlers
    application._update = update  # ursina calls update each frame
    app.run()

if __name__ == '__main__':
    main()
