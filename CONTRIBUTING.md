## Contributing

Contributions are welcome!

For typos and minor corrections, please feel free to submit a PR. For technical changes, please speak with the core team first. We'd hate to turn down your awesome work.

Note: Due to a [limitation in textual](https://github.com/willmcgugan/textual/issues/14), Windows is not supported, but fear not, this works in [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10).

1. Fork the repository to get started.

2. Clone the repo and enter the `wtpython` folder.

```
git clone https://github.com/<your-name>/wtpython.git
cd wtpython
```

3. Create and activate a virtual environment.
```
python -m venv .venv --prompt template
source .venv/bin/activate
```

4. Upgrade pip and install [Flit](https://flit.readthedocs.io/en/latest/).
```
python -m pip install --upgrade pip flit
```

5. Install the package in editable mode.
```
flit install -s
```

If you add dependencies to the project, you'll have to run this command again to install the new dependencies. Make sure to pin the version in `pyproject.toml`. This software is under a MIT license, so all dependencies must respect this. There is an automated test that will block contributions that violate MIT.


6. Install [pre-commit](https://pre-commit.com/).
```
pre-commit install
```

The `.pre-commit-config.yaml` file is configured to perform the following tasks on each commit:

- Validate yaml files
- Validate toml files
- Ensure a single new line on each file
- Ensure trailing white spaces are removed
- Ensure `noqa` annotations have specific codes
- Ensure your python imports are sorted consistently
- Check for errors with flake8

7. Create a new branch in your repo.
```
git checkout -b <mybranch>
```

8. Make some awesome changes!

We're excited to see what you can do. 🤩

9. Commit your changes.
```
git add .
git commit -m "<description of changes>"
```

10. Push your changes up to your repository.
```
git push --set-upstream origin <mybranch>
```

11. Open a Pull Request.
Please provide a good description to help us understand what you've done. We are open to your suggestions and hope you'll be open to feedback if necessary.

12. Celebrate! You've just made an open-source contribution, 🎉 and you deserve a gold star! ⭐
