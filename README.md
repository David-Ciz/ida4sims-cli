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

#### Examples:

##### Upload simulation:
```bash
ida-upload-dataset simulation "/data/sim_run_5" "uuuu-ROC-TIP3P-0.1NaCl" --author-name "Jane Doe" --description "Equilibration phase, using TIp3P water model"
```
##### Upload Force Field with multiple frcmod files:
```bash
ida-upload-dataset forcefield "/data/ff_examples/ROC_RNA" "ROC-RNA forcefield" --ff-format AMBER --ff-name "ROC-RNA" --molecule-type R --dat-file parm10.dat --library-file nucleic12.ROC-RNA.lib --leaprc-file leaprc.RNA.ROC --frcmod-file frcmod.ROC-RNA --frcmod-file frcmod.ROC-RNA_const
```
##### Upload Force Field with multiple library files:
```bash
ida-upload-dataset forcefield "/data/ff_examples/ROC_RNA" "ROC-RNA forcefield" --ff-format AMBER --ff-name "ROC-RNA" --molecule-type R --dat-file parm10.dat --library-file nucleic12.ROC-RNA.lib --library-file terminalphos.ROC-RNA.lib --frcmod-file frcmod.ROC-RNA
```
##### Upload Force Field with additional metadata:
```bash
ida-upload-dataset forcefield "/data/ff_examples/ROC_RNA" "ROC-RNA forcefield" --ff-format AMBER --ff-name "ROC-RNA" --molecule-type R --dat-file parm10.dat --library-file nucleic12.ROC-RNA.lib --data-publication-time "2024-06-01" --reference-article-doi "10.1234/example.doi" --author-name "James Bond"
```
##### Upload Experimental data with multiple files:
```bash
ida-upload-dataset experimental "/data/exp_examples/test1" "Experimental_data_test" --technique NMR --sample-description "Set of experimental data used for testing purpose" --temperature "285.65" --3j-coupling exp_jcoupl-sugar --3j-coupling exp_jcoupl-bb --noe exp_noes --noe exp_unoes --noe amb_noe --data-publication-time "2024-06-01" --reference-article-doi "10.1234/example.doi" --author-name "James Bond"
```
##### Upload Experimental data with file contain multiple types:
```bash
ida-upload-dataset experimental "/data/exp_examples/test1" "Experimental_data_test" --technique NMR --sample-description "Set of experimental data used for testing purpose" --temperature "285.65" --3j-coupling exp_jcoupl-sugar_jcoup-bb --noe exp_noes_ambnoe_unoe --data-publication-time "2024-06-01" --reference-article-doi "10.1234/example.doi" --author-name "James Bond"
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


### Listing of Dataset File Hashes
To get a list of all files in a dataset along with their SHA256 hashes, use:

```bash
ida-get-dataset-hashes DATASET_ID
```

You can also compare the dataset hashes with a local directory to verify integrity:
```bash
ida-get-dataset-hashes DATASET_ID --compare-with /path/to/local/data
```
The output will show checking status for each file (MATCH, DIFFERS, MISSING).

Example:
```bash
ida-get-dataset-hashes d56c812e-e30c-11ef-a926-0242ac150006
``` 

### Exporting Hashes
You can export the results to a CSV file for later use:
```bash
ida-get-dataset-hashes DATASET_ID --output-file hashes.csv
```
This will create a CSV file containing columns for `File Path`, `Remote Hash`, and `Status`. If used with `--compare-with`, it will also include `Local Check` and `Local Hash`.


### Listing Datasets
To list all datasets uploaded to Lexis that are visible to the user, use the following command:

```bash
ida-get-all-datasets
```

This command has no parameters.

### Logout
**After you have finished your work, it's recommended to clear the stored authentication tokens:**

```bash
ida-logout
```
## Troubleshooting
### 🔐 Token Authentication Error

If you encounter the following errors:

- `py4lexis.core.session.refresh_token(): AUTH -- b'{"error":"invalid_grant","error_description":"Offline user session not found"}' -- FAILED`
- `Error occurred in py4lexis.core.session.get_access_token(): SESSION -- Access token is not defined! -- FAILED`

you need to uncomment **line 9** in `ida4sims_cli/functions/LexisAuthManager.py`, set `stored_token=False`, and log in again to generate a new token.



## Main contributors
IT4Innovations
