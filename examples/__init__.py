import os
import shutil

project_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

assets_dir = os.path.join(project_root_dir, 'assets')
glyphs_dir = os.path.join(assets_dir, 'glyphs')

build_dir = os.path.join(project_root_dir, 'build')
outputs_dir = os.path.join(build_dir, 'outputs')

if os.path.exists(build_dir):
    shutil.rmtree(build_dir)
os.makedirs(outputs_dir)
