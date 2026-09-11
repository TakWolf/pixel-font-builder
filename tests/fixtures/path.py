from pathlib import Path

import pytest


@pytest.fixture(scope='session')
def project_root_dir() -> Path:
    return Path(__file__).parent.joinpath('..', '..').resolve()


@pytest.fixture(scope='session')
def assets_dir(project_root_dir: Path) -> Path:
    return project_root_dir.joinpath('assets')


@pytest.fixture(scope='session')
def build_dir(project_root_dir: Path) -> Path:
    return project_root_dir.joinpath('build')
