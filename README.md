# Personal-Content-Feed
Personal Intelligent content feed
# Personal-Content-Feed
**Personal Intelligent Content Feed driven by Local LLM Agents.**

## 🛠 Prerequisites
- **Python 3.13+**
- **uv**: Fast Python package manager

---

## 🚀 Setup & Installation

### 1. Project Initialization
Clone the repository and synchronize the environment. `uv` will automatically create the `.venv` and install all required dependencies from the `uv.lock` file.
```bash
uv sync
```
### 2. Code Quality Setup
Install the pre-commit hooks to ensure all code is automatically formatted and linted before every commit.
```bash
uv run pre-commit install
```
### Run API
```bash
uv run uvicorn main:app --reload
```