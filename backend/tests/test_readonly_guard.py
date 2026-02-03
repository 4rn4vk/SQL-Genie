import pytest

from app.mcp_server import MCPDatabaseBridge


def test_execute_blocks_non_select():
    bridge = MCPDatabaseBridge("sqlite:///:memory:", "sqlite")
    with pytest.raises(ValueError):
        bridge.execute_read_query("DELETE FROM users")
