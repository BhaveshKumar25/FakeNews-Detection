"""Root entrypoint proxy for FakeNews AI."""
import os
import sys
import importlib.util

# Path to the actual application module in the subfolder
inner_dir = os.path.join(os.path.dirname(__file__), "FakeNews-Detection-Application-main")
app_py_path = os.path.join(inner_dir, "app.py")

if os.path.isdir(inner_dir):
    if inner_dir not in sys.path:
        sys.path.insert(0, inner_dir)
    os.chdir(inner_dir)

# Load the inner app module explicitly to prevent circular import
spec = importlib.util.spec_from_file_location("fakenews_app", app_py_path)
module = importlib.util.module_from_spec(spec)
sys.modules["fakenews_app"] = module
spec.loader.exec_module(module)

app = module.app

if __name__ == "__main__":
    app.run(debug=True, port=5000)
