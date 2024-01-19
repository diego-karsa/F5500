from datetime import datetime
from io import BytesIO
import requests
import zipfile
import os
import pandas as pd

# Download the zip file from the specified URL and return it as a BytesIO object.
def _download_5500(schedule, year, modality):
    # Construct the download URL based on the provided arguments.
    url = "https://askebsa.dol.gov/FOIA%20Files/" + year + "/" + modality + "/F_" + schedule + "_" + year + "_" + modality + ".zip"
    # Print a message telling the user that the download is starting.
    print(f"Downloading '{schedule}_{year}_{modality}'...")
    # Download the zip file from the URL.
    response = requests.get(url)
    # If the response status code is not 200, raise an HTTPError.
    response.raise_for_status()
    # Print a green colored message telling the user that the download is complete.
    print(f"\033[32mDownload complete.\033[0m")
    # Buffer the response content in memory.
    return BytesIO(response.content)

# Save the content of the response to the specified file path.
def _save_zip(new_zip, path):
    with open(path, 'wb') as output_file:
        output_file.write(new_zip.getvalue())

# Find and check if zip file contain one expected CSV.
def _get_csv_name(zip_file):
    # Find the CSV file name within the zip archive.
    csv_file_name = [name for name in zip_file.namelist() if name.endswith('.csv')]
    # If no CSV file found, print a message and return None.
    if not csv_file_name:
        raise ValueError("\033[31mNo .csv file found in the zip archive.\033[0m")
    # If multiple CSV files found, print a message and return None.
    if len(csv_file_name) > 1:
        raise ValueError("\033[31mMultiple .csv files found in the zip archive.\033[0m")
    return csv_file_name[0]

# Get the modification date of the CSV file within the zip archive.
def _mod_date(path):
    with zipfile.ZipFile(path) as zip_file:
        # Find the CSV file name within the zip archive.
        csv_file_name = _get_csv_name(zip_file)
        # Get the modification date from the zip file and format it as 'YYYY-MM-DD'.
        csv_info = zip_file.getinfo(csv_file_name)
    mod_date = datetime(*csv_info.date_time).strftime("%Y-%m-%d")
    return mod_date

def clean(archive = 'Datasets'):
    # Before running, ask confirmation from the user.
    confirmation = input(f"""This will delete all .zip files in the folder that are not the most recent version of the same file.\n Proceed? (Y/n) """)
    # If the user does not confirm, stop the function.
    if confirmation != 'y':
        print("Operation cancelled.")
        return None
    # For every .zip file in 'Datasets' subfolders, if the same .zip file exists in another subfolder, only keep the one in the folder named after the most recent date (date is in format Y%-m%-d%):
    # Get the list of all subfolders in 'Datasets'.
    subfolders = [f.path for f in os.scandir(archive) if f.is_dir()]
    # For every subfolder:
    for subfolder in subfolders:
        # Get the list of all .zip files in the subfolder.
        zip_files = [f.path for f in os.scandir(subfolder) if f.is_file() and f.name.endswith('.zip')]
        # For every .zip file in the subfolder:
        for zip_file in zip_files:
            # Get the list of all subfolders that are not the current subfolder.
            other_subfolders = [f.path for f in os.scandir(archive) if f.is_dir() and f.path != subfolder]
            # For every other subfolder:
            for other_subfolder in other_subfolders:
                # Get the list of all .zip files in the other subfolder.
                other_zip_files = [f.path for f in os.scandir(other_subfolder) if f.is_file() and f.name.endswith('.zip')]
                # For every .zip file in the other subfolder:
                for other_zip_file in other_zip_files:
                    # If the .zip file in the other subfolder has the same name as the .zip file in the current subfolder:
                    if other_zip_file.split('\\')[-1] == zip_file.split('\\')[-1]:
                        # Get the modification date of the .zip file in the current subfolder.
                        zip_file_mod_date = datetime.strptime(subfolder.split('\\')[-1], "%Y-%m-%d")
                        # Get the modification date of the .zip file in the other subfolder.
                        other_zip_file_mod_date = datetime.strptime(other_subfolder.split('\\')[-1], "%Y-%m-%d")
                        # If the .zip file in the current subfolder is older than the .zip file in the other subfolder:
                        if zip_file_mod_date < other_zip_file_mod_date:
                            # Delete the .zip file in the current subfolder.
                            os.remove(zip_file)
                        # If the .zip file in the current subfolder is more recent than the .zip file in the other subfolder:
                        else:
                            # Delete the .zip file in the other subfolder.
                            os.remove(other_zip_file)
    #Lastly, if any subfolder in the 'Datasets' folder is now empty, delete it.
    for subfolder in subfolders:
        if not os.listdir(subfolder):
            os.rmdir(subfolder)

