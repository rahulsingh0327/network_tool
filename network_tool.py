from server import mcp
import subprocess
import socket
import sys
from typing import Any, Dict


def ping_host(host: str, count: int = 1, timeout: int = 2) -> Dict[str, Any]:
    """
    Ping a host using system ping command.

    Args:
        host: Hostname or IP.
        count: Number of pings.
        timeout: Timeout seconds per ping (platform dependent).

    Returns:
        Dict with success boolean and raw output.

    Notes:
        Uses system 'ping' command, so behavior is platform-specific.
    """
    param = "-n" if sys.platform.startswith("win") else "-c"
    try:
        out = subprocess.check_output(["ping", param, str(count), "-W", str(timeout), host], stderr=subprocess.STDOUT, universal_newlines=True, timeout=timeout*count+5)
        return {"ok": True, "output": out}
    except subprocess.CalledProcessError as e:
        return {"ok": False, "output": e.output}
    except subprocess.TimeoutExpired:
        return {"ok": False, "output": "timeout"}


def dns_lookup(host: str) -> Dict[str, Any]:
    """
    Perform DNS lookup (A records) for a host.

    Args:
        host: Domain name.

    Returns:
        Dict with list of resolved IPs.
    """
    try:
        res = socket.getaddrinfo(host, None)
        ips = sorted({r[4][0] for r in res})
        return {"ips": ips}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def network_tool(action: str, target: str, count: int = 1) -> Dict[str, Any]:
    """
    Network helper supporting 'ping' and 'dns'.

    Args:
        action: 'ping' or 'dns'
        target: Host or IP
        count: ping count

    Returns:
        Dict result depending on action.
    """
    action = action.lower()
    if action == "ping":
        return ping_host(target, count=count)
    if action == "dns":
        return dns_lookup(target)
    raise ValueError("Unsupported network action. Use 'ping' or 'dns'.")
