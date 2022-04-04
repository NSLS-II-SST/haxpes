from setuptools import setup, find_packages
from glob import glob

scripts = glob("scripts/*")
scripts = [script for script in scripts if script[-1] != '~']

setup(
    author="Charles Titus",
    author_email="charles.titus@nist.gov",
    install_requires=["bluesky", "ophyd", "sst_base", "sst_funcs"],
    name="haxpes",
    use_scm_version=True,
    packages=find_packages(),
    scripts=scripts
)
