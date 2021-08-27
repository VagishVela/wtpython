"""Keep requirements.txt in sync with pyproject.toml.

Since flit uses pyproject.toml to build, it does not need requirements.txt.
However, github uses requirements.txt to track dependencies. Therefore,
this script will allow us to keep the requirements.txt file in sync with
pyproject.toml. This will allow for dependabot to track dependencies and
for us to be discoverable through our dependencies.
"""
from pathlib import Path

import toml

PROJECT_ROOT = Path(__file__).parent.parent
TOML_FILE = PROJECT_ROOT / 'pyproject.toml'
REQ_FILE = PROJECT_ROOT / 'requirements.txt'

config = toml.load(TOML_FILE)
metadata = config['tool']['flit']['metadata']

requirements = "\n".join(sorted([
    *metadata['requires'],
    *metadata['requires-extra']['test'],
    *metadata['requires-extra']['dev'],
]))

REQ_FILE.write_text(f"""
# This file auto-generated from `scripts/update_requirements.py`
# Do not edit by hand.
{requirements}
""".lstrip())
