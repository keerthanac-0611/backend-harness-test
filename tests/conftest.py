import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Module-level `app = create_app()` must not touch the real data directory during tests.
os.environ.setdefault("CUSTOMER_DB_PATH", os.path.join(tempfile.mkdtemp(), "import.db"))
