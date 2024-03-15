import logging
import os

logging.basicConfig(level=logging.DEBUG)

project_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
glyphs_dir = os.path.join(project_root_dir, 'assets', 'glyphs')
build_dir = os.path.join(project_root_dir, 'build')
