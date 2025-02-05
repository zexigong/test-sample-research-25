## Requests  
### Project URL  
[https://github.com/psf/requests](https://github.com/psf/requests)

### **1. Clone the Requests Repository**
First, clone the repository from GitHub:

```bash
git clone https://github.com/psf/requests.git
cd requests
```

2. Set Up a Virtual Environment (Windows)
It is recommended to create and activate a virtual environment to manage dependencies:

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install Dependencies
Inside the Requests directory, install the required dependencies:

```bash
pip install -U pip wheel setuptools
pip install -e ".[security,socks]"
pip install pytest pytest-httpbin pytest-cov
```
This installs Requests in editable mode along with the dependencies needed for testing.

4. Run a Test File Inside Requests
To run a specific test file inside Requests’s test suite, use the following command:

```bash
python -m pytest tests/test_<filename>.py
```