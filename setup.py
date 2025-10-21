# SPDX-License-Identifier: LGPL-2.1-or-later

from setuptools import setup
import os
from freecad.fcstdmigrator.version import __version__

version_path = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "freecad", "fcstdmigrator", "version.py"
)
with open(version_path) as fp:
    exec(fp.read())

setup(
    name="freecad.fcstdmigrator",
    version=str(__version__),
    packages=["freecad.fcstdmigrator"],
    maintainer="chennes",
    maintainer_email="chennes@freecad.org",
    url="https://github.com/FreeCAD/FCStdMigrator",
    license="LGPL-2.1-or-later",
    description="A tool for upconverting and downconverting FreeCAD files between versions",
    install_requires=["defusedxml", "packaging"],
    include_package_data=True,
)