def download(schedule, year, modality, overwrite=False, archive = 'Datasets'): 
    try:
        # If 'Datasets' folder does not exist, create it.
        if not os.path.exists(archive):
            os.makedirs(archive)
        # Download the zip file and get the modification date.
        new_zip = _download_5500(schedule, year, modality)
        # Get and print the modification date of the downloaded zip file.
        mod_date = _mod_date(new_zip)
        print(f"    Date of modification: {mod_date}")
        # Create the folder path and the zip file path.
        folder_path = os.path.join(archive, mod_date)
        zip_file_path = os.path.join(folder_path, f"{schedule}_{year}_{modality}.zip")
        # If folder does not exist, create it.
        if not os.path.exists(folder_path):
            print(f"    Creating new folder...")
            os.makedirs(folder_path)
        # If zip file does not exist, save the downloaded zip file to the folder.
        if not os.path.exists(zip_file_path):
            _save_zip(new_zip, zip_file_path)
            return None
        # If the folder and zip file already exists:
        if overwrite is True:
                print(f"    File already exists in folder. Overwriting...")
                _save_zip(new_zip, zip_file_path)
                return None
        if overwrite is False:
                print(f"    File already exists in folder. No changes made.")
                return None
    # Handle any exceptions that may occur during the execution of the function.
    except Exception as e:
        print(f"Error: {e}")
        return None

def _latest_mod_date(schedule, year, modality, archive = 'Datasets'):
    # for a given .zip named after "'schedule'_'year'_'modality'.zip"
    zip_name = f"{schedule}_{year}_{modality}.zip"
    # Get the list of all subfolders in 'Datasets'.
    subfolders = [f.path for f in os.scandir(archive) if f.is_dir()]
    # The paths of object subfolder end in a string with format "%Y-%m-%d", I want to order them by that date from most recent to oldest.
    # I use a lambda function to get the date from the path and then sort the subfolders by that date.
    subfolders = sorted(subfolders, key=lambda x: datetime.strptime(x.split('\\')[-1], "%Y-%m-%d"), reverse=True)
    # Now search in the subfolders for the zip file until the first hit.
    for subfolder in subfolders:
        file_path = os.path.join(subfolder, zip_name)
        if os.path.isfile(file_path):
            return subfolder.split('\\')[-1]
        raise ValueError(f"File not found in archive.")

def read(schedule, year, modality, mod_date = "Latest", archive = 'Datasets'):
    # if mod_date is different to latest or if it does not parse as a date in format Y%-m%-d%:
    try:
        datetime.strptime(mod_date, "%Y-%m-%d")
    except ValueError:
        parse_error = True
        
    if mod_date != "Latest" and parse_error is True:
        raise ValueError("\033[31m'mod_date' must be either 'Latest' or a string in format Y%-m%-d%\033[0m")
    
    if mod_date == "Latest":
        mod_date_x = _latest_mod_date(schedule, year, modality, archive)
    
    zip_name = f"{schedule}_{year}_{modality}.zip"
    path = os.path.join(archive, mod_date_x, zip_name)
    
    with zipfile.ZipFile(path) as zip_file:
        csv_file_name = _get_csv_name(zip_file)
        with zip_file.open(csv_file_name, 'r') as csv_file:
            df = pd.read_csv(csv_file)
            
    return df 