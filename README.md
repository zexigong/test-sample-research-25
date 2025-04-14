# Unit Test Data Pipeline & LLM Evaluation – Implementation Overview

This repository documents my semester-long implementation work on multi-language unit test generation using LLMs. I organized and managed four separate GitHub repositories — one for each programming language: **Python**, **Go**, **TypeScript**, and **Java**.

The focus of this work was to build end-to-end pipelines that:
1. Extract and organize real-world code from open-source projects,
2. Generate role-based fine-tuning data in JSONL format,
3. Run and evaluate both base and fine-tuned models.

---

## 📁 Repository Structure Across All Languages

Each of the four repositories shares the following structure and core scripts:

### 🔹 `other_projects/`  
- Contains raw code extracted from real open-source GitHub projects.  
- Extraction done using a custom-built script:  
  - `download_script.py` or `script.py`
- Reformats project code into a consistent three-part structure:
  ```
  test file → source file → source dependencies
  ```

This process involved manually identifying, validating, and cleaning test-source pairs to ensure they are functional and relevant to the unit testing scope.

---

### 🔹 Prompt Formatting for Fine-Tuning  
- Implemented `prompt.py` or `[language]_prompt.py` in each repo  
- These scripts:
  - Format test/source/dependency files into a **role-based prompt template**
  - Output structured **JSONL** files for training and validation

Each repo uses a consistent template schema, with a 60:40 train-validation split for reproducibility. JSONL generation was scripted and parameterized to support multiple experiments efficiently.

---

### 🔹 Inference Scripts (Base vs Fine-Tuned)
- `basemodel.py`:  
  Script to call the **base GPT-4o model** using OpenAI/Azure API and generate tests from prompt JSONL inputs.

- `finetuned_model.py` or similarly named script:  
  Script to call the **fine-tuned GPT-4o model** using Azure endpoint for side-by-side evaluation with the base model.

These scripts support batch processing of prompts, result logging, and formatting for downstream evaluation.

---

### 🔹 Local Evaluation (Windows)
- Each validation repo folder contains a `README.md` specific to its evaluation procedure.
- These include:
  - Environment setup for Windows
  - How to run evaluation scripts step-by-step
  - File organization expectations and test execution process

I designed and tested these pipelines specifically for local execution on my Windows machine, troubleshooting model output formatting, environment set up for each validation project, and test running issues along the way.

---

## 📌 Summary of Contributions

- ✅ Built 4 full repositories for 4 languages from scratch (Python, Go, TS, Java)
- ✅ Implemented GitHub scraping and file restructuring tools
- ✅ Designed and scripted a JSONL generation system for role-based fine-tuning
- ✅ Automated both base and fine-tuned model inference using OpenAI/Azure APIs
- ✅ Developed evaluation workflow for local testing on Windows
- ✅ Maintained clean, consistent structure and tooling across all 4 codebases

---

This README serves as an implementation summary of all technical contributions made during the semester as part of the multi-language unit test generation project.

