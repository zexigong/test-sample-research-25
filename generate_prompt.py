import json
import datetime
import argparse


def generate_messages(repository: str,
                      source_file_paths: list,
                      test_file_path: str,
                      language: str,
                      framework: str,
                      source_file_contents: list,
                      dependencies_file_contents: list,
                      test_example_content: str) -> dict:
    """
    Generate a JSON object in conversation format for fine-tuning.
    The assistant message is set to the test example content.
    """
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    system_message = (
        "You are an AI agent expert in writing unit tests. "
        "Your task is to write unit tests for the given code file of the repo. "
    )
    
    source_content = "\n\n".join(
        [f"### Source File: {path}\n{content}" for path, content in zip(source_file_paths, source_file_contents)]
    )

    # Combine multiple dependencies into a single section
    dependencies_content = "\n\n".join(
        [f"### Dependency File: {path}\n{content}" for path, content in zip(source_file_paths, dependencies_file_contents)]
    )

    user_message = (
        "### Task Information\n"
        "Based on the source code, write/rewrite tests to cover the source code.\n"
        "Make sure the tests can be executed without lint, or compile errors.\n"
        f"Repository: {repository}\n"
        f"Source File Path: {source_file_paths}\n"
        f"Test File Path: {test_file_path}\n"
        f"Project Programming Language: {language}\n"
        f"Testing Framework: {framework}\n"
        "### Source File Content\n"
        f"{source_content}\n"
        "### Source File Dependency Files Content\n"
        f"{dependencies_content}\n"
        "Output the complete test file, code only, no explanations. For example:\n"
        f"```{language}\n<complete test code>\n```\n"
        "### Time\n"
        f"Current time: {current_time}"
    )
    
    # Set the assistant message to the test example content.
    assistant_message = f"```python\n{test_example_content}\n```"

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": assistant_message}
    ]
    return {"messages": messages}


def main():
    parser = argparse.ArgumentParser(
        description="Generate a fine-tuning JSONL document in conversation format"
    )
    parser.add_argument("--repository", type=str, required=True, help="Repository name or URL")
    parser.add_argument("--source_file", nargs="+", required=True, help="Path to the source file")
    parser.add_argument("--test_file", type=str, required=True, help="Path to the test file")
    parser.add_argument("--language", type=str, required=True, help="Programming language")
    parser.add_argument("--framework", type=str, required=True, help="Testing framework")
    parser.add_argument("--source_file_content", nargs="+", required=True,
                        help="Path to file containing the source file content")
    parser.add_argument("--dependencies_file_content", nargs="+", required=True,
                        help="Path to file containing the dependency file content")
    parser.add_argument("--test_example_content", type=str, required=True,
                        help="Path to file containing test example references")
    parser.add_argument("--output", type=str, default="fine_tuning.jsonl", help="Output JSONL file")

    args = parser.parse_args()

    # Read multiple source files
    source_file_contents = [open(path, "r", encoding="utf-8").read() for path in args.source_file_content]

    # Read multiple dependency files
    dependencies_file_contents = [open(path, "r", encoding="utf-8").read() for path in args.dependencies_file_content]

    # Read the test example file
    with open(args.test_example_content, "r", encoding="utf-8") as te:
        test_example_content = te.read()

    conversation = generate_messages(
        repository=args.repository,
        source_file_paths=args.source_file,
        test_file_path=args.test_file,
        language=args.language,
        framework=args.framework,
        source_file_contents=source_file_contents,
        dependencies_file_contents=dependencies_file_contents,
        test_example_content=test_example_content
    )

    # Append the new conversation as a new line in the output JSONL file
    with open(args.output, "a", encoding="utf-8") as out_file:
        out_file.write(json.dumps(conversation) + "\n")

    # args = parser.parse_args()

    # with open(args.source_file_content, "r", encoding="utf-8") as sf:
    #     source_file_content = sf.read()
    # with open(args.dependencies_file_content, "r", encoding="utf-8") as df:
    #     dependencies_file_content = df.read()
    # with open(args.test_example_content, "r", encoding="utf-8") as te:
    #     test_example_content = te.read()

    # conversation = generate_messages(
    #     repository=args.repository,
    #     source_file_path=args.source_file,
    #     test_file_path=args.test_file,
    #     language=args.language,
    #     framework=args.framework,
    #     source_file_content=source_file_content,
    #     dependencies_file_content=dependencies_file_content,
    #     test_example_content=test_example_content
    # )

    # # Append the new conversation as a new line in the output JSONL file
    # with open(args.output, "a", encoding="utf-8") as out_file:
    #     out_file.write(json.dumps(conversation) + "\n")


if __name__ == "__main__":
    main()
