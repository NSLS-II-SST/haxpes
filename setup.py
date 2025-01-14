from setuptools import setup, find_packages
from glob import glob

scripts = glob("scripts/*")
scripts = [script for script in scripts if script[-1] != "~"]

with open("requirements.txt") as f:
    requirements = f.read().split()

setup(
    author="Charles Titus",
    author_email="charles.titus@nist.gov",
    install_requires=requirements,
    name="haxpes",
    use_scm_version=True,
    packages=find_packages(),
    scripts=scripts,
)
