#!/usr/bin/env python3
"""
Network File Inspector

Outputs metadata about network-connected files using `lsof`.
Supports macOS and Ubuntu systems.

Features:
- Extract remote IPs from open network file descriptors
- Resolve hostnames
- Optional geolocation lookup
- JSON output support
"""

import argparse
import json
import re
import socket
import subprocess
from dataclasses import dataclass, asdict
from typing import List, Optional


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclass
class IP_METADATA:
    """
    Represents metadata associated with a network IP connection.
    """
    ip: str
    hostname: Optional[str] = None
    port: Optional[int] = None
    protocol: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    org: Optional[str] = None


@dataclass
class INPUT_ARGS:
    """
    Stores parsed command-line arguments.
    """
    geo: bool
    output: Optional[str]


# ---------------------------------------------------------------------------
# Argument Parsing
# ---------------------------------------------------------------------------

def args_parsing() -> INPUT_ARGS:
    """
    Parse command-line arguments.

    Returns:
        INPUT_ARGS: Parsed arguments encapsulated in a dataclass.
    """
    parser = argparse.ArgumentParser(
        description="Analyze network-connected open files using lsof"
    )

    parser.add_argument(
        "--geo",
        action="store_true",
        help="Enable IP geolocation lookup (requires internet access)"
    )

    parser.add_argument(
        "--output",
        type=str,
        help="Path to output JSON file"
    )

    args = parser.parse_args()

    return INPUT_ARGS(
        geo=args.geo,
        output=args.output
    )


# ---------------------------------------------------------------------------
# Collect Open File IPs
# ---------------------------------------------------------------------------

def collect_open_file_ips() -> List[str]:
    """
    Execute `lsof` to retrieve open network connections.

    Returns:
        List[str]: Raw output lines from lsof (excluding header).
    """
    try:
        result = subprocess.run(
            ["lsof", "-nP", "-i"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as exc:
        print(f"[ERROR] Failed to run lsof: {exc}")
        return []

    # Skip header line
    lines = result.stdout.splitlines()[1:]
    return lines


# ---------------------------------------------------------------------------
# IP Address Identification
# ---------------------------------------------------------------------------

def ip_address_identification(lines: List[str]) -> List[IP_METADATA]:
    """
    Extract IP addresses, ports, and protocol from lsof output.

    Args:
        lines (List[str]): Raw lsof output lines.

    Returns:
        List[IP_METADATA]: Extracted IP metadata objects.
    """
    ip_meta_list: List[IP_METADATA] = []

    # Regex to match TCP/UDP connections with remote endpoints
    pattern = re.compile(r"(TCP|UDP)\s+([\d\.:]+)->([\d\.:]+)")

    for line in lines:
        match = pattern.search(line)
        if not match:
            # Skip entries without a remote endpoint (e.g., LISTEN)
            continue

        protocol = match.group(1)
        remote = match.group(3)

        # Attempt to split IP and port
        try:
            ip, port_str = remote.rsplit(":", 1)
            port = int(port_str)
        except ValueError:
            ip = remote
            port = None

        ip_meta_list.append(
            IP_METADATA(
                ip=ip,
                port=port,
                protocol=protocol
            )
        )

    return ip_meta_list


# ---------------------------------------------------------------------------
# Metadata Collection (DNS Resolution)
# ---------------------------------------------------------------------------

def ip_address_metadata_collection(ip_meta_list: List[IP_METADATA]) -> None:
    """
    Resolve hostnames for each IP address.

    Args:
        ip_meta_list (List[IP_METADATA]): List of metadata objects.
    """
    for meta in ip_meta_list:
        try:
            meta.hostname = socket.gethostbyaddr(meta.ip)[0]
        except Exception:
            # Hostname resolution may fail; ignore silently
            meta.hostname = None


# ---------------------------------------------------------------------------
# Geolocation Lookup
# ---------------------------------------------------------------------------

def ip_address_geoidentification(ip_meta_list: List[IP_METADATA]) -> None:
    """
    Enrich IP metadata with geolocation data using a public API.

    Args:
        ip_meta_list (List[IP_METADATA]): List of metadata objects.
    """
    import urllib.request

    for meta in ip_meta_list:
        try:
            url = f"http://ip-api.com/json/{meta.ip}"

            with urllib.request.urlopen(url, timeout=2) as response:
                data = json.loads(response.read().decode())

            if data.get("status") == "success":
                meta.country = data.get("country")
                meta.city = data.get("city")
                meta.org = data.get("org")

        except Exception:
            # Network/API failures are ignored
            continue


# ---------------------------------------------------------------------------
# Main Execution
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Main execution flow.
    """
    # Parse arguments
    args = args_parsing()

    # Collect raw lsof output
    raw_lines = collect_open_file_ips()

    # Extract IP metadata
    ip_meta_list = ip_address_identification(raw_lines)

    # Resolve hostnames
    ip_address_metadata_collection(ip_meta_list)

    # Optional geolocation enrichment
    if args.geo:
        ip_address_geoidentification(ip_meta_list)

    # Convert to serializable format
    output_data = [asdict(meta) for meta in ip_meta_list]

    # Output results
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as file:
                json.dump(output_data, file, indent=2)
        except IOError as exc:
            print(f"[ERROR] Failed to write output file: {exc}")
    else:
        print(json.dumps(output_data, indent=2))


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()
