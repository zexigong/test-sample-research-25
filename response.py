import os
import json
import yaml
import datetime
import argparse
from openai import AzureOpenAI

# Azure OpenAI Configuration
endpoint = os.getenv("ENDPOINT_URL", "https://gongz-m82drk07-eastus2.openai.azure.com/")
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o-2024-08-06-ft-62875f3571c54451ada76ed1b79d6a4f-epoch3")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "")

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version="2024-05-01-preview",
)

# Function to find test, source, and dependency files
def find_files(repo_path: str):
    test_source_map = {}

    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)

            if "test_" in os.path.basename(root):  # Detect test files
                test_folder = root
                test_file = file_path

                # Locate corresponding source and dependency files
                source_folder = os.path.join(test_folder, "source_files")
                dependent_folder = os.path.join(test_folder, "dependent_files")

                source_files = (
                    [os.path.join(source_folder, f) for f in os.listdir(source_folder) if f.endswith(".py")]
                    if os.path.exists(source_folder) else []
                )

                dependency_files = (
                    [os.path.join(dependent_folder, f) for f in os.listdir(dependent_folder) if f.endswith(".py")]
                    if os.path.exists(dependent_folder) else ["empty.txt"]
                )

                test_source_map[test_file] = {"sources": source_files, "dependencies": dependency_files}

    return test_source_map

# Function to read file contents
def read_files(file_paths):
    contents = []
    for path in file_paths:
        if path == "empty.txt":
            contents.append("")
        else:
            with open(path, "r", encoding="utf-8") as f:
                contents.append(f.read())
    return contents

# Function to generate a structured prompt
def generate_prompt(repository: str, source_file_contents: list, test_file_path: str, 
                     language: str, framework: str, dependencies_file_names: list, dependencies_file_contents: list):

    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    system_message = "You are an AI agent expert in writing unit tests. Your task is to write unit tests for the given code files of the repository. Make sure the tests can be executed without lint or compile errors."

    source_content = "\n\n".join([f"### Source File Content:\n{content}" for content in source_file_contents])
    dependencies_content = "\n\n".join([f"### Dependency File: {os.path.basename(name)}\n{content}" for name, content in zip(dependencies_file_names, dependencies_file_contents)])

    user_message = f"""### Task Information
Based on the source code, write/rewrite tests to cover the source code.
Repository: {repository}
Test File Path: {test_file_path}
Project Programming Language: {language}
Testing Framework: {framework}
### Source File Content
{source_content}
### Source File Dependency Files Content
{dependencies_content}
Output the complete test file, code only, no explanations.
### Time
Current time: {current_time}
"""

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]
    
    return {"messages": messages}

# Function to call Azure OpenAI model
def call_openai_model(messages):
    completion = client.chat.completions.create(
        model=deployment,
        messages=messages,
        max_tokens=16000,
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        stream=False
    )
    return completion.choices[0].message.content

# Function to save response as a Python file
def save_response_as_python(repo_name, source_file, response):
    source_file_name = os.path.basename(source_file).replace(".py", "")
    response_filename = f"{repo_name}_{source_file_name}_3epochs_test.py"

    # Remove markdown formatting from response
    if response.startswith("```python"):
        response = response[len("```python"):].strip()
    if response.endswith("```"):
        response = response[:-3].strip()
    
    with open(response_filename, "w", encoding="utf-8") as f:
        f.write(response)
    
    print(f"Saved Response as Python File: {response_filename}")

# Function to save the prompt as a YAML file
def save_prompt_as_yaml(repo_name, source_file, prompt_data):
    source_file_name = os.path.basename(source_file).replace(".py", "")
    prompt_filename = f"{repo_name}_{source_file_name}_prompt.yaml"
    
    with open(prompt_filename, "w", encoding="utf-8") as f:
        yaml.dump(prompt_data, f, allow_unicode=True)
    
    print(f"Saved Prompt as YAML File: {prompt_filename}")

# Main execution function
def main():
    parser = argparse.ArgumentParser(description="Generate prompt & get response from Azure OpenAI")
    parser.add_argument("--repository", type=str, required=True, help="Repository name or path")
    parser.add_argument("--repo_path", type=str, required=True, help="Path to the repository directory")
    parser.add_argument("--language", type=str, required=True, help="Programming language")
    parser.add_argument("--framework", type=str, required=True, help="Testing framework")

    args = parser.parse_args()

    # Auto-detect files
    test_source_map = find_files(args.repo_path)

    for test_file, file_mappings in test_source_map.items():
        related_sources = file_mappings["sources"]
        related_dependencies = file_mappings["dependencies"]

        # Read files
        source_file_contents = read_files(related_sources)
        dependencies_file_contents = read_files(related_dependencies)

        # Generate prompt
        prompt_data = generate_prompt(
            repository=args.repository,
            source_file_contents=source_file_contents,
            test_file_path=test_file,
            language=args.language,
            framework=args.framework,
            dependencies_file_names=related_dependencies,
            dependencies_file_contents=dependencies_file_contents
        )

        # Call OpenAI model
        response = call_openai_model(prompt_data["messages"])

        # Save results
        save_response_as_python(args.repository, test_file, response)
        save_prompt_as_yaml(args.repository, test_file, prompt_data)

if __name__ == "__main__":
    main()
