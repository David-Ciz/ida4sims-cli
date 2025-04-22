# IDA4SIMS LEXIS Dataset Upload

## What is this about

This is a module facilitating cli uploads of datasets to the LEXIS platform using the py4lexis library and custom IDA4SIMS modifications.

Features include:
- **Resuming upload:** In case of an interruption of the upload process, the script holds the Lexis dataset ID in a temporary file. This allows for resuming the upload process without needing to re-upload the entire dataset.

- **Improved authentication:** Lexis token is saved to avoid re-authentication for each upload. The script uses the `keyring` library to store the token securely. Please logout after the upload is finished to clear the token from the keyring.

- **Simulation Metadata:** Not all optional metadata are required for the upload, missing information can be added later via a web interface. Keep in mind that only simulations with all metadata filled in can be added to the final IDA database.


## Assumptions and Prerequisites

- **Python:**  v.3.11.* installed on the system.
- **Git:** Required for cloning the repository.
- **LEXIS Account:** An active account on the LEXIS platform.
- **Project Access:** Membership and access rights to the `exa4mind_wp4` project on LEXIS. (follow the instructions here: [wiki-instructions](https://github.com/David-Ciz/ida4sims-cli/wiki/accessing%E2%80%90Lexis%E2%80%90project))

## Installation

1.  **Clone the Repository:**

    ```bash
    git clone repo: "git clone https://github.com/David-Ciz/ida4sims-cli.git"
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

The main script for uploading datasets is `upload_dataset.py` scripted to be utilized by calling  `ida-upload_dataset`. It uses subcommands to specify the *type* of data being uploaded.

### Uploading Simulation Data

Use the `simulation` subcommand to upload folders containing simulation results.

**Syntax:**

```bash
ida-upload-dataset simulation [OPTIONS] PATH TITLE
```

TITLE: Dataset title (e.g., "uuuu-ROC-TIP3P-0.1NaCl").

PATH: Local file or directory path containing simulation output.


For a full list of options for the simulation subcommand, run: 

```bash
ida-upload-dataset simulation --help
```

#### Example:

```bash
ida-upload-dataset simulation /data/sim_run_5 "uuuu-ROC-TIP3P-0.1NaCl" --author-name "Jane Doe" --description "Equilibration phase, using TIp3P water model"
```

### Resuming the upload of Simulation Data

In case of an interruption of the upload process, the script holds the created Lexis dataset ID in a temporary file `dataset_id.txt` created in the folder from where the script was called. 
This allows for resuming the upload process by repeating the same upload command as before. In case of a missing `dataset_id.txt` file, the script will create a new dataset ID and start the upload process from scratch.

#### Example:

```bash
ida-upload-dataset simulation /data/sim_run_5 "uuuu-ROC-TIP3P-0.1NaCl" --author-name "Jane Doe" --description "Equilibration phase, using TIp3P water model"
```

Interruptions happen, The user now has a dataset_id.txt file. The user executes the command again:

```bash
ida-upload-dataset simulation /data/sim_run_5 "uuuu-ROC-TIP3P-0.1NaCl" --author-name "Jane Doe" --description "Equilibration phase, using TIp3P water model"
```

#### Manual creation of dataset_id.txt file
This file can also be created manually and it should contain the dataset ID only. Dataset ID is a string in the format of: `90b95334-1ac2-18f0-b80c-0242ac140003`. The id can be found in the log information of the upload, or can be found in the LEXIS web interface.


### Logout
**After you have finished your work, it's recommended to clear the stored authentication tokens:**

```bash
ida-logout
```


## Main contributors
IT4Innovations
