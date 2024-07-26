#! /usr/bin/env python3

#
# magify.py
#
# Template generation tool that updates the templates with the latest scripts.
# Run with argument --help to see available options.
#

#
# Modules
#

import argparse
import logging
import os
import shutil
import subprocess
import sys

from distutils.dir_util import copy_tree

#
# Constants
#

SCRIPT_NAME = 'magify.py'
SCRIPT_VERSION = '0.2.0'
SCRIPT_DATE = '2024-07-26'

SCRIPTS_DIR = 'Scripts'
SCRIPTS_VERSION_FILE = 'scripts_version.txt'

#
# Global vars
#

# Parsed command line args
args = None
# Version of the source scripts. Determined either manually or automatically with git.
scripts_last_commit = None

#
# Functions
#

def parse_args():
    """Parses command line args and stores them in a global variable."""
    parser = argparse.ArgumentParser(
        prog=SCRIPT_NAME,
        description='Map template generator, that updates the template with the '
                    'newest scripts.')

    parser.add_argument('-t', dest='templates_path', required=True,
                        metavar='TEMPLATES_PATH',
                        help='Path to the Git repository with map templates')
    parser.add_argument('-s', dest='scripts_path', required=True,
                        metavar='SCRIPTS_PATH',
                        help='Path to the Git repository containing scripts')
    parser.add_argument('-b', dest='base_path', required=True,
                        metavar='BASE_PATH',
                        help='Path to the directory with base files (textures, etc.)')
    parser.add_argument('-v', dest='scripts_version', metavar='SCRIPTS_VERSION',
                        help='Manually specify scripts version, do not use git')
    parser.add_argument('-d', dest='debug', action='store_true',
                        help='Display debug output')

    global args
    args = parser.parse_args()

def display_greeting():
    print(f"{SCRIPT_NAME} {SCRIPT_VERSION} ({SCRIPT_DATE})\n")

def do_filesystem_checks():
    """Performs various filesystem checks to determine, whether the script
    can proceed with its tasks. Exists the script on errors.
    """
    global args

    # Check for existence of directories

    errors = False
    paths = ((args.templates_path, 'templates'),
            (args.scripts_path, 'scripts'),
            (args.base_path, 'base files'))
    for path, name in paths:
        if not os.path.isdir(path):
            logging.critical(f"Directory with {name} does not exist. (Path: '{path}')")
            errors = True
    if errors:
        sys.exit(1)

    # Check for git repos

    paths = ((args.templates_path, 'templates'),
            (args.scripts_path, 'scripts'),)
    for path, name in paths:
        if not os.path.isdir(os.path.join(path, '.git')):
            logging.critical(f"Directory with {name} is not a Git repository.")
            errors = True
    if errors:
        sys.exit(1)

    # Check for the presence of key files and directories

    if not os.path.isdir(os.path.join(args.base_path, 'Textures')):
        logging.critical(f"Base directory lacks 'Textures' subdirectory.")
        errors = True
    if not os.path.isfile(os.path.join(args.base_path, 'description.ext')):
        logging.critical(f"Base directory lacks file 'description.ext'.")
        errors = True

    if not os.path.isfile(os.path.join(args.scripts_path, 'config.cpp')):
        logging.critical(f"Scripts directory lacks file 'config.cpp'.")
        errors = True
    if not os.path.isdir(os.path.join(args.scripts_path, 'Armory')):
        logging.critical(f"Scripts directory lacks 'Armory' subdirectory.")
        errors = True

    if errors:
        sys.exit(1)

def build_template(tpath):
    """Copy new scripts and base files to the template directory.
    The `tpath` argument is the path to the template directory.
    """
    global args
    global scripts_last_commit

    # Remove existing scripts, copy new scripts and base files

    tspath = os.path.join(tpath, SCRIPTS_DIR)
    spath = args.scripts_path.rstrip('/')
    if os.path.exists(tspath):
        logging.debug(f"Removing old scripts directory '{tspath}'.")
        shutil.rmtree(tspath)

    logging.debug(f"Copying '{spath}' to '{tspath}'")
    copy_tree(spath, tspath)

    # Copy base files
    logging.debug(f"Copying base files to '{tpath}'")
    cpfiles = []
    for entry in os.listdir(args.base_path):
        cpfiles.append(entry)
        epath = os.path.join(args.base_path, entry)
        target = os.path.join(tpath, entry)

        if os.path.isdir(epath):
            if os.path.isdir(target):
                shutil.rmtree(target)
            copy_tree(epath, target)
        else:
            if os.path.exists(target):
                os.remove(target)
            shutil.copyfile(epath, target)
    logging.debug('Copied base files/dirs: ' + ', '.join(cpfiles))

def get_scripts_last_commit():
    """Gets the date of the last commit of the Scripts repo (in ISO format)
    by running `git`. Returns the date in YYYY-MM-DD format."""
    global args

    logging.debug(f"Getting last commit date of Git repo '{args.scripts_path}'.")
    res = subprocess.run(['git', 'log', '-1', '--format="%aI"'],
                         stdout=subprocess.PIPE, cwd=args.scripts_path)
    date = res.stdout.decode('utf-8').strip().strip('"')
    logging.debug(f"Result: '{date}'.")

    if len(date) != 25:
        logging.critical(f"Could not get last commit date of '{args.scripts_path}' "
                         "by using git.")
        sys.exit(1)

    date = date[:10]
    logging.debug(f"Extracted date: '{date}'.")

    return date

#
# Main
#

# Parse args and perform setup

parse_args()
display_greeting()

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.WARNING)
if args.debug:
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug('Debug logging enabled.')

do_filesystem_checks()

# Get scripts version

if args.scripts_version:
    logging.debug(f"Using manual scripts version: '{args.scripts_version}'.")
    scripts_last_commit = args.scripts_version
else:
    scripts_last_commit = get_scripts_last_commit()

# Iterate the templates directory and build each template

for template in os.listdir(args.templates_path):
    if template in ['.git', '.gitignore', 'README.md']:
        continue

    tpath = os.path.join(args.templates_path, template)
    if not os.path.isdir(tpath):
        logging.debug(f"Skipping file '{tpath}'.")
        continue
    if not os.path.isfile(os.path.join(tpath, 'mission.sqm')):
        logging.warning(f"Template directory '{template}' lacks file 'mission.sqm'. Skipping.")
        continue

    logging.debug(f"Found a valid template directory: '{template}'.")
    build_template(tpath)
    print(f":: Built template '{template}'.")

# Create scripts version file
vfpath = os.path.join(args.templates_path, SCRIPTS_VERSION_FILE)
logging.debug(f"Writing scripts version file '{vfpath}")
with open(vfpath, 'w') as f:
    f.write('Templates were created with the following scripts version:\n')
    f.write(f"{scripts_last_commit}\n")
print(f":: Wrote scripts version file (version '{scripts_last_commit}')")
