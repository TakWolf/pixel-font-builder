import os

from examples.utils import fs_util

project_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

assets_dir = os.path.join(project_root_dir, 'assets')
glyphs_dir = os.path.join(assets_dir, 'glyphs')

build_dir = os.path.join(project_root_dir, 'build')
outputs_dir = os.path.join(build_dir, 'outputs')

fs_util.delete_dir(build_dir)
fs_util.make_dirs_if_not_exists(outputs_dir)
