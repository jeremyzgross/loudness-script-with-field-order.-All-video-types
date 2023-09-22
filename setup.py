from setuptools import setup

APP = ['Loudness_Checker_Script.py']
DATA_FILES = []
OPTIONS = {
    'packages': [],
    'excludes': ['PySide6.QtOpenGL'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
