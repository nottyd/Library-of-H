import argparse
from pathlib import Path

from nhentaiDBManager.DBWriter import nhentaiLibrary
from nhentaiDownloader.Config import Config
from nhentaiDownloader import Helper

config = Config()

def validate_library_directory(library_directory):
    if Path(library_directory).exists():
        return library_directory
    else:
        raise argparse.ArgumentTypeError("Provided location does not exist.")

parser = argparse.ArgumentParser(description='Create a database with provided nhentai Library. The database file will be created in accordance to config.ini')
parser.add_argument('library_root_directory', type=validate_library_directory, help='Path to nhentai library directory.')

args = parser.parse_args()

def library_to_database():
    nhen_DBW_l = nhentaiLibrary()
    if Path(f'{config.databaselocation}').exists():
        nhen_DBW_l.set_database(config.databaselocation, metadata_location=args.library_root_directory)
    else:
        Helper.log_and_print(error_family='CONFError', error_type='databaselocation_load_error', cont_default=True)
        nhen_DBW_l.set_database(config.default_databaselocation, metadata_location=args.library_root_directory)
    nhen_DBW_l.set_database(database_location=config.databaselocation, metadata_location=args.library_root_directory)


library_to_database()