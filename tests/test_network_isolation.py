"""Regression tests for the default offline test network guard."""

import errno
import socket
from pathlib import Path

import pytest


def test_cache_database_is_scoped_to_project_tmp():
    import core.stock_cache as stock_cache

    project_root = Path(__file__).resolve().parents[1]
    cache_path = Path(stock_cache._CACHE_DB).resolve()
    test_temp_root = (project_root / ".tmp").resolve()
    production_cache_path = (project_root / "cache" / "stock_cache.db").resolve()
    assert cache_path.is_relative_to(test_temp_root)
    assert cache_path != production_cache_path


def test_external_dns_preflight_is_stubbed():
    # An IPv4 literal avoids DNS even if the guard regresses; this must stay local.
    assert socket.gethostbyname("203.0.113.9") == "127.0.0.1"


def test_external_name_resolution_is_blocked():
    # getaddrinfo on an IP literal is local and cannot send a DNS query.
    with pytest.raises(socket.gaierror, match="network mock: external DNS disabled"):
        socket.getaddrinfo("203.0.113.9", 443)


def test_external_socket_connect_is_blocked():
    # UDP connect does not send a packet, so the assertion itself stays offline
    # even if the guard is accidentally removed.
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        with pytest.raises(OSError, match="network mock: external socket connections disabled"):
            sock.connect(("203.0.113.9", 443))


def test_loopback_socket_connect_remains_available():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.connect(("127.0.0.1", 443))
        assert sock.getpeername()[0] == "127.0.0.1"


def test_external_connect_ex_is_blocked():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        assert sock.connect_ex(("203.0.113.9", 443)) == errno.EACCES
