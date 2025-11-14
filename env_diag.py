import streamlit as st
import subprocess
import sys
import importlib

st.set_page_config(layout="wide")
st.title("Python Environment & Package Diagnostic Dashboard")

st.markdown("### Environment Info")

st.code(f"""
Python executable:
{sys.executable}

Python version:
{sys.version}

Active sys.path:
{sys.path}
""")

# -----------------------------------------------------
# PACKAGE CHECKER
# -----------------------------------------------------
st.markdown("## Installed Package Checker")

packages = [
    "geopy",
    "numpy",
    "pandas",
    "sklearn",
    "pydeck",
    "streamlit"
]

missing = []

for pkg in packages:
    try:
        importlib.import_module(pkg)
        st.success(f"{pkg} ✓ Installed")
    except ImportError:
        st.error(f"{pkg} ✗ Missing")
        missing.append(pkg)

# -----------------------------------------------------
# INSTALLATION COMMANDS
# -----------------------------------------------------
st.markdown("## Installation Commands")

if missing:
    st.warning("Some required packages are missing.")

    install_command = f"{sys.executable} -m pip install " + " ".join(missing)

    st.markdown("**Run this inside your virtual environment:**")
    st.code(install_command)

else:
    st.success("All required packages are installed!")

# -----------------------------------------------------
# ENVIRONMENT VALIDATION
# -----------------------------------------------------
st.markdown("## Virtual Environment Verification")

st.markdown("""
This checks whether `streamlit` is running inside the same environment
where you install packages.
""")

try:
    result = subprocess.check_output(
        [sys.executable, "-m", "pip", "list"],
        text=True
    )
    st.code(result)
except Exception as e:
    st.error(e)

st.markdown("""
If you don't see **geopy** in the above list, it means you installed it
into a *different environment* than the one Streamlit is using.
""")

# -----------------------------------------------------
# Fix guide
# -----------------------------------------------------
st.markdown("## Common Fixes")

st.markdown("""
### 1. Activate your environment *before* installing
""")