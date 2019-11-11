#!/usr/bin/env python

"""
Compares content of two given directories and copy missing files to a third
given directory.

authors:
    Mattia Martinello - mattia@mattiamartinello.com
"""

import argparse
import logging
import os
import re
import shutil

_VERSION = "1.0"
_VERSION_DESCR = "Directory comparison."


class Compare:
    def __init__(self):
        # Command line parser
        parser = argparse.ArgumentParser(
            description="Directory comparison"
        )
        self.add_arguments(parser)

        # Read the command line
        args = parser.parse_args()

        # Manage arguments
        self._manage_arguments(args)

    def add_arguments(self, parser):
        parser.add_argument(
            '-V', '--version',
            action='version',
            version = "%(prog)s v{} - {}".format(_VERSION, _VERSION_DESCR)
        )
        parser.add_argument(
            'first_dir',
            type=str,
            default=None,
            help="The first directory to be compared"
        )
        parser.add_argument(
            'second_dir',
            type=str,
            default=None,
            help="The second dir to be compared"
        )
        parser.add_argument(
            '--copy-dir',
            type=str,
            default=None,
            dest='copy_dir',
            help="The directory in which missing files needs to be copied"
        )
        parser.add_argument(
            '--copy',
            default=False,
            action="store_true",
            dest='copy',
            help="Copy missing file to copy-dir (instead make a dry run)"
        )
        parser.add_argument(
            '--preserve-tree',
            default=False,
            dest='preserve_tree',
            action="store_true",
            help="Preserve the original tree of directories during copy"
        )
        parser.add_argument(
            '--debug',
            action="store_true",
            help="Print debugging info to console"
        )

    def _manage_arguments(self, args):
        # Enable debug
        if getattr(args, "debug", False):
            logging.basicConfig(level=logging.DEBUG)

        # First dir
        self.first_dir = getattr(args, 'first_dir', None)

        # Second dir
        self.second_dir = getattr(args, 'second_dir', None)

        # Copy dir
        self.copy_dir = getattr(args, 'copy_dir', None)
        self.preserve_tree = getattr(args, 'preserve_tree', False)
        self.copy = getattr(args, 'copy', False)

        # Debug all given arguments
        logging.debug("Given arguments: " + repr(args.__dict__))

    def handle(self):
        missing_files = self._get_missing_files(self.first_dir,
            self.second_dir)
        
        created_dirs = []
        for current_file in missing_files:
            print("Missing file: '{}".format(current_file))

            # If copy-dir is given, copy missing files
            if self.copy_dir:
                src_file = os.path.join(self.first_dir, current_file)
                dst_dir_name = os.path.dirname(current_file)
                dst_dir = os.path.join(self.second_dir, dst_dir_name)
                dst_file = os.path.join(self.second_dir, current_file)

                if self.copy:
                    # Create destination dir if does not exist
                    if not os.path.exists(dst_dir): 
                            msg = "Creating directory '{}' ...".format(dst_dir)
                            print(msg)
                            os.makedirs(dst_dir, exist_ok=True)
                    
                    msg = "Copying file '{}' to '{}' ..."
                    msg = msg.format(src_file, dst_file)
                    print(msg)
                    shutil.copyfile(src_file, dst_file)
                else:
                    # Create destination dir if does not exist
                    if (not os.path.exists(dst_dir)
                        and (dst_dir not in created_dirs)):
                        
                            msg = "Creating directory '{}' ...".format(dst_dir)
                            print(msg)
                            created_dirs.append(dst_dir)

                    msg = "Copying file '{}' to '{}' ..."
                    msg = msg.format(src_file, dst_file)
                    print(msg)
                print()

    def _list_files(self, dir_path):
        files_list = []

        for path, subdirs, files in os.walk(dir_path):
            for name in files:
                file_path = os.path.join(path, name)
                logging.debug("File '{}' discovered".format(file_path))
                files_list.append(file_path)

        return files_list

    def _file_exists(self, dir_path, file_path):
        full_path = os.path.join(dir_path, file_path)

        if os.path.exists(full_path):
            return True
        else:
            return False

    def _get_missing_files(self, first_dir, second_dir):
        first_dir_files = self._list_files(self.first_dir)
        missing_files = []

        regex_string = "^{}/(.+)$".format(first_dir)
        regex = re.compile(regex_string)   

        for file in first_dir_files:
            matches = re.findall(regex, file)
            relative_path = matches[0]

            logging.debug("File '{}', relative path '{}'".format(
                file, relative_path))

            if not self._file_exists(second_dir, relative_path):
                missing_files.append(relative_path)

        return missing_files


# Main
if __name__ == "__main__":
    # run the procedure and get results
    main = Compare()
    main.handle()
