import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="3D Traversable Game Environment", layout="wide")

st.title("🎮 3D Traversable Game Environment")

st.sidebar.header("🌄 Environment Settings")
sky_color = st.sidebar.color_picker("Sky Color", "#87CEEB")
ground_color = st.sidebar.color_picker("Ground Color", "#2E8B57")
object_color = st.sidebar.color_picker("Object Color", "#FF6347")
light_intensity = st.sidebar.slider("Light Intensity", 0.1, 3.0, 1.2)
num_objects = st.sidebar.slider("Number of Objects", 1, 30, 10)
move_speed = st.sidebar.slider("Move Speed", 0.1, 1.0, 0.3)
look_speed = st.sidebar.slider("Look Sensitivity", 0.1, 1.0, 0.2)

html_code = f"""
<!DOCTYPE html>
<html>
  <head>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/PointerLockControls.js"></script>
  </head>
  <body style="margin:0;overflow:hidden;">
    <div id="blocker" style="position:absolute;top:0;left:0;width:100%;height:100%;background-color:rgba(0,0,0,0.5);">
      <div id="instructions" style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;color:white;font-size:24px;">
        Click to start. Use W, A, S, D to move, Mouse to look.
      </div>
    </div>

    <script>
      const scene = new THREE.Scene();
      scene.background = new THREE.Color("{sky_color}");

      const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
      const renderer = new THREE.WebGLRenderer();
      renderer.setSize(window.innerWidth, window.innerHeight);
      document.body.appendChild(renderer.domElement);

      const light = new THREE.DirectionalLight(0xffffff, {light_intensity});
      light.position.set(1, 1, 1);
      scene.add(light);

      const ambientLight = new THREE.AmbientLight(0x404040);
      scene.add(ambientLight);

      const groundGeometry = new THREE.PlaneGeometry(500, 500, 32, 32);
      const groundMaterial = new THREE.MeshPhongMaterial({{ color: "{ground_color}" }});
      const ground = new THREE.Mesh(groundGeometry, groundMaterial);
      ground.rotation.x = -Math.PI / 2;
      scene.add(ground);

      for (let i = 0; i < {num_objects}; i++) {{
        const size = Math.random() * 2 + 1;
        const geometry = new THREE.BoxGeometry(size, size, size);
        const material = new THREE.MeshPhongMaterial({{ color: "{object_color}" }});
        const cube = new THREE.Mesh(geometry, material);
        cube.position.set((Math.random() - 0.5) * 200, size / 2, (Math.random() - 0.5) * 200);
        scene.add(cube);
      }}

      const controls = new THREE.PointerLockControls(camera, document.body);
      const blocker = document.getElementById('blocker');
      const instructions = document.getElementById('instructions');

      instructions.addEventListener('click', function() {{
        controls.lock();
      }});

      controls.addEventListener('lock', function() {{
        blocker.style.display = 'none';
      }});

      controls.addEventListener('unlock', function() {{
        blocker.style.display = 'block';
      }});

      scene.add(controls.getObject());

      const velocity = new THREE.Vector3();
      const direction = new THREE.Vector3();
      const move = {{ forward: false, backward: false, left: false, right: false }};

      document.addEventListener('keydown', function(e) {{
        switch (e.code) {{
          case 'KeyW': move.forward = true; break;
          case 'KeyA': move.left = true; break;
          case 'KeyS': move.backward = true; break;
          case 'KeyD': move.right = true; break;
        }}
      }});

      document.addEventListener('keyup', function(e) {{
        switch (e.code) {{
          case 'KeyW': move.forward = false; break;
          case 'KeyA': move.left = false; break;
          case 'KeyS': move.backward = false; break;
          case 'KeyD': move.right = false; break;
        }}
      }});

      let prevTime = performance.now();
      function animate() {{
        requestAnimationFrame(animate);

        if (controls.isLocked) {{
          const time = performance.now();
          const delta = (time - prevTime) / 1000;

          velocity.x -= velocity.x * 10.0 * delta;
          velocity.z -= velocity.z * 10.0 * delta;

          direction.z = Number(move.forward) - Number(move.backward);
          direction.x = Number(move.right) - Number(move.left);
          direction.normalize();

          if (move.forward || move.backward) velocity.z -= direction.z * {move_speed} * delta * 50.0;
          if (move.left || move.right) velocity.x -= direction.x * {move_speed} * delta * 50.0;

          controls.moveRight(-velocity.x * delta);
          controls.moveForward(-velocity.z * delta);

          prevTime = time;
        }}

        renderer.render(scene, camera);
      }}

      animate();

      window.addEventListener('resize', () => {{
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
      }});
    </script>
  </body>
</html>
"""

html(html_code, height=750)
