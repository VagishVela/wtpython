# Python Discord Code Jam Repository Template

## A Primer
Hello code jam participants! We've put together this repository template for you to use in [our code jams](https://pythondiscord.com/events/) or even other Python events!

This document will contain the following information:
1. [What does this template contain?](#what-does-this-template-contain)
2. [How do I use it?](#how-do-i-use-it)
3. [How do I adapt it to my project?](#how-do-i-adapt-it-to-my-project)

You can also look at [our style guide](https://pythondiscord.com/events/code-jams/code-style-guide/) to get more information about what we consider a maintainable code style.

## What does this template contain?

Here is a quick rundown of what each file in this repository contains:
- `LICENSE`: [The MIT License](https://opensource.org/licenses/MIT), an OSS approved license which grants rights to everyone to use and modify your projects and limits your liability. We highly recommend you to read the license.
- `.gitignore`: A list of files that will be ignored by Git. Most of them are auto-generated or contain data that you wouldn't want to share publicly.
- `dev-requirements.txt`: Every PyPI packages used for the project's development, to ensure a common and maintainable code style. [More on that below](#using-the-default-pip-setup).
- `tox.ini`: The configurations of two of our style tools: [`flake8`](https://pypi.org/project/flake8/) and [`isort`](https://pypi.org/project/isort/).
- `.pre-commit-config.yaml`: The configuration of the [`pre-commit`](https://pypi.org/project/pre-commit/) tool.
- `.github/workflows/lint.yaml`: A [GitHub Actions](https://github.com/features/actions) workflow, a set of actions run by GitHub on their server after each push, to ensure the style requirements are met.

Each of these files have comments for you to understand easily, and modify to fit your needs.

### flake8: general style rules

Our first and probably most important tool is flake8. It will run a set of plugins on your codebase and warn you about any non-conforming lines.
Here is a sample output:
```
~> flake8
./app.py:1:1: D100 Missing docstring in public module
./app.py:1:6: N802 function name 'helloWorld' should be lowercase
./app.py:1:16: E201 whitespace after '('
./app.py:1:17: ANN001 Missing type annotation for function argument 'name'
./app.py:1:23: ANN201 Missing return type annotation for public function
./app.py:2:1: D400 First line should end with a period
./app.py:2:1: D403 First word of the first line should be properly capitalized
./app.py:3:19: E225 missing whitespace around operator
```

Each line corresponds to an error. The first part is the file path, then the line number, and the column index.
Then comes the error code, a unique identifier of the error, and then a human-readable message.

If, for any reason, you do not wish to comply with this specific error on a specific line, you can add `# noqa: CODE` at the end of the line.
For example:
```python
def helloWorld():  # noqa: N802
    ...
```
will pass linting. Although we do not recommend ignoring errors unless you have a good reason to do so.

It is run by calling `flake8` in the project root.

#### Plugin List:

- `flake8-annotations`: Checks your code for the presence of [type-hints](https://docs.python.org/3/library/typing.html).
- `flake8-bandit`: Checks for common security breaches.
- `flake8-docstring`: Checks that you properly documented your code.
- `flake8-isort`: Makes sure you ran ISort on the project.

### ISort: automatic import sorting

This second tool will sort your imports according to the [PEP8](https://www.python.org/dev/peps/pep-0008/#imports). That's it! One less thing for you to do!

It is run by calling `isort .` in the project root. Notice the dot at the end, it tells ISort to use the current directory.

### Pre-commit: run linting before committing

This third tool doesn't check your code, but rather makes sure that you actually *do* check it.

It makes use of a feature called [Git hooks](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks) which allow you to run a piece of code before running `git commit`.
The good thing about it is that it will cancel your commit if the lint doesn't pass. You won't have to wait for Github Actions to report and have a second fix commit.

It is *installed* by running `pre-commit install` and can be run manually by calling only `pre-commit`.

[Lint before you push!](https://soundcloud.com/lemonsaurusrex/lint-before-you-push)

#### Hooks List:

- `check-toml`: Lints and corrects your TOML files.
- `check-yaml`: Lints and corrects your YAML files.
- `end-of-file-fixer`: Makes sure you always have an empty line at the end of your file.
- `trailing-whitespaces`: Removes whitespaces at the end of each line.
- `python-check-blanket-noqa`: Forbids you from using noqas on large pieces of code.
- `isort`: Runs ISort.
- `flake8`: Runs flake8.

The last two hooks won't ship with their own environment but will rather run shell commands. You will have to modify them if you change your dependency manager.

## How do I use it?

### Creating your Team Repository

One person in the team, preferably the leader, will have to create the repository and add other members as collaborators.

1. In the top right corner of your screen, where **Clone** usually is, you have a **Use this template** button to click.

![](https://docs.github.com/assets/images/help/repository/use-this-template-button.png)

2. Give the repository a name and a description.

![](https://docs.github.com/assets/images/help/repository/create-repository-name.png)

3. Click **Create repository from template**.

4. Click **Settings** in your newly created repository.

![](https://docs.github.com/assets/images/help/repository/repo-actions-settings.png)

5. Select **Manage access**.

<!-- Yes, this is inline html. The source image is too vertical to be displayed with 100% width. -->
<img src="https://docs.github.com/assets/images/help/repository/manage-access-tab.png" style="width: 30%"></img>

6. Click **Invite a collaborator**.

![](https://docs.github.com/assets/images/help/repository/invite-a-collaborator-button.png)

7. Insert the names of each of your teammates, and invite them. Once they have accepted the invitation in their email, they will have write access to the repository.

You are now ready to go! Now sit down, relax, and wait for the kickstart!
Don't forget to swap "Python Discord" in the `LICENSE` file for the name of each of your team members or the name of your team after the start of the jam.

### Using the Default Pip Setup

Our default setup includes a bare requirement file to be used with a [virtual environment](https://docs.python.org/3/library/venv.html).

We recommend this if you never have used any other dependency manager, although if you have, feel free to switch to it. More on that below.

#### Creating the environment
Create a virtual environment in the folder `.venv`.
```shell
$ python -m venv .venv
```

#### Enter the environment
It will change based on your operating system and shell.
```shell
# Linux, Bash
$ source .venv/bin/activate
# Linux, Fish
$ source .venv/bin/activate.fish
# Linux, Csh
$ source .venv/bin/activate.csh
# Linux, PowerShell Core
$ .venv/bin/Activate.ps1
# Windows, cmd.exe
> .venv\Scripts\activate.bat
# Windows, PowerShell
> .venv\Scripts\Activate.ps1
```

#### Installing the Dependencies
Once the environment is created and activated, use this command to install the development dependencies.
```shell
$ pip install -r dev-requirements.txt
```

#### Exiting the environment
Interestingly enough, it is the same for every platform
```shell
$ deactivate
```

Once the environment is activated, all the commands listed previously should work. We highly recommend that you run `pre-commit install` as soon as possible.

## How do I adapt it to my project?

If you wish to use Pipenv or Poetry, you will have to move the dependencies in `dev-requirements.txt` to the development dependencies of your tool.

Additionally, you will have to open `.pre-commit-config.yaml` and `.github/workflows/lint.yaml` and uncomment the right section.

When installing new dependencies, don't forget to [pin them](https://pip.pypa.io/en/stable/user_guide/#pinned-version-numbers) by adding a version tag at the end.
For example, if I wish to install `Click`, a quick look at [PyPI](https://pypi.org/project/click/) tells me that 8.0.1 is the latest version.
I will then add `click ~= 8.0`, without the last number, to my dependency manager.

A code jam project is left unmaintained after the end of the event. If the dependencies aren't pinned, the project will break after the fist major change in an API.

## Final words

Don't forget to replace this README with an actual description of your project! Images are also welcome!

We hope this template will be helpful. Good luck in the jam!
