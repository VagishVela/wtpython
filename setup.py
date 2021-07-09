import os
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pytui',
    version='0.0.1',
    entry_points={
    'console_scripts': [
            'pytui = pytui.main:main',
        ],
    },
    author="Perceptive Porcupines",
    license="MIT",
    install_requires=[
        'requests', 'pyyaml', 'aiohttp', 'aiofiles', 'cmd2', 'rich', 'jinja2'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
