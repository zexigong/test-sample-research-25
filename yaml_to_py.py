import yaml
import os

def convert_yaml_to_python(yaml_file):
    # Extract the filename without extension
    base_name = os.path.splitext(yaml_file)[0]
    output_py_file = f"{base_name}.py"

    # Load YAML file
    with open(yaml_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    # Extract the response and clean it
    python_code = data.get("response", "")
    
    # Remove ```python and trailing ```
    if python_code.startswith("```python"):
        python_code = python_code[len("```python"):].strip()
    if python_code.endswith("```"):
        python_code = python_code[:-3].strip()
    
    # Save as .py file
    with open(output_py_file, "w", encoding="utf-8") as f:
        f.write(python_code)
    
    print(f"Converted to Python file: {output_py_file}")

# Example usage
convert_yaml_to_python("twisted_test_address_response.yaml")
