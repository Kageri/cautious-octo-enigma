import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="3D Game Environment Builder", layout="wide")

st.title("🕹️ 3D Game Environment Builder")

# Sidebar controls
st.sidebar.header("🎨 Environment Controls")
sky_color = st.sidebar.color_picker("Sky Color", "#87CEEB")
ground_color = st.sidebar.color_picker("Ground Color", "#228B22")
object_color = st.sidebar.color_picker("Object Color", "#ff6347")
object_shape = st.sidebar.selectbox("Object Shape", ["Box", "Sphere", "Torus", "Cone"])
light_intensity = st.sidebar.slider("Light Intensity", 0.1, 3.0, 1.0)
rotation_speed = st.sidebar.slider("Rotation Speed", 0.1, 5.0, 1.0)

st.sidebar.subheader("Camera Controls")
camera_z = st.sidebar.slider("Camera Distance (Z)", 2.0, 20.0, 8.0)

# HTML with Three.js for 3D environment
html_code = f"""
<!DOCTYPE html>
<html>
  <head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  </head>
  <body style="margin:0;overflow:hidden;">
    <script>
      const scene = new THREE.Scene();
      scene.background = new THREE.Color("{sky_color}");

      const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
      camera.position.z = {camera_z};

      const renderer = new THREE.WebGLRenderer();
      renderer.setSize(window.innerWidth, window.innerHeight);
      document.body.appendChild(renderer.domElement);

      const light = new THREE.PointLight(0xffffff, {light_intensity});
      light.position.set(10, 10, 10);
      scene.add(light);

      const groundGeometry = new THREE.PlaneGeometry(100, 100);
      const groundMaterial = new THREE.MeshPhongMaterial({{color: "{ground_color}" }});
      const ground = new THREE.Mesh(groundGeometry, groundMaterial);
      ground.rotation.x = -Math.PI / 2;
      ground.position.y = -1.5;
      scene.add(ground);

      let geometry;
      switch ("{object_shape}") {{
        case "Sphere":
          geometry = new THREE.SphereGeometry(1, 32, 32);
          break;
        case "Torus":
          geometry = new THREE.TorusGeometry(1, 0.4, 16, 100);
          break;
        case "Cone":
          geometry = new THREE.ConeGeometry(1, 2, 32);
          break;
        default:
          geometry = new THREE.BoxGeometry(1, 1, 1);
      }}

      const material = new THREE.MeshPhongMaterial({{ color: "{object_color}" }});
      const object = new THREE.Mesh(geometry, material);
      scene.add(object);

      function animate() {{
        requestAnimationFrame(animate);
        object.rotation.x += 0.01 * {rotation_speed};
        object.rotation.y += 0.01 * {rotation_speed};
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

html(html_code, height=700)
