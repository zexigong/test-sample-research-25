## http-prompt 
### Project URL  
[https://github.com/httpie/http-prompt](https://github.com/httpie/http-prompt)

### **1. Clone the http-prompt Repository**
First, clone the repository from GitHub:

```bash
git clone https://github.com/httpie/http-prompt.git
cd http-prompt
```

2. Set Up a Virtual Environment (Windows)
It is recommended to create and activate a virtual environment to manage dependencies:

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install Dependencies
Inside the http-prompt directory, install the required dependencies:

```bash
pip install -U pip wheel setuptools
pip install -e ".[dev,test]"
```
This installs http-prompt in editable mode along with the dependencies needed for testing.

If missing pytest and related modules, try:

```bash
pip install pytest
pip install pytest-cov
```
4. Run a Test File Inside http-prompt
To run a specific test file inside http-prompt's test suite, use the following command:

```bash
python -m pytest tests/test_<filename>.py
```