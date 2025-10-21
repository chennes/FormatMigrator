# SPDX-License-Identifier: LGPL-2.1-or-later

import os
import sys
import unittest

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "..", "..", "..", ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    loader = unittest.TestLoader()

    suite = loader.discover(start_dir=current_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    sys.exit(0 if result.wasSuccessful() else 1)
