# SPDX-License-Identifier: LGPL-2.1-or-later

import importlib.util
import pathlib
import sys
import inspect
from typing import Type, List
from .migrator import Migrator


def find_migrator_subclasses(root: str) -> List[Type[Migrator]]:
    """Find all Migrator subclasses in the given directory and its subdirectories."""
    base_path = pathlib.Path(root).resolve()
    sys.path.insert(0, str(base_path.parent))

    migrators = []

    for py_file in base_path.rglob("*.py"):
        if py_file.name.startswith("__"):
            continue

        module_name = (
            py_file.with_suffix("").relative_to(base_path.parent).as_posix().replace("/", ".")
        )
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            spec = importlib.util.spec_from_file_location(module_name, str(py_file))
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, Migrator) and obj is not Migrator:
                    migrators.append(obj)

    return migrators
