from typing import Dict

import click
from ida4sims_cli.functions.LexisAuthManager import LexisAuthManager
from ida4sims_cli.functions.create_dataset import create_lexis_dataset
from ida4sims_cli.functions.upload_dataset_content import upload_dataset_content
from ida4sims_cli.functions.delete_dataset_id import delete_saved_dataset_id
from py4lexis.lexis_irods import iRODS
from py4lexis.ddi.datasets import Datasets
from ida4sims_cli.helpers.default_data import DEFAULT_ACCESS
import sys

auth_manager = LexisAuthManager()

def upload_lexis_dataset(title: str, path: str, access: str, metadata: Dict[str, str], dataset_type: str) -> None:
    """
    Core function to handle dataset creation and upload to LEXIS.

    Args:
        title (str): Dataset title.
        path (str): Local file or directory path to upload.
        access (str): Access level for the dataset.
        dataset_type (str): Type of the dataset (e.g., 'simulation', 'forcefield').
        **metadata (dict): Additional metadata specific to the dataset type.
    """
    print(f"--- Starting {dataset_type.capitalize()} Dataset Upload ---")
    print(f"Processing dataset '{title}' from path '{path}'...")
    print(f"Access level: {access}")

    print("\nChecking for refresh token...")
    try:
        session = auth_manager.login()
        if not session:
             print("ERROR: Failed to obtain authentication session. Exiting.", file=sys.stderr)
             sys.exit(1) # Exit if authentication fails

    except Exception as auth_err:
        print(f"ERROR: Authentication failed: {auth_err}", file=sys.stderr)
        sys.exit(1) # Exit if authentication fails

    print("Initializing LEXIS connection...")
    try:
        irods = iRODS(session=session, suppress_print=False)
        datasets = Datasets(session=session, suppress_print=False)
    except Exception as conn_err:
        print(f"ERROR: Failed to initialize iRODS/Datasets connection: {conn_err}", file=sys.stderr)
        sys.exit(1) # Exit if connection fails

    dataset_id = None
    try:
        print("Creating dataset entry...")
        metadata_filtered = {k: v for k, v in metadata.items() if v is not None}
        dataset_id = create_lexis_dataset(irods, title, metadata_filtered) # Note: 'access' is not used by this func currently
        if not dataset_id:
            print("ERROR: Failed to create dataset entry. Dataset ID is missing.", file=sys.stderr)
            sys.exit(1)

        print(f"Created dataset entry with preliminary ID: '{dataset_id}'")
        print("Uploading content to dataset...")

        upload_dataset_content(irods, datasets, path, dataset_id)

        print("Cleaning up temporary data...")
        delete_saved_dataset_id() # Assumes this cleans up temp ID files

        print("\n--- Success ---")
        print(f"Dataset Type: {dataset_type.capitalize()}")
        print(f"Dataset Title: '{title}'")
        print(f"Dataset ID: {dataset_id}")
        print(f"Source Path: '{path}'")
        print("Content uploaded successfully.")

    except Exception as e:
        print(f"\n--- ERROR during Upload/Processing ---", file=sys.stderr)
        if dataset_id:
            print(f"Dataset entry '{dataset_id}' might have been created.", file=sys.stderr)
        else:
            print("Dataset entry creation might have failed.", file=sys.stderr)
        print(f"Attempted to upload from: '{path}'", file=sys.stderr)
        print(f"Error details: {e}", file=sys.stderr)
        print("\nRecommendation: Check the LEXIS platform.", file=sys.stderr)
        if dataset_id:
             print(f"If dataset '{dataset_id}' exists, you may need to manually upload content or delete the dataset.", file=sys.stderr)
        sys.exit(1) # Indicate failure

# --- Click CLI Group ---
@click.group()
def cli():
    """LEXIS Dataset Uploader Tool"""
    pass

def common_options(func):
    func = click.argument('title', type=str)(func)
    func = click.argument('path', type=click.Path(exists=True, file_okay=True, dir_okay=True, readable=True))(func)
    func = click.option(
        '--access',
        default=DEFAULT_ACCESS,
        show_default=True, # Show the default value in help
        help=f'Access level for the dataset (e.g., public, user, project).'
    )(func)
    return func

@cli.command()
@common_options
@click.option('--author-name', type=str, required=False, help='Name of the author of the simulation.')
@click.option('--description', type=str, required=False, help='Description of the simulation.')
@click.option('--stripping-mask', type=str, required=False, help='Stripping mask for the simulation (e.g., ":WAT;20-30").')
@click.option('--restraint_file_path', type=str, required=False, help='Path to the restraint file (e.g., "restraints/restraint_file.txt").')
def simulation(path, title, access, author_name, description, stripping_mask, restraint_file_path):
    """
    Uploads a SIMULATION dataset to LEXIS.

    This command takes simulation output data from a local PATH, gives it a TITLE,
    and uploads it as a dataset. You can provide additional metadata specific
    to simulations using the available options.

    \b
    Arguments:
        PATH: Local file or directory path containing simulation output.
        TITLE: Dataset title (e.g., "MD simulation of protein X").


    \b
    Examples:
        ida-upload_dataset simulation /data/sim_run_5 \\
         "uuuu-ROC-TIP3P-0.1NaCl" --author-name "Jane Doe" --description "Equilibration phase"

        ida-upload_dataset simulation sim_runs "AAAA-strip-SOL" \\
          --stripping-mask ":SOL" --access public --restraint-file-path restraints.dat

    """
    metadata = {
        'dataset_type': 'simulation',
        'author_name': author_name,
        'description': description,
        'stripping_mask': stripping_mask,
        'restraint_file_path': restraint_file_path
    }
    upload_lexis_dataset(title, path, access, metadata, dataset_type='simulation')

@cli.command()
@common_options
@click.option('--ff-type', type=str, required=True, help='Type of the force field (e.g., GROMOS, CHARMM, AMBER).')
@click.option('--atom-types', type=str, help='Comma-separated list of main atom types covered (e.g., C,H,O,N).')
def forcefield(title, path, access, ff_type, atom_types):
    """
    Upload a FORCE FIELD dataset.

    TITLE: Dataset title (e.g., "Custom GROMOS force field for lipids").
    PATH: Local file or directory path containing force field files.
    """
    metadata = {
        'ff_type': ff_type,
        'atom_types': atom_types,
        'dataset_type': 'force_field'
    }
    # Remove None values if atom_types wasn't provided
    metadata = {k: v for k, v in metadata.items() if v is not None}
    upload_lexis_dataset(title, path, access, dataset_type='forcefield', **metadata)

@cli.command()
@common_options
@click.option('--technique', type=str, required=True, help='Experimental technique used (e.g., NMR, XRD, Cryo-EM).')
@click.option('--sample-description', type=str, help='Brief description of the sample.')
def experimental(title, path, access, technique, sample_description):
    """
    Upload an EXPERIMENTAL DATA dataset.

    TITLE: Dataset title (e.g., "NMR spectra of molecule Y").
    PATH: Local file or directory path containing experimental data.
    """
    metadata = {
        'technique': technique,
        'sample_description': sample_description,
        'dataset_type': 'experimental'
    }
    # Remove None values if sample_description wasn't provided
    metadata = {k: v for k, v in metadata.items() if v is not None}
    upload_lexis_dataset(title, path, access, dataset_type='experimental', **metadata)


if __name__ == "__main__":
    # Make sure necessary helper files/modules are accessible
    # (e.g., functions/*, helpers/*)
    # Example check for default data (replace with your actual path logic if needed)
    try:
        _ = DEFAULT_ACCESS
    except NameError:
        print("Error: DEFAULT_ACCESS not defined. Make sure 'helpers/default_data.py' is accessible and defines it.", file=sys.stderr)
        sys.exit(1)
    cli()