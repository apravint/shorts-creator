from setuptools import setup, find_packages

setup(
    name="shorts-creator",
    version="2.1.0",
    description="Universal AI Video & YouTube Shorts Creator (Tamil & English)",
    author="Pravin",
    packages=find_packages(),
    package_data={
        "shorts_creator": ["web_static/*", "web_static/**/*"],
    },
    include_package_data=True,
    install_requires=[
        "edge-tts>=7.0.0",
        "rich>=13.0.0",
        "pillow>=10.0.0",
        "numpy>=1.24.0",
    ],
    extras_require={
        "fallback": ["gTTS>=2.5.0"],
        "ai": ["google-genai>=1.0.0", "fal-client>=0.5.0", "replicate>=1.0.0"],
        "caption": ["faster-whisper>=1.0.0"],
        "mcp": ["mcp>=1.0.0"],
        "dev": ["pytest>=8.0.0", "ruff>=0.3.0"],
    },
    entry_points={
        "console_scripts": [
            "shorts=shorts_creator.cli:main",
            "shorts-creator=shorts_creator.cli:main",
            "shorts-mcp=shorts_creator.mcp_server:main",
        ],
    },
    python_requires=">=3.8",
)
