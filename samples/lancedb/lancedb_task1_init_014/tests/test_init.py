"""Tests for LanceDB initialization."""

import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import asyncio

def test_async_class_exists():
    """Test AsyncLanceDB class exists."""
    from expected import app
    assert hasattr(app, "AsyncLanceDB")

def test_async_connect():
    """Test async connection works."""
    from expected import app

    async def test():
        adb = app.AsyncLanceDB("./test_async_db")
        await adb.connect()
        return adb

    adb = asyncio.run(test())
    assert adb._db is not None
