import os
from datetime import datetime
from typing import List, Dict, Tuple, NoReturn

USER_DIR = os.path.expanduser("~")


def get_file_modified_year_month(path: str) -> str:
    file_modified_unix_ts = os.path.getmtime(path)
    yr_month = datetime.utcfromtimestamp(file_modified_unix_ts).strftime('%Y_%m')

    return yr_month


def stage_image_files(source_paths: List[str], destination_base_dir: str) -> NoReturn:
    # TODO
    pass


def retrieve_and_map_image_files() -> Tuple[List[str], Dict[Tuple[str, str]: List[str]]]:
    input_pictures_dir = f"{USER_DIR}/IDrive Downloads/JaimesMacBookPro/My Pictures/2010/JAN"  # TODO tmp
    year_month_mappings = dict()
    picture_locations = list()

    for file_nm in os.listdir(input_pictures_dir):
        file_path = os.path.join(input_pictures_dir, file_nm)

        # Only files
        if os.path.isfile(file_path):
            file_extension = os.path.splitext(file_path)[1].lower()

            # Only picture/image files
            if file_extension in [".jpg", ".jpeg"]:
                year_month = get_file_modified_year_month(file_path)

                # Capture file path and the file's year/month
                if year_month in year_month_mappings:
                    year_month_mappings[year_month].append(file_path)
                else:
                    year_month_mappings[year_month] = list(file_path)

                # Also track separately as a flat list for staging and debugging
                picture_locations.append(file_extension)

    print(f"There are {len(year_month_mappings)} unique year months based on file modify timestamps")
    print(f"and {len(picture_locations)} total files to process...")
    print("")

    # TODO testing
    print(f"year / month image file mappings:")
    for year_month in year_month_mappings:
        print(year_month)

        for file_path in year_month:
            print(file_path)

        print("")

    return picture_locations, year_month_mappings


def save_organized_image_files():
    # TODO
    pass


def main():
    # 1. Get list of files nested within base folder
    # 2. Copy all files into base folder
    # 3. Copy all files into new sub-folders based on year + month
    source_picture_locations, picture_mappings = retrieve_and_map_image_files()
    output_pictures_dir = f"{USER_DIR}/Pictures"

    exit(0)

    # TODO stage_image_files(source_paths=source_picture_locations, destination_dir=output_pictures_dir)





    # Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
