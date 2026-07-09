# This file marks the project root for pytest. Its presence puts this folder on
# Python's import path, so tests can do `from services.user_service import app`
# and `from gateway.main import app` — the same module paths uvicorn uses.
#
# It also provides a throwaway SECRET_KEY for the test run. The apps now REQUIRE
# SECRET_KEY from the environment (no hardcoded fallback), so tests must supply
# one before importing them. setdefault means a real env var still wins.
import os

os.environ.setdefault("SECRET_KEY", "test-only-secret-not-for-production")
