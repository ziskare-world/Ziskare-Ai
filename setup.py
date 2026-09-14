from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ziskare-ai",
    version="1.0.0",
    author="Ziskare World",
    author_email="contact@ziskare.com",
    description="Universal, 100% offline, GPU-accelerated local intelligence engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ziskare-world/Ziskare-Ai",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "torch",
        "transformers",
        "accelerate"
    ],
    entry_points={
        "console_scripts": [
            "ziskare-ai=ziskare_ai.cli:main",
            "ziskare=ziskare_ai.cli:main",
        ],
    },
)
