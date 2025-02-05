## Seaborn  
### Project URL  
[https://github.com/mwaskom/seaborn](https://github.com/mwaskom/seaborn)

### **1. Clone the Seaborn Repository**
First, clone the repository from GitHub:

```bash
git clone https://github.com/mwaskom/seaborn.git
cd seaborn
```

2. Set Up a Virtual Environment (Windows)
It is recommended to create and activate a virtual environment to manage dependencies:

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install Dependencies
Inside the Seaborn directory, install the required dependencies:

```bash
pip install -U pip wheel setuptools
pip install -e ".[test]"
```
This installs Seaborn in editable mode along with the dependencies needed for testing.

If missing pytest and related modules, try:

```bash
pip install pytest
```
4. Run a Test File Inside Seaborn
To run a specific test file inside Seaborn’s test suite, use the following command:

```bash
python -m pytest tests/test_<filename>.py
```