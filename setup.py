# coding=utf-8

from setuptools import find_packages
from setuptools import setup
from urllib.parse import urljoin

from xkits_command.attribute import __author__
from xkits_command.attribute import __author_email__
from xkits_command.attribute import __description__
from xkits_command.attribute import __project__
from xkits_command.attribute import __urlhome__
from xkits_command.attribute import __version__

__urlcode__ = __urlhome__
__urldocs__ = __urlhome__
__urlbugs__ = urljoin(__urlhome__, "issues")


def all_requirements():
    def read_requirements(path: str):
        with open(path, "r", encoding="utf-8") as rhdl:
            return rhdl.read().splitlines()

    requirements = read_requirements("requirements.txt")
    return requirements


setup(
    name=__project__,
    version=__version__,
    description=__description__,
    url=__urlhome__,
    author=__author__,
    author_email=__author_email__,
    project_urls={"Source Code": __urlcode__,
                  "Bug Tracker": __urlbugs__,
                  "Documentation": __urldocs__},
    packages=find_packages(include=["xkits_command*"], exclude=["xkits_command.unittest"]),
    install_requires=all_requirements())
