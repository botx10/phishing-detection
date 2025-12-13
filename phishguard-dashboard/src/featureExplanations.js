// src/featureExplanations.js

export const FEATURE_EXPLANATIONS = {
  // URL structure features
  length_url:
    "Very long URLs are often used in phishing attacks to hide malicious parameters and confuse users.",

  directory_length:
    "Long and deeply nested directory paths are commonly used to conceal phishing content.",

  qty_slash_directory:
    "Multiple directory slashes can indicate complex redirection patterns often seen in phishing URLs.",

  qty_dot_file:
    "Excessive dots in file names may suggest obfuscation techniques used by attackers.",

  qty_dollar_directory:
    "Special characters like '$' are frequently used in phishing URLs to trick users.",

  // Domain-based features
  time_domain_activation:
    "Newly registered domains are commonly associated with phishing campaigns.",

  domain_length:
    "Unusually long domain names may be crafted to resemble legitimate brands.",

  qty_hyphen_domain:
    "Hyphens in domain names are often used to imitate trusted websites.",

  qty_subdomain:
    "Multiple subdomains can be used to mislead users about the true destination of a URL.",

  // Security-related features
  https_token:
    "The presence or misuse of HTTPS-related tokens can be deceptive in phishing URLs.",

  ip_address:
    "Using an IP address instead of a domain name is a strong indicator of phishing behavior.",

  // Fallback (used if explanation is missing)
  __default__:
    "This indicator represents a structural property of the URL commonly analyzed in phishing detection."
};
