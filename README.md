# FCStd Migrator

A pure Python, XML-based tool for performing migrations of FreeCAD *.FCStd files to different versions of FreeCAD.

## Running the tool

During this early development stage, the tool is not yet packaged as a FreeCAD Addon. To run it you will need to clone this repository and run the `main.py` file from within the freecad/fcstdmigrator directory.

That file takes three arguments:
* `-i`/`--input` `filename`: The input file to migrate (*.FCStd)
* `-o`/`--output` `filename`: The output file to write the migrated file to (*.FCStd)
* `-v`/`--version` `version`: The version of FreeCAD to migrate to

## Adding a migration

To create a new migration, add a new Python file to the `migrations` directory. Inside that file create a class that inherits from `Migrator` and implements its abstract methods and properties (see the `Migrator` class for details).

Migrations in this tool operate purely on XML data, in either the Document.xml or GuiDocument.xml files. Any migrations that need to modify other data (such as BREP files) cannot use this framework.