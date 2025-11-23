# src/kaggle_features.py
"""
Feature extractor to map a raw URL -> feature dict matching Kaggle dataset columns.
It computes lexical & domain features and fills heavier network features (WHOIS, SSL, DNS)
when available. Safe defaults (0) are used to avoid accidentally signaling "malicious".
Use `do_whois=True` to enable WHOIS lookups (slower per-request).
"""

import re
from urllib.parse import urlparse
import tldextract
import pandas as pd
import socket
import os

# Try to import WHOIS and date parsing tools; allow graceful fallback
try:
    import whois
    from dateutil import parser as dateparser
    from datetime import datetime, timezone
    WHOIS_AVAILABLE = True
except Exception:
    # whois/dateutil not available -> WHOIS features disabled but extractor still works
    WHOIS_AVAILABLE = False
    from datetime import datetime, timezone  # still import datetime used for safe typing

# SSL imports
import ssl
import datetime as _datetime

SHORTENERS = [
    "bit.ly","tinyurl.com","goo.gl","t.co","ow.ly","buff.ly","adf.ly","bitly.com",
    "is.gd","mcaf.ee","trib.al","shorturl.at","tiny.cc"
]

# Simple in-memory cache for WHOIS lookups to avoid repeated network calls
_WHOIS_CACHE = {}

# ---------------- WHOIS helpers ----------------
def safe_parse_date(d):
    """Try to parse many date formats, return datetime or None."""
    try:
        if d is None:
            return None
        # some whois fields are lists; take first
        if isinstance(d, (list, tuple)):
            d = d[0]
        # some values are already datetime
        if isinstance(d, datetime):
            return d
        # if parser available, use it; otherwise try simple parsing
        if WHOIS_AVAILABLE:
            return dateparser.parse(str(d))
        else:
            return None
    except Exception:
        return None

def get_whois_dates_for_domain(domain):
    """
    Return (creation_date, expiration_date) as datetimes or (None, None) on failure.
    domain is a string like 'google.com' (no protocol).
    Results cached in _WHOIS_CACHE for the session.
    """
    if not WHOIS_AVAILABLE:
        return None, None

    if not domain:
        return None, None

    if domain in _WHOIS_CACHE:
        return _WHOIS_CACHE[domain]

    try:
        w = whois.whois(domain)
    except Exception:
        _WHOIS_CACHE[domain] = (None, None)
        return None, None

    creation = None
    expiration = None
    # possible keys - try multiple names in the whois response
    for k in ("creation_date", "created", "created_date"):
        try:
            if k in w and w[k]:
                creation = safe_parse_date(w[k])
                break
        except Exception:
            pass
    for k in ("expiration_date", "expires", "registry_expiry_date", "expire_date"):
        try:
            if k in w and w[k]:
                expiration = safe_parse_date(w[k])
                break
        except Exception:
            pass

    # some whois implementations expose attributes directly
    try:
        if creation is None and getattr(w, "creation_date", None):
            creation = safe_parse_date(getattr(w, "creation_date"))
        if expiration is None and getattr(w, "expiration_date", None):
            expiration = safe_parse_date(getattr(w, "expiration_date"))
    except Exception:
        pass

    _WHOIS_CACHE[domain] = (creation, expiration)
    return creation, expiration

