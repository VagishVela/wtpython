# Poetry doesn't yet support Python 3.10
FROM python:3.9.7

# Environment variables
ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VIRTUALENVS_CREATE=false \
  PATH="~/.local/bin:$PATH"

# Copy all project files 
COPY . .

# Install poetry and dependencies
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python - && ~/.local/bin/poetry install --no-ansi --no-interaction

# Install pre-commit
RUN pre-commit install