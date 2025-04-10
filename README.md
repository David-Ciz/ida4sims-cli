# LEXIS Dataset Upload Script

This script uploads a dataset to the LEXIS platform using the py4lexis library.

## Prerequisites

1.  **Clone the Repository:**

    ```bash
    git clone repo: "git clone https://opencode.it4i.eu/exa4mind-private/wp4/ida4sims-cli.git"
    cd "ida4sims-cli"
    ```

2.  **Install Required Libraries:**

    ```bash
    python -m venv .venv
    ```

    ```bash
    .venv\Scripts\activate
    ```

    py4lexis requires <3.12

    ```bash
    pip install py4lexis --index-url https://opencode.it4i.eu/api/v4/projects/107/packages/pypi/simple
    ```

    Default "access" is "project"

## Assumptions

1.  **LEXIS Account:**

    You need an active LEXIS account with access to the appropriate project.

## Usage

**To upload dataset:**

    ```bash
    python upload_dataset.py "YOUR_DATASET_TITLE" "YOUR_LOCAL_FILE_PATH" --access "YOUR_ACCESS[optional]"
    ```

**To get dataset content:**

    ```bash
    python get_dataset_content.py
    ```

## Script Functionality

The script performs the following actions:

1.  **Token Generation:**

2.  **Session Creation:**

3.  **Dataset Creation:**

4.  **Data Upload:**
