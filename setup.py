from setuptools import setup
import os
from freecad.FormatMigrator.version import __version__

version_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            "freecad", "FormatMigrator", "version.py")
with open(version_path) as fp:
    exec(fp.read())

setup(name='freecad.FormatMigrator',
      version=str(__version__),
      packages=['freecad.FormatMigrator'],
      maintainer="chennes",
      maintainer_email="chennes@freecad.org",
      url="https://github.com/FreeCAD/FormatMigrator",
      license="LGPL-2.1-or-later",
      description="A tool for upconverting and downconverting FreeCAD files between versions",
      install_requires=['defusedxml'],
      include_package_data=True)
