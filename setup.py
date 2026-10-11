from setuptools import setup, find_packages

setup(
    name="shorts-creator",
    version="1.0.0",
    description="Automated AI YouTube Shorts Video Creator (Tamil & English)",
    author="Pravin",
    packages=find_packages(),
    install_requires=[
        "edge-tts>=7.0.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "shorts=shorts_creator.cli:main",
            "shorts-creator=shorts_creator.cli:main",
        ],
    },
    python_requires=">=3.8",
)
