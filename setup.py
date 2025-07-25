"""
Setup configuration for humanmouse package
符合PyPI发布标准的安装配置
"""
from setuptools import setup, find_packages
from pathlib import Path

# 读取README文件
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# 定义依赖
install_requires = [
    "numpy>=1.20.0",
    "pandas>=1.3.0", 
    "scipy>=1.7.0",
    "scikit-learn>=0.24.0",
    "pyautogui>=0.9.50",
    'typing-extensions>=4.0.0;python_version<"3.8"',
]

dev_requires = [
    "pytest>=6.0.0",
    "pytest-cov>=2.0.0",
    "black>=22.0.0",
    "flake8>=4.0.0",
    "mypy>=0.900",
    "build>=0.7.0",
    "twine>=3.0.0",
]

setup(
    name="HumanMoveMouse",
    version="1.0.0",
    author="HumanMoveMouse contributors",
    author_email="",  # Add your email if you want to publish
    description="A human-like mouse movement automation tool based on real trajectory data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Tomotsugu-dev/HumanMoveMouse",
    project_urls={
        "Bug Tracker": "https://github.com/Tomotsugu-dev/HumanMoveMouse/issues",
        "Documentation": "https://github.com/Tomotsugu-dev/HumanMoveMouse/wiki",
        "Source Code": "https://github.com/Tomotsugu-dev/HumanMoveMouse",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "humanmouse": ["models/data/*.pkl"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require={
        "dev": dev_requires,
        "collector": ["pygame>=2.0.0"],
    },
    entry_points={
        "console_scripts": [
            "humanmouse=humanmouse.cli:main",
        ],
    },
    keywords="mouse automation human-like trajectory movement testing ui-automation",
    zip_safe=False,
    include_package_data=True,
)