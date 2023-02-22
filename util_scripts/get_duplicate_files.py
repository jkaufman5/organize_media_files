import os
import click
import logging
import filecmp
from typing import NoReturn


logging.basicConfig(
    format="",
    level=logging.INFO,
)
LOGGER_NAME = "get_files_by_extension"


"""
Usage examples:

cd util_scripts/

python get_duplicate_files.py \
--source_dir=~/Pictures/laptop
"""


def print_duplicate_file_names(file_dir: str) -> NoReturn:
    logger = logging.getLogger(LOGGER_NAME)
    potential_duplicate_files = dict()
    # ###################################
    # sample to illustrate structure:
    # ###################################
    # {
    #     "pic1.jpg": {
    #         "/dupe_pic1a/pic1.jpg": [
    #             "/dupe_pic1b/pic1.jpg",
    #             "/dupe_pic1c/pic1.jpg"
    #         ],
    #         "/dupe_pic2a/pic1.jpg": [
    #             "dupe_pic2b/pic1.jpg"
    #         ]
    #     }
    # }

    for path, sub_dirs, files in os.walk(os.path.expanduser(file_dir)):
        for file_basename in files:
            compare_file_with_path = os.path.join(path, file_basename)
            new_entry_added = False

            # Exclusions
            if not file_basename.startswith(".") and file_basename not in ["Thumbs.db"]:
                # Keep track of potential duplicate files where the file names match
                if file_basename in potential_duplicate_files:
                    for initial_file_with_path in potential_duplicate_files[
                        file_basename
                    ]:
                        # Check if the image files are identical in addition to the file names
                        if filecmp.cmp(
                            f1=initial_file_with_path, f2=compare_file_with_path
                        ):
                            potential_duplicate_files[file_basename][
                                initial_file_with_path
                            ].append(compare_file_with_path)
                            new_entry_added = True
                            break

                # If a duplicate was not found (with matching file name or otherwise), then track the new entry
                if not new_entry_added:
                    potential_duplicate_files[file_basename] = {
                        compare_file_with_path: []
                    }

    duplicate_files = {
        base_file_name: {
            initial_file_with_path: sorted(
                potential_duplicate_files[base_file_name][initial_file_with_path]
            )
        }
        for base_file_name in sorted(potential_duplicate_files)
        for initial_file_with_path in potential_duplicate_files[base_file_name]
        if len(potential_duplicate_files[base_file_name][initial_file_with_path]) > 0
    }

    logger.info("")
    logger.info(
        "There are %s files duplicated within %s" % (len(duplicate_files), file_dir)
    )
    logger.info("------------------------------")

    print(duplicate_files)

    for base_file_name, duplicates in duplicate_files.items():
        logger.info(base_file_name)

        for initial_file, duplicate_files in duplicates.items():
            logger.info("    %s" % initial_file)

            for duplicate_file in duplicate_files:
                logger.info("    %s" % duplicate_file)

            logger.info("------------------------------")

    logger.info("")


@click.command()
@click.option(
    "--source_dir",
    required=True,
    type=str,
    help="source directory where image files live (separate multiple values with commas",
)
def main(source_dir: str):
    print_duplicate_file_names(file_dir=source_dir)


if __name__ == "__main__":
    main()
