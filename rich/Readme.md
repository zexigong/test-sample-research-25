## rich
### Project URL
[https://github.com/Textualize/rich](https://github.com/Textualize/rich)

### 1. Clone the pytest Repository
First, clone the rich repository from GitHub:

```bash
git clone https://github.com/Textualize/rich.git
cd rich
```

### 2. Set Up a Virtual Environment (Windows)
Create and activate a virtual environment to manage dependencies.

```bash
python -m venv venv
venv\Scripts\activate
```
### 3. Install Dependencies
Install the required dependencies. Since rich does not provide [dev] or [test] dependencies, install the required testing packages manually:

```bash
pip install -U pip wheel setuptools
pip install -e .
pip install pytest pytest-cov
```
This installs Rich in editable mode along with all necessary dependencies for testing.

### 4. Run a Test File Inside Pytest
Rich uses pytest for testing. To run a specific test file, use:
```bash
python -m pytest tests/test_<filename>.py
```
