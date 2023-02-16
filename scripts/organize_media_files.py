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


logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)
USER_DIR = os.path.expanduser("~")
LOGGER_NAME = "organize_media_files"
# Increase max file size
Image.MAX_IMAGE_PIXELS = 1000000000

"""
Usage examples:

cd scripts/

python organize_media_files.py \
--source_dir=~/Pictures/phone \
--output_dir=~/Pictures/laptop \
--media_type=photos \
--copy_or_move=move

python organize_media_files.py \
--source_dir=~/Pictures/tablet \
--output_dir=~/Pictures/laptop \
--media_type=photos \
--copy_or_move=move

python organize_media_files.py \
--source_dir=~/Movies/phone \
--output_dir=~/Movies/laptop \
--media_type=videos \
--copy_or_move=move

python organize_media_files.py \
--source_dir=~/Movies/tablet \
--output_dir=~/Movies/laptop \
--media_type=videos \
--copy_or_move=move
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


def get_image_modified_year_month(file_path: str) -> Tuple[str, str]:
    # 1. Extract date from image exif metadata
    try:
        image_exif_metadata = Image.open(file_path).getexif()
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
    file_name = os.path.basename(file_path)
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
    file_datetime = os.path.getmtime(file_path)

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
    input_pictures_dir: str, file_type: str
) -> Dict[Tuple[str, str], List[str]]:
    logger = logging.getLogger(LOGGER_NAME)

    year_month_mappings = dict()
    picture_locations = list()
    # TODO unique_file_extensions = set()

    if file_type == "photos":
        file_extensions = [
            ".bmp",
            ".gif",
            ".jpeg",
            ".jpg",
            ".pdf",
            ".png",
        ]
    elif file_type == "videos":
        file_extensions = [
            ".3gp",
            ".avi",
            ".bin",
            ".iso",
            ".m4v",
            ".mkv",
            ".mov",
            ".mp4",
            ".mpeg",
            ".mpg",
            ".mts",
            ".wmv",
        ]
    else:
        error_msg = "file_type, %s, must be either 'photos' or 'videos'" % file_type
        logger.error(error_msg)
        raise ValueError(error_msg)

    logger.info(
        "Extracting image file paths and timestamps from %s..." % input_pictures_dir
    )
    logger.info("")

    for path, sub_dirs, files in progressbar.progressbar(
        iterator=os.walk(os.path.expanduser(input_pictures_dir)),
    ):
        for file_name in files:
            file_extension = os.path.splitext(file_name)[1].lower()
            # TODO if file_extension:
            #      unique_file_extensions.add(file_extension)

            # Only expected media files formats
            if file_extension and file_extension in file_extensions:
                file_name_with_path = os.path.join(path, file_name)
                year_and_month = get_image_modified_year_month(
                    file_path=file_name_with_path
                )

                # Keep track of each image file and its respective last modified year and month
                if year_and_month in year_month_mappings:
                    year_month_mappings[year_and_month].append(file_name_with_path)
                else:
                    year_month_mappings[year_and_month] = [file_name_with_path]

                picture_locations.append(file_name_with_path)

    logger.info("Done.")
    logger.info("")

    if len(picture_locations) == 0:
        logger.warning("No eligible media files to process; terminating program.")
        logger.warning("")
        exit(0)

    logger.info("There are %s total files to process" % len(picture_locations))
    logger.info(
        "including %s unique year / month values extracted from these files"
        % len(year_month_mappings)
    )
    logger.info("")

    year_month_mappings = dict(sorted(year_month_mappings.items()))

    # Log a sample of results
    # TODO logger.info("year / month image file mappings:")
    for year_and_month in year_month_mappings:
        pass  # logger.info(year_and_month)

        for file_path in year_month_mappings[year_and_month][:3]:
            pass  # logger.info("    %s" % file_path)

    return year_month_mappings


def save_organized_image_files(
    image_file_mappings: Dict[Tuple[str, str], List[str]],
    destination_base_dir: str,
    copy_or_move_source_files: str,
) -> NoReturn:
    logger = logging.getLogger(LOGGER_NAME)

    transfer_via_move = copy_or_move_source_files == "move"

    if transfer_via_move:
        transfer_language = ["Moving", "moved"]
    else:
        transfer_language = ["Copying", "copied"]

    # Assume supplied destination directory either does not exist or is empty
    # and create if not exists
    if not os.path.exists(destination_base_dir):
        logger.info("Creating new base directory: %s" % destination_base_dir)
        os.makedirs(destination_base_dir)

    # Stage copy of image files organized based on year and month folders
    logger.info(
        "%s all image files organized by year and month under" % transfer_language[0]
    )
    logger.info("%s/..." % destination_base_dir)
    logger.info("")

    copy_counter = 0

    for year, month in progressbar.progressbar(iterator=image_file_mappings):
        # Create subdirectory if not exists
        destination_dir = os.path.join(destination_base_dir, f"{year}/{month}")
        os.makedirs(name=destination_dir, exist_ok=True)

        for source_file_path in image_file_mappings[year, month]:
            source_file_name = os.path.basename(source_file_path)
            destination_file_path = os.path.join(destination_dir, source_file_name)

            if transfer_via_move:
                shutil.move(
                    src=source_file_path,
                    dst=destination_file_path,
                )
            # Copy source files by default
            else:
                shutil.copyfile(
                    src=source_file_path,
                    dst=destination_file_path,
                )

            copy_counter += 1

    logger.info(
        "%s image files successfully %s." % (copy_counter, transfer_language[1])
    )
    logger.info("")


@click.command()
@click.option(
    "--source_dir",
    required=True,
    type=str,
    help="source directory where image files live (separate multiple values with commas",
)
@click.option(
    "--output_dir",
    required=True,
    type=str,
    help="destination base directory to move reorganized image files",
)
@click.option(
    "--media_type",
    required=True,
    type=click.Choice(["photos", "videos", "all_extensions"]),
    help="'photos' or 'videos': defines which file extensions to include",
)
@click.option(
    "--copy_or_move",
    required=False,
    type=click.Choice(["copy", "move"]),
    default="copy",
    help="'photos' or 'videos': defines which file extensions to include",
)
def main(source_dir: str, output_dir: str, media_type: str, copy_or_move):
    # 1. Get list of files nested within base folder
    # 2. Copy all files into base folder
    # 3. Copy all files into new sub-folders based on year + month
    picture_mappings = retrieve_and_map_image_files(
        input_pictures_dir=source_dir, file_type=media_type
    )

    save_organized_image_files(
        image_file_mappings=picture_mappings,
        destination_base_dir=os.path.expanduser(output_dir),
        copy_or_move_source_files=copy_or_move,
    )


if __name__ == "__main__":
    main()