# ---------------- SSL helper ----------------
def get_ssl_expiry_days(domain, port=443, timeout=5):
    """
    Connect to domain:port, fetch SSL cert, return days until expiry (int).
    Returns 0 on any failure (no cert, timeout, connection error).
    """
    if not domain:
        return 0
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((domain, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                not_after = cert.get('notAfter')
                if not not_after:
                    return 0
                # Example format: 'May  1 12:00:00 2026 GMT'
                try:
                    expiry = _datetime.datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                except Exception:
                    # fallback: try parsing without timezone name
                    try:
                        expiry = _datetime.datetime.strptime(not_after, '%b %d %H:%M:%S %Y')
                    except Exception:
                        return 0
                now = _datetime.datetime.utcnow()
                delta = expiry - now
                days = max(int(delta.total_seconds() // 86400), 0)
                return days
    except Exception:
        return 0

# ----- DNS helpers (requires dnspython) -----
try:
    import dns.resolver
    DNS_AVAILABLE = True
except Exception:
    DNS_AVAILABLE = False

def safe_dns_query(name, rdtype):
    """
    Return number of answers for the given record type or 0 on failure.
    """
    if not DNS_AVAILABLE or not name:
        return 0
    try:
        answers = dns.resolver.resolve(name, rdtype, lifetime=3.0)
        return len(answers)
    except Exception:
        return 0

def compute_dns_counts(domain):
    """
    Returns dict with:
      - qty_ip_resolved: number of A records (IPs)
      - qty_nameservers: number of NS records
      - qty_mx_servers: number of MX records
    """
    out = {'qty_ip_resolved': 0, 'qty_nameservers': 0, 'qty_mx_servers': 0}
    if not domain or not DNS_AVAILABLE:
        return out
    try:
        out['qty_ip_resolved'] = safe_dns_query(domain, 'A')
        out['qty_nameservers'] = safe_dns_query(domain, 'NS')
        out['qty_mx_servers'] = safe_dns_query(domain, 'MX')
    except Exception:
        pass
    return out

# ---------------- domain age features ----------------
def compute_domain_age_features(domain):
    """
    Returns dict with:
      - time_domain_activation : days since creation (int) or 0 if unknown
      - time_domain_expiration : days until expiration (int) or 0 if unknown/expired
    """
    out = {'time_domain_activation': 0, 'time_domain_expiration': 0}
    try:
        creation, expiration = get_whois_dates_for_domain(domain)
        now = datetime.now(timezone.utc) if WHOIS_AVAILABLE else None
        if creation and now:
            # days since creation
            delta = now - creation if creation.tzinfo else now - creation.replace(tzinfo=timezone.utc)
            out['time_domain_activation'] = max(int(delta.total_seconds() // 86400), 0)
        if expiration and now:
            # days until expiration
            delta2 = expiration - now if expiration.tzinfo else expiration.replace(tzinfo=timezone.utc) - now
            out['time_domain_expiration'] = max(int(delta2.total_seconds() // 86400), 0)
    except Exception:
        out['time_domain_activation'] = 0
        out['time_domain_expiration'] = 0
    return out

# ---------------- basic helpers ----------------
def count_char(s, ch):
    return s.count(ch) if s else 0

def has_ip(hostname):
    try:
        return 1 if re.match(r'^\d+\.\d+\.\d+\.\d+$', hostname) else 0
    except:
        return 0

def is_shortened(url):
    try:
        parsed = urlparse(url)
        host = (parsed.netloc or "").lower()
        for s in SHORTENERS:
            if s in host:
                return 1
        return 0
    except:
        return 0

def get_domain(url):
    """
    Return the registered domain (e.g. example.com) given a URL or hostname string.
    """
    try:
        if not url:
            return ""
        parsed = tldextract.extract(url)
        domain = parsed.domain or ""
        suffix = parsed.suffix or ""
        registered = (domain + (("." + suffix) if suffix else ""))
        return registered
    except:
        return ""

def safe_len(x):
    try:
        return len(str(x))
    except:
        return 0

# ---------------- lexical & domain feature extractors ----------------
def extract_basic_lexical(url):
    u = str(url).strip()
    parsed = urlparse(u)
    hostname = parsed.hostname or ""
    path = parsed.path or ""
    query = parsed.query or ""
    feats = {}
    feats['qty_dot_url'] = count_char(u, '.')
    feats['qty_hyphen_url'] = count_char(u, '-')
    feats['qty_underline_url'] = count_char(u, '_')
    feats['qty_slash_url'] = count_char(u, '/')
    feats['qty_questionmark_url'] = count_char(u, '?')
    feats['qty_equal_url'] = count_char(u, '=')
    feats['qty_at_url'] = count_char(u, '@')
    feats['qty_and_url'] = count_char(u, '&')
    feats['qty_exclamation_url'] = count_char(u, '!')
    feats['qty_space_url'] = count_char(u, ' ')
    feats['qty_tilde_url'] = count_char(u, '~')
    feats['qty_comma_url'] = count_char(u, ',')
    feats['qty_plus_url'] = count_char(u, '+')
    feats['qty_asterisk_url'] = count_char(u, '*')
    feats['qty_hashtag_url'] = count_char(u, '#')
    feats['qty_dollar_url'] = count_char(u, '$')
    feats['qty_percent_url'] = count_char(u, '%')
    feats['qty_tld_url'] = 1 if '.' in (tldextract.extract(u).suffix or "") else 0
    feats['length_url'] = len(u)
    feats['email_in_url'] = 1 if re.search(r'mailto:|@', u) else 0
    feats['url_shortened'] = is_shortened(u)
    feats['has_https'] = 1 if u.lower().startswith('https') else 0
    # path/dir/file/params counts (approx)
    feats['qty_dot_directory'] = count_char(path, '.')
    feats['directory_length'] = safe_len(path)
    feats['qty_dot_file'] = count_char(path.split('/')[-1], '.')
    feats['file_length'] = safe_len(path.split('/')[-1])
    feats['qty_params'] = 1 if query else 0
    feats['params_length'] = safe_len(query)
    return feats, hostname

def extract_domain_features_from_hostname(hostname):
    parsed = tldextract.extract(hostname)
    feats = {}
    feats['qty_dot_domain'] = count_char(hostname, '.')
    feats['qty_hyphen_domain'] = count_char(hostname, '-')
    feats['qty_underline_domain'] = count_char(hostname, '_')
    feats['domain_length'] = len(hostname)
    feats['domain_in_ip'] = has_ip(hostname)
    feats['qty_vowels_domain'] = sum(1 for ch in hostname if ch.lower() in 'aeiou')
    return feats

# ---------------- heavy defaults ----------------
def heavy_defaults():
    return {
        'time_domain_activation': 0,
        'time_domain_expiration': 0,
        'qty_ip_resolved': 0,
        'qty_nameservers': 0,
        'qty_mx_servers': 0,
        'time_response': 0,
        'domain_spf': 0,
        'ttl_hostname': 0,
        'tls_ssl_certificate': 0,
        'qty_redirects': 0,
        'url_google_index': 0,
        'domain_google_index': 0,
        'asn_ip': 0
    }

# ---------------- main extractor ----------------
def extract_kaggle_features(url, expected_columns=None, do_whois=False):
    """
    url: raw URL string
    expected_columns: list of column names the Kaggle model expects (so we keep same order)
    do_whois: (optional) try to fill WHOIS fields (may be slow)
    returns: ordered dict (Python dict with keys of expected_columns)
    """
    base_feats = {}
    lexical_feats, hostname = extract_basic_lexical(url)
    domain_feats = extract_domain_features_from_hostname(hostname)
    base_feats.update(lexical_feats)
    base_feats.update(domain_feats)

    # start with safe defaults for heavy features
    base_feats.update(heavy_defaults())

    # WHOIS features (optional)
    registered_domain = get_domain(url)
    if do_whois and WHOIS_AVAILABLE and registered_domain:
        try:
            whois_feats = compute_domain_age_features(registered_domain)
            # merge whois values into base
            base_feats.update(whois_feats)
        except Exception:
            pass

    # SSL/TLS certificate feature: days until expiry (0 if no cert/failure)
    try:
        ssl_days = get_ssl_expiry_days(registered_domain)
        base_feats['tls_ssl_certificate'] = ssl_days
    except Exception:
        base_feats['tls_ssl_certificate'] = base_feats.get('tls_ssl_certificate', 0)

    # DNS counts (fast) — improves classifier
    try:
        dns_feats = compute_dns_counts(registered_domain)
        base_feats.update(dns_feats)
    except Exception:
        pass

    # if expected_columns provided, ensure all keys present (fill with 0 by default)
    if expected_columns is None:
        return base_feats

    out = {}
    for col in expected_columns:
        key = col.strip()
        if key in base_feats:
            out[key] = base_feats[key]
        else:
            # fallback heuristics: always use 0 as neutral default
            out[key] = 0
    return out

# ---------------- utility to load columns ----------------
def load_kaggle_columns(kaggle_csv_path):
    """
    Read header of kaggle CSV and return list of feature columns (exclude label column)
    """
    df = pd.read_csv(kaggle_csv_path, nrows=1, encoding='utf-8-sig')
    cols = list(df.columns)
    # find label column (common names)
    label_candidates = [c for c in cols if any(x in c.lower() for x in ['label','phish','result','class','status'])]
    label_col = label_candidates[0] if label_candidates else None
    feature_cols = [c for c in cols if c != label_col]
    return feature_cols, label_col

# ---------------- quick test when run directly ----------------
if __name__ == "__main__":
    cols, label = load_kaggle_columns("../data/raw/kaggle_phish.csv")
    print("Detected feature columns (sample):", cols[:20], "label:", label)
    u = "http://paypal.com.security-checkupdate.com/login"
    feats = extract_kaggle_features(u, expected_columns=cols, do_whois=False)
    for k in list(feats.keys())[:40]:
        print(k, ":", feats[k])
