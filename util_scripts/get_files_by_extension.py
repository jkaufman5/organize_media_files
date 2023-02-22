import os
import click
import logging
from typing import NoReturn


logging.basicConfig(
    format="",
    level=logging.INFO,
)
LOGGER_NAME = "get_files_by_extension"


"""
Usage examples:

cd util_scripts/

python get_files_by_extension.py \
--source_dir=~/Pictures/laptop \
--file_extension=gif
"""


def print_file_names(file_dir: str, file_ext: str) -> NoReturn:
    logger = logging.getLogger(LOGGER_NAME)
    file_locations = list()

    if len(file_ext) == 0:
        raise ValueError("Requested file_extension is empty")

    if not file_ext.startswith("."):
        file_ext = f".{file_ext}"

    for path, sub_dirs, files in os.walk(os.path.expanduser(file_dir)):
        for file_name in files:
            file_extension = os.path.splitext(file_name)[1].lower()

            # Keep track of files with requested file extension (e.g., jpg)
            if file_extension == file_ext:
                file_locations.append(os.path.join(path, file_name))

    logger.info("")
    logger.info("Files with extension, %s:" % file_ext)
    logger.info("------------------------------")

    for file_location in sorted(file_locations):
        logger.info(file_location)

    logger.info("------------------------------")
    logger.info("")


@click.command()
@click.option(
    "--source_dir",
    required=True,
    type=str,
    help="source directory where image files live (separate multiple values with commas",
)
@click.option(
    "--file_extension",
    required=True,
    type=str,
    help="file extension to search for (e.g., jpg)",
)
def main(source_dir: str, file_extension: str):
    print_file_names(file_dir=source_dir, file_ext=file_extension)


if __name__ == "__main__":
    main()
