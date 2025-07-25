# Developer Guide - HumanMouse Project Structure

## Overview

This project has a dual structure to serve different purposes:
1. **PyPI Package**: Minimal, production-ready package for end users
2. **GitHub Repository**: Complete development environment with tools and examples

## Project Structure

```
humanmouse/
├── src/humanmouse/          # Core package (PyPI + GitHub)
│   ├── __init__.py         # Package initialization
│   ├── __version__.py      # Version management
│   ├── cli.py             # Command-line interface
│   ├── controllers/        # Mouse control logic
│   ├── models/            # Trajectory models
│   │   └── data/          # Pre-trained models
│   │       └── mouse_model.pkl
│   └── core/              # Core interfaces and structures
│
├── Development Tools (GitHub only)
│   ├── csv_data_collecter/  # Data collection GUI tools
│   │   ├── Mouse Trajectory Collecter.py
│   │   └── Mouse Trajectory Animation Player.py
│   ├── demos/              # Usage examples
│   ├── mouse_utils/        # Utility scripts
│   └── train_model.py      # Model training script
│
├── Configuration
│   ├── setup.py           # Package setup configuration
│   ├── pyproject.toml     # Modern build configuration
│   ├── MANIFEST.in        # Files to include in source distribution
│   ├── .gitignore         # Git ignore rules
│   └── .pypiignore        # PyPI ignore rules
│
└── Documentation
    ├── README.md          # Main documentation
    ├── DEVELOPER_GUIDE.md # This file
    └── SECURITY.md        # Security guidelines

```

## Publishing Workflow

### For PyPI Users (pip install humanmouse)
Users get:
- Core `humanmouse` package with all functionality
- Pre-trained model for immediate use
- Command-line tools
- Clean, minimal installation

### For GitHub Users (developers/researchers)
Full access to:
- Data collection tools
- Training scripts
- Demo applications
- Development utilities
- Complete source history

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/HumanMoveMouse contributors/humanmouse.git
   cd humanmouse
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install in development mode**:
   ```bash
   pip install -e ".[dev,collector]"
   ```

## Building for PyPI

### Setup PyPI Authentication

1. **Create PyPI API token**:
   - Go to https://pypi.org/manage/account/token/
   - Create a new API token
   - Copy the token (starts with `pypi-`)

2. **Configure authentication** (choose one method):

   **Method 1: Environment Variables (Recommended)**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your token
   # PYPI_TOKEN=pypi-your-actual-token-here
   
   # Use with twine
   export TWINE_USERNAME=__token__
   export TWINE_PASSWORD=$(grep PYPI_TOKEN .env | cut -d '=' -f2)
   ```

   **Method 2: Keyring (More Secure)**
   ```bash
   pip install keyring
   keyring set https://upload.pypi.org/legacy/ __token__
   # Enter your token when prompted
   ```

   **Method 3: .pypirc file**
   ```ini
   # ~/.pypirc (chmod 600 for security)
   [pypi]
   username = __token__
   password = pypi-your-token-here
   ```

### Build and Upload

1. **Build the distribution**:
   ```bash
   python -m build
   ```

2. **Test with TestPyPI** (optional):
   ```bash
   twine upload --repository testpypi dist/*
   ```

3. **Upload to PyPI**:
   ```bash
   twine upload dist/*
   ```

## Key Differences

### PyPI Package
- **Size**: ~50KB (excluding model)
- **Focus**: End-user functionality
- **Dependencies**: Minimal (numpy, scipy, scikit-learn, pyautogui)
- **Use case**: Automation scripts, testing

### GitHub Repository  
- **Size**: Complete development environment
- **Focus**: Development, research, contribution
- **Dependencies**: Includes pygame for data collection
- **Use case**: Training custom models, contributing

## Data Collection and Training

To collect your own data and train models (GitHub only):

1. **Collect trajectories**:
   ```bash
   python csv_data_collecter/Mouse\ Trajectory\ Collecter.py
   ```

2. **Train model**:
   ```bash
   python train_model.py
   ```

3. **Test your model**:
   ```bash
   python demo.py
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure tests pass
5. Submit a pull request

## Important Notes

- **Never commit**: `Pypi_Token.txt`, `.env` files, personal trajectory data
- **Always test**: Both PyPI package build and GitHub functionality
- **Model files**: Default model in `src/humanmouse/models/data/`, custom models in root
- **Documentation**: Update both README files when adding features