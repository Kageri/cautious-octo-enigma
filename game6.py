# npc_webhook.py
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import requests
import threading

app = Ursina()

# ---------- World ----------
Sky()
ground = Entity(model='plane', collider='box', scale=100, color=color.lime)
DirectionalLight().look_at(Vec3(1, -1, -1))
AmbientLight(color=color.rgb(255, 255, 255))

player = FirstPersonController(y=3, speed=5)
player.gravity = 1
player.cursor.visible = True

WEBHOOK_URL = 'https://your-webhook-url.com/endpoint'  # Replace with your webhook URL

# ---------- NPC ----------
class NPC(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            model='AI NPC High poly.obj',
            scale=(0.8,1.6,0.8),
            color=color.rgb(255,220,180),
            collider='box',
            origin_y=-.5,
            position=(5,0,5),
        )
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

        # Send player's message to webhook in a separate thread
        def send_to_webhook(message):
            try:
                resp = requests.post(WEBHOOK_URL, json={"message": message})
                reply = resp.json().get("reply", "No response")
            except Exception as e:
                reply = f"Error: {e}"
            self.dialogue_box = Text(
                text=reply,
                origin=(0,0),
                y=0.35,
                background=True,
                color=color.black,
                scale=1.2
            )

        # Example: send a fixed message for now
        threading.Thread(target=send_to_webhook, args=("Hello from player!",)).start()

npc = NPC()

# ---------- Input ----------
def input(key):
    if key == 'e':
        if distance(player, npc) < 3:
            npc.interact()

# ---------- HUD ----------
Text("WASD to move • Mouse to look • E to talk", origin=(0,0), y=.45, scale=1.1)

app.run()
