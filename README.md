# IDA4SIMS LEXIS Dataset Upload

## What is this about

This is a module facilitating cli uploads of datasets to the LEXIS platform using the py4lexis library and custom IDA4SIMS modifications.

## Assumptions and Prerequisites

- **Python**  v.3.11.* installed on the system.
- **Git:** Required for cloning the repository.
- **LEXIS Account:** An active account on the LEXIS platform.
- **Project Access:** Membership and access rights to the `exa4mind_wp4` project on LEXIS. (https://opencode.it4i.eu/exa4mind-private/wp4/adams4sims/-/wikis/processes/acessing-Lexis-project)

## Installation

1.  **Clone the Repository:**

    ```bash
    git clone repo: "git clone https://opencode.it4i.eu/exa4mind-private/wp4/ida4sims-cli.git"
    cd "ida4sims-cli"
    ```

2.  **Create and Activate Virtual Environment:**
    *   **Linux/macOS:**
        ```bash
        python -m venv .venv
        source .venv/bin/activate
        ```
    *   **Windows (Command Prompt/PowerShell):**
        ```bash
        python -m venv .venv
        .venv\Scripts\activate
        ```
    Or Alternative virtual environment manager.
3.  **Install Required Libraries:**
    *(Ensure your virtual environment is active)*
    ```bash
    pip install -r requirements.txt
    ```

## Usage

The main script for uploading datasets is `upload_dataset.py`. It uses subcommands to specify the *type* of data being uploaded.

### Uploading Simulation Data

Use the `simulation` subcommand to upload folders containing simulation results.

**Syntax:**

```bash
python upload_dataset.py simulation [OPTIONS] PATH TITLE
```

For a full list of options for the simulation subcommand, run: 

```bash
python upload_dataset.py simulation --help
```

#### Example:

```bash
python upload_dataset.py simulation /data/sim_run_5 "uuuu-ROC-TIP3P-0.1NaCl" --author-name "Jane Doe"
```


### Logout
**After you have finished your work, it's recommended to clear the stored authentication tokens:**

```bash
python logout.py
```

## Script Functionality and Features

In case of an interruption of the upload process, the script holds the Lexis dataset ID in a temporary file. This allows for resuming the upload process without needing to re-upload the entire dataset.

Lexis token is saved into a keyring to avoid re-authentication for each upload. The script uses the `keyring` library to store the token securely. Please logout after the upload is finished to clear the token from the keyring.

Not all optional metadata are required for the upload, missing information can be added later via a web interface.

## Main contributors
IT4Innovations