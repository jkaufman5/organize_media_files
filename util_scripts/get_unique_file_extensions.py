import os
import click
import logging
from typing import NoReturn


logging.basicConfig(
    format="",
    level=logging.INFO,
)
LOGGER_NAME = "get_unique_file_extensions"


"""
Usage examples:

cd util_scripts/

python get_unique_file_extensions.py \
--source_dir=~/Pictures/laptop
"""


def print_file_extensions(file_dir: str) -> NoReturn:
    logger = logging.getLogger(LOGGER_NAME)

    file_extensions = set()

    for path, sub_dirs, files in os.walk(os.path.expanduser(file_dir)):
        for file_name in files:
            file_extension = os.path.splitext(file_name)[1].lower()
            if file_extension:
                file_extensions.add(file_extension)

    logger.info("")
    logger.info("File extensions present within %s:" % file_dir)
    logger.info("------------------------------")

    for file_ext in sorted(file_extensions):
        logger.info(file_ext)

    logger.info("------------------------------")
    logger.info("")


@click.command()
@click.option(
    "--source_dir",
    required=True,
    type=str,
    help="source directory where media files live",
)
def main(source_dir: str):
    print_file_extensions(file_dir=source_dir)


if __name__ == "__main__":
    main()
