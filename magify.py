#! /usr/bin/env python3

#
# magify.py
#
#

#
# Modules
#

import argparse
import logging
import os
import sys

#
# Constants
#

SCRIPT_NAME = 'magify.py'
SCRIPT_VERSION = '0.1.0'
SCRIPT_DATE = '2024-07-26'

#
# Global vars
#

# Parsed command line args
args = None

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
    parser.add_argument('-d', dest='debug', action='store_true',
                        help='Display debug output')

    global args
    args = parser.parse_args()

def display_greeting():
    print(f"{SCRIPT_NAME} {SCRIPT_VERSION} ({SCRIPT_DATE})\n")

#
# Main
#

# Parse args and perform setup

parse_args()
display_greeting()

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
if args.debug:
    logging.getLogger().setLevel(logging.DEBUG)
    logging.info('Debug logging enabled.')

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

    # TODO: remove existing scripts, copy new scripts and base files
    # TODO: create a script version file
    # TODO: description.ext: insert script version and map name
