"""
Setup configuration for LiteDesk
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="litedesk",
    version="1.0.0",
    author="LiteDesk Contributors",
    description="A simple peer-to-peer remote desktop application inspired by RustDesk",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/h123456001/litedesk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Desktop Environment :: Remote Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "mss>=9.0.0",
        "Pillow>=10.0.0",
        "pynput>=1.7.6",
        "PyQt5>=5.15.0",
    ],
    entry_points={
        "console_scripts": [
            "litedesk-server=server:main",
            "litedesk-client=client:main",
        ],
    },
)
