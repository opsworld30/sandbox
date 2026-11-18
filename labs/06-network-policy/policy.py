"""Exact-host allowlist decision helper. Not a network enforcement mechanism."""
from __future__ import annotations

import ipaddress
import re


_HOST_LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")


def normalize_host(host: str) -> str:
    value = host.strip().rstrip(".").lower()
    if not value or any(ch in value for ch in "/:@?#"):
        raise ValueError("expected a bare hostname, without scheme, path, or port")
    try:
        return value.encode("idna").decode("ascii")
    except UnicodeError as exc:
        raise ValueError("invalid IDN hostname") from exc


def is_public_ip_literal(host: str) -> bool:
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return False
    return address.is_global


class EgressPolicy:
    def __init__(self, allowed_hosts: set[str]) -> None:
        self.allowed = {normalize_host(item) for item in allowed_hosts}

    def decide(self, host: str) -> tuple[bool, str]:
        try:
            normalized = normalize_host(host)
        except ValueError as exc:
            return False, f"invalid-host: {exc}"

        try:
            ipaddress.ip_address(normalized)
            return False, "IP literals are denied; use an approved hostname"
        except ValueError:
            pass

        labels = normalized.split(".")
        if any(not _HOST_LABEL.fullmatch(label) for label in labels):
            return False, "invalid DNS label"
        if normalized not in self.allowed:
            return False, "hostname is not in the exact allowlist"
        return True, "exact hostname match"
