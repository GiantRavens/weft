"""TLS for weft's fetches: the system's trusted roots, plus intermediate certificates that some servers fail
to send (pin 69). A browser fetches a missing intermediate from the address in the server's certificate; Python's
OpenSSL does not, so a server that omits it cannot be verified. Weft supplies those intermediates from
data/tls/, each pinned by sha256 and checked to chain to a root already in the system store. They are chain
material, not trust anchors: partial-chain verification is switched off, so every chain must still end at a
system root, and nothing is verified that the system would not verify given the full chain.

InCommonRSAServerCA2.pem  InCommon RSA Server CA 2 (Internet2), issued by USERTrust RSA Certification
                          Authority, valid to 2032-11-15; from http://crt.sectigo.com/InCommonRSAServerCA2.crt,
                          the address in Oracc's certificate. Oracc (oracc.museum.upenn.edu) omits it.
"""
from __future__ import annotations

import hashlib
import ssl
from pathlib import Path

DIR = Path(__file__).parent / "data" / "tls"
PINS = {"InCommonRSAServerCA2.pem": "6e5a1f3cbe059cda144f2a38d3d61a73c580ea5b18de767da8099982937b0e2a"}
_CTX: ssl.SSLContext | None = None


def context() -> ssl.SSLContext:
    global _CTX
    if _CTX is None:
        ctx = ssl.create_default_context()
        ctx.verify_flags &= ~ssl.VERIFY_X509_PARTIAL_CHAIN     # an intermediate never ends a chain
        for name, want in PINS.items():
            pem = (DIR / name).read_bytes()
            if hashlib.sha256(pem).hexdigest() != want:
                raise SystemExit(f"weft: {DIR / name} does not match its pinned sha256")
            ctx.load_verify_locations(cadata=pem.decode("ascii"))
        _CTX = ctx
    return _CTX
