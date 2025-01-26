import os
import requests
import shutil

# Helper function to download a file from GitHub
def download_file(url, save_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        print(f"Downloaded: {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}: {e}")

# Organize files into a structured directory
def organize_files(project_name, file_info):
    base_dir = os.path.join(os.getcwd(), project_name)

    # Download test files and organize with source files
    test_to_source = file_info.get('test_to_source', {})
    for test_url, source_urls in test_to_source.items():
        test_dir = os.path.join(base_dir, os.path.basename(test_url).replace('.py', ''))
        os.makedirs(test_dir, exist_ok=True)

        # Save the test file
        test_file_name = os.path.basename(test_url)
        test_save_path = os.path.join(test_dir, test_file_name)
        download_file(test_url, test_save_path)

        # Organize source files for the test
        for source_url in source_urls:
            source_dir = os.path.join(test_dir, f"sourcefile_for_{test_file_name.replace('.py', '')}")
            os.makedirs(source_dir, exist_ok=True)

            source_file_name = os.path.basename(source_url)
            source_save_path = os.path.join(source_dir, source_file_name)
            download_file(source_url, source_save_path)

            # Download dependent files for the source file
            dependent_files = file_info.get('source_to_dependent', {}).get(source_url, [])
            if dependent_files:
                dependent_dir = os.path.join(source_dir, f"{source_file_name}_dependent_files")
                os.makedirs(dependent_dir, exist_ok=True)
                for dependent_url in dependent_files:
                    dependent_file_name = os.path.basename(dependent_url)
                    dependent_save_path = os.path.join(dependent_dir, dependent_file_name)
                    download_file(dependent_url, dependent_save_path)

if __name__ == "__main__":
    # Example input: Replace with your filenames and GitHub raw URLs
    project_files = {
        "auto-sklearn": {
            "test_to_source": {
                "https://github.com/automl/auto-sklearn/blob/development/test/test_automl/test_construction.py": [
                    "https://github.com/automl/auto-sklearn/blob/development/autosklearn/util/dask.py",
                    "https://github.com/automl/auto-sklearn/blob/development/autosklearn/util/data.py",
                    "https://github.com/automl/auto-sklearn/blob/development/autosklearn/util/single_thread_client.py",
                ],
            },
            "source_to_dependent": {
                "https://github.com/automl/auto-sklearn/blob/development/autosklearn/util/data.py": [
                    "https://github.com/automl/auto-sklearn/blob/development/autosklearn/evaluation/splitter.py",
                ],
            },
        },
    }

    for project_name, file_info in project_files.items():
        organize_files(project_name, file_info)
