<p align="center">
	<img src="./docs/logo.png" width="200px" alt="logo">
</p>
<h1 align="center">Cron Expression Parser CLI</h1>

<p align="center">
	<img src="https://img.shields.io/github/last-commit/markrofail/cron-expression-parser-cli?style=for-the-badge&logo=git&logoColor=white&color=0080ff" alt="last-commit">
	<img src="https://img.shields.io/github/languages/top/markrofail/cron-expression-parser-cli?style=for-the-badge&color=0080ff" alt="repo-top-language">
	<img src="https://img.shields.io/github/languages/count/markrofail/cron-expression-parser-cli?style=for-the-badge&color=0080ff" alt="repo-language-count">
</p>
<p align="center">
	<img src="https://img.shields.io/badge/Python-3776AB.svg?style=for-the-badge&logo=Python&logoColor=white" alt="Python">
	<img src="https://img.shields.io/badge/Pytest-0A9EDC.svg?style=for-the-badge&logo=Pytest&logoColor=white" alt="Pytest">
</p>

<br>

## 📍 Overview

A simple python cli to expand cron expressions

<p align="center">
	<img src="./docs/demo.gif" alt="demo">
</p>

## 🚀 Getting Started

### 🔖 Prerequisites

**Python**: `version 3.12`

### 📦 Installation

Build the project from source:

1. Clone the cron-expression-parser-cli repository:

```sh
❯ git clone https://github.com/markrofail/cron-expression-parser-cli
```

2. Navigate to the project directory:

```sh
❯ cd cron-expression-parser-cli
```

3. Install the required dependencies:

```sh
❯ pip install -r requirements.txt
```

### 🤖 Usage

To run the project, execute the following command:

```sh
❯ python -m src.main "*/15 0 1,15 * 1-5 /usr/bin/find"
```

### 🧪 Tests

Execute the test suite using the following command:

```sh
❯ pytest
```
