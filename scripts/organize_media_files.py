import os
import re
import click
import shutil
import logging
import progressbar
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
from typing import List, Dict, Tuple, NoReturn

USER_DIR = os.path.expanduser("~")
LOGGER_NAME = "organize_media_files"
# Increase max file size
Image.MAX_IMAGE_PIXELS = 1000000000

"""
Usage:

cd scripts/
python organize_media_files.py \
--source_dirs=~/Pictures \
--output_dir=~/Pictures_tmp
"""


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
    # 1. Extract date from image exif metadata
    try:
        image_exif_metadata = Image.open(path).getexif()
        image_modified_timestamps = [
            image_exif_metadata.get(tag_id)
            for tag_id in image_exif_metadata
            if TAGS.get(tag_id) == "DateTime"
        ]
    except Exception:
        image_modified_timestamps = None

    if image_modified_timestamps:
        try:
            image_meta_data_date = datetime.strptime(
                image_modified_timestamps[0], "%Y:%m:%d %H:%M:%S"
            )
        except Exception as e:
            image_meta_data_date = None

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
        try:
            file_name_date = datetime.strptime(file_name_string_dates[0], "%Y%m%d")
        # Handle invalid / unexpected date string format
        except Exception:
            file_name_date = None

        if file_name_date:
            year = file_name_date.strftime("%Y")
            month = file_name_date.strftime("%b").upper()

            if year_and_month_are_valid(y=year, m=month):
                return year, month

    alternative_expression = r".*_?((?:19|20)[0-9]{2}_[0-9]{2}_[0-9]{2}).*"
    file_name_string_dates = re.findall(alternative_expression, file_name)

    if file_name_string_dates:
        try:
            file_name_date = datetime.strptime(file_name_string_dates[0], "%Y_%m_%d")
        except Exception:
            file_name_date = None

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


def retrieve_and_map_image_files(
    input_picture_dirs: List[str],
) -> Tuple[List[str], Dict[Tuple[str, str], List[str]]]:
    logger = logging.getLogger(LOGGER_NAME)

    year_month_mappings = dict()
    picture_locations = list()
    # unique_file_extensions = set()

    image_extensions = [
        ".bmp",
        ".gif",
        ".ico",
        ".jpeg",
        ".jpg",
        ".pdf",
        ".png",
    ]

    # progress_widgets = [
    #     ' [', progressbar.Timer(), '] ',
    #     progressbar.Bar(),
    #     ' (', progressbar.ETA(), ') ',
    # ]

    for input_pictures_dir in input_picture_dirs:
        logger.info(
            "Extracting image file paths and timestamps from %s..." % input_pictures_dir
        )

        for path, sub_dirs, files in progressbar.progressbar(
            iterator=os.walk(os.path.expanduser(input_pictures_dir)),
            # TODO widgets=progress_widgets
        ):
            for file_name in files:
                file_extension = os.path.splitext(file_name)[1].lower()
                # if file_extension:
                #     unique_file_extensions.add(file_extension)

                # Only image files
                if file_extension and file_extension in image_extensions:
                    file_name_with_path = os.path.join(path, file_name)

                    # TODO year_and_month = get_image_modified_year_month(file_name_with_path)
                    #  # Keep track of each image file and its respective last modified year and month
                    #  if year_and_month in year_month_mappings:
                    #      year_month_mappings[year_and_month].append(file_name_with_path)
                    #  else:
                    #      year_month_mappings[year_and_month] = [file_name_with_path]

                    # TODO
                    picture_locations.append(file_name_with_path)

        logger.info("Done.")

    logger.info("")
    logger.info(
        "There are %s unique year months based on file modify timestamps"
        % len(year_month_mappings)
    )
    logger.info("and %s total files to process." % len(picture_locations))
    logger.info("")

    year_month_mappings = dict(sorted(year_month_mappings.items()))

    # Log a sample of results
    # TODO logger.info("year / month image file mappings:")
    for year_and_month in year_month_mappings:
        pass  # logger.info(year_and_month)

        for file_path in year_month_mappings[year_and_month][:3]:
            pass  # logger.info("    %s" % file_path)

    return picture_locations, year_month_mappings


def stage_image_files(source_paths: List[str], destination_base_dir: str) -> NoReturn:
    logger = logging.getLogger(LOGGER_NAME)
    destination_base_dir = os.path.expanduser(destination_base_dir)

    # Assume supplied destination directory either does not exist or is empty
    # and create if not exists
    if os.path.exists(destination_base_dir):
        if len(os.listdir(destination_base_dir)) > 0:
            error_msg = (
                "The directory, %s, is not empty; please clean it up or provide a different one."
                % destination_base_dir
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
    else:
        os.makedirs(destination_base_dir)

    # Stage copy of files
    logger.info("Staging a copy of all image files to %s..." % destination_base_dir)

    for source_path in progressbar.progressbar(iterator=source_paths):
        shutil.copy(
            src=source_path,
            dst=destination_base_dir,
        )

    logger.info("%s image files successfully copied." % len(source_paths))


def save_organized_image_files():
    # TODO
    pass


@click.command()
@click.option(
    "--source_dirs",
    help="source directories where image files live (separate multiple values with commas",
)
@click.option(
    "--output_dir", help="destination base directory to move reorganized image files"
)
def main(source_dirs: str, output_dir: str):
    # 1. Get list of files nested within base folder
    # 2. Copy all files into base folder
    # 3. Copy all files into new sub-folders based on year + month
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    source_dir_list = source_dirs.replace(" ", "").split(",")

    source_picture_locations, picture_mappings = retrieve_and_map_image_files(
        input_picture_dirs=source_dir_list
    )
    stage_image_files(
        source_paths=source_picture_locations, destination_base_dir=output_dir
    )

    # TODO function call to move files based on year and month


if __name__ == "__main__":
    main()
