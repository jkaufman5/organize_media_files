import os
import re
import logging
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
from typing import List, Dict, Tuple, NoReturn

USER_DIR = os.path.expanduser("~")
LOGGER_NAME = "organize_media_files"


def year_and_month_are_valid(y: str, m: str) -> bool:
    year_is_valid = (
        y
        and (isinstance(y, str))
        and (len(y) == 4)
        and int(y)
        and (1980 <= int(y) <= 2099)
    )
    expected_months = [
        "JAN",
        "FEB",
        "MAR",
        "APR",
        "MAY",
        "JUN",
        "JUL",
        "AUG",
        "SEP",
        "OCT",
        "NOV",
        "DEC",
    ]
    month_is_valid = m and (isinstance(m, str)) and (m in expected_months)

    return year_is_valid and month_is_valid


def get_image_modified_year_month(path: str) -> Tuple[str, str]:
    # TODO path = "/Users/jkaufman/Pictures/tablet/_EXTERNAL_/Pictures/jaime navy trumpet 1.jpg"
    # 1. Extract date from image exif metadata
    image_exif_metadata = Image.open(path).getexif()

    image_modified_timestamps = [
        image_exif_metadata.get(tag_id)
        for tag_id in image_exif_metadata
        if TAGS.get(tag_id) == "DateTime"
    ]

    if image_modified_timestamps:
        image_meta_data_date = datetime.strptime(
            image_modified_timestamps[0], "%Y:%m:%d %H:%M:%S"
        )

        if image_meta_data_date:
            year = image_meta_data_date.strftime("%Y")
            month = image_meta_data_date.strftime("%b").upper()

            if year_and_month_are_valid(y=year, m=month):
                return year, month

    # 2. Otherwise, extract date from file name (two expected formats handled)
    file_name = path.split("/")[-1]
    expression = r".*_?((?:19|20)[0-9]{6}).*"
    file_name_string_dates = re.findall(expression, file_name)

    if file_name_string_dates:
        file_name_date = datetime.strptime(file_name_string_dates[0], "%Y%m%d")

        if file_name_date:
            year = file_name_date.strftime("%Y")
            month = file_name_date.strftime("%b").upper()

            if year_and_month_are_valid(y=year, m=month):
                return year, month

    alternative_expression = r".*_?((?:19|20)[0-9]{2}_[0-9]{2}_[0-9]{2}).*"
    file_name_string_dates = re.findall(alternative_expression, file_name)

    if file_name_string_dates:
        file_name_date = datetime.strptime(file_name_string_dates[0], "%Y_%m_%d")

        if file_name_date:
            year = file_name_date.strftime("%Y")
            month = file_name_date.strftime("%b").upper()

            if year_and_month_are_valid(y=year, m=month):
                return year, month

    # 3. Otherwise, extract date from file metadata
    file_datetime = os.path.getmtime(path)

    if file_datetime:
        year = datetime.utcfromtimestamp(file_datetime).strftime("%Y")
        month = datetime.utcfromtimestamp(file_datetime).strftime("%b").upper()

        if year_and_month_are_valid(y=year, m=month):
            return year, month

        # 4. Otherwise, we can fall back on using the current year and month =(
        year = datetime.now().strftime("%Y")
        month = datetime.now().strftime("%b").upper()

        return year, month


def stage_image_files(source_paths: List[str], destination_base_dir: str) -> NoReturn:
    # TODO
    pass


def retrieve_and_map_image_files() -> (
    Tuple[List[str], Dict[Tuple[str, str], List[str]]]
):
    logger = logging.getLogger(LOGGER_NAME)
    input_pictures_dir = f"{USER_DIR}/Pictures/tablet"  # TODO tmp
    year_month_mappings = dict()
    picture_locations = list()

    for path, sub_dirs, files in os.walk(input_pictures_dir):
        for file_name in files:
            # Only image files
            if file_name.lower().endswith((".jpg", ".jpeg", ".gif", ".png")):
                file_name_with_path = os.path.join(path, file_name)
                year_and_month = get_image_modified_year_month(file_name_with_path)

                # Keep track of each image file and its respective last modified year and month
                if year_and_month in year_month_mappings:
                    year_month_mappings[year_and_month].append(file_name_with_path)
                else:
                    year_month_mappings[year_and_month] = [file_name_with_path]

                # # TODO
                picture_locations.append(file_name_with_path)

    logger.info("")
    logger.info(
        "There are %s unique year months based on file modify timestamps"
        % len(year_month_mappings)
    )
    logger.info("and %s total files to process..." % len(picture_locations))
    logger.info("")

    year_month_mappings = dict(sorted(year_month_mappings.items()))

    # Log a sample of results
    logger.info("year / month image file mappings:")
    for year_and_month in year_month_mappings:
        logger.info(year_and_month)

        for file_path in year_month_mappings[year_and_month][:3]:
            logger.info("    %s" % file_path)

    return picture_locations, year_month_mappings


def save_organized_image_files():
    # TODO
    pass


def main():
    # 1. Get list of files nested within base folder
    # 2. Copy all files into base folder
    # 3. Copy all files into new sub-folders based on year + month

    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    source_picture_locations, picture_mappings = retrieve_and_map_image_files()
    output_pictures_dir = f"{USER_DIR}/Pictures"

    exit(0)

    # TODO stage_image_files(source_paths=source_picture_locations, destination_dir=output_pictures_dir)


if __name__ == "__main__":
    main()
