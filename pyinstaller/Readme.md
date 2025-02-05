## PyInstaller  
### Project URL  
[https://github.com/pyinstaller/pyinstaller](https://github.com/pyinstaller/pyinstaller)

### **1. Clone the PyInstaller Repository**
First, clone the repository from GitHub:

```bash
git clone https://github.com/pyinstaller/pyinstaller.git
cd pyinstaller
```

2. Set Up a Virtual Environment (Windows)
It is recommended to create and activate a virtual environment to manage dependencies:

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install Dependencies
Inside the PyInstaller directory, install the required dependencies:

```bash
pip install -U pip wheel setuptools
pip install -e ".[test]"
```
This installs PyInstaller in editable mode along with the dependencies needed for testing.

If missing pytest, try:

```bash
pip install pytest
```
4. Run a Test File Inside PyInstaller
To run a specific test file inside PyInstaller’s test suite, use the following command:

```bash
python -m pytest tests/unit/test_<filename>.py
```