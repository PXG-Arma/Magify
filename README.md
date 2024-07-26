# Magify

Template generation tool that updates the templates with the latest scripts.

## Usage

Clone or update the following repositories:
- [Templates](https://github.com/PXG-Arma/Templates)
- [Scripts](https://github.com/PXG-Arma/Scripts)
- [Magify](https://github.com/PXG-Arma/Magify)

Open a terminal in the Magify directory. Run Magify and provide it with paths to all the repositories. The following example assumes all the repositories reside in the same directory.
```console
python magify.py -t ../Templates -s ../Scripts -b base

```

`-t` precedes path to the templates repository, `-s` path to the scripts repository, and `-b` path to the directory with base files, like textures and `description.ext`. Base files are currently packaged in the Magify repo.

Magify will use Git to automatically determine the date of the last commit in the scripts repository. If command line use of git is not supported in your environment, you can specify the scripts version manually with `-v`. In this case, Git will not be run.
```console
python magify.py -t ../Templates -s ../Scripts -b base -v my-version
```

For help with script options, run it with the help flag:
```console
python magify.py --help
```
