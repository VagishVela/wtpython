# PyTUI

Helping you find answers to the errors Python spits out.

## Development Tools

- [Flit](https://flit.readthedocs.io/en/latest/) is a simple way to develop Python packages. It's pretty lightweight but can do a lot. We'll use it to manage dependencies.
- [pre-commit](https://pre-commit.com/) will run a few tests before you can commit your code. Don't worry, it will make the changes for you. Worst case, you'll have to type the `git add/commit` lines twice.


## Set up the project

### Create and activate a virtual environment
```
python -m venv .venv --prompt template
source .venv/bin/activate
```

### Upgrade pip and install flit manually
```
python -m pip install -U pip flit
```

### Install the package using symlinks

Run this command to install the package in your virtual environment. If you add dependencies to `pyproject.toml`, you'll have to run this command again to install the new dependencies. Make sure to pin the version in `pyproject.toml`.


```
flit install -s
```

### Install pre-commit
The `.pre-commit-config.yaml` file is configured to perform the following tasks on each commit:

- Validate yaml files
- Validate toml files
- Ensure a single new line on each file
- Ensure trailing whitespaces are removed
- Format your code with black
- Ensure your python imports are sorted consistently

```
pre-commit install
```
