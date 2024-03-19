from setuptools import setup

setup(
    name='gudpy',
    entry_points={
        'console_scripts': [
            'cli = gudpy.cli:cli',
        ],
        'gui_scripts': [
            'gui = gudpy.gui:main',
        ]
    }
)
