# How to upload new version to pypi

The best resource about packaging and distribution so far can be found here:
https://packaging.python.org/
- Make sure you have an account on https://pypi.python.org.
I assume the username `richard.bann` here.
- Create (or check) the file `.pypirc` in the home directory.
It should be something like this:
```ini
[distutils]
index-servers=pypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = richard.bann
```
- Create the distribution by running the command below in the directory
where `setup.py` lives:
```sh
python setup.py sdist
```
This will create a `tar.gz` file in the `dist` directory.
- upload to pypi:
```sh
twine upload dist/*
```
