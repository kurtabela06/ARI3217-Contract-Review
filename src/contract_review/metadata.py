"""Contract type and filing-year rules from the supplied notebook."""

import re

import numpy as np


TYPE_RULES = [  # (type, pattern on the agreement name in the title); first match wins
    ("Non-Compete/No-Solicit/Non-Disparagement", r"non[- ]?compet|non[- ]?solicit"), ("Franchise", r"franchis"),
    ("Endorsement", r"endorse"), ("Sponsorship", r"sponsor"), ("Co-Branding", r"co[- ]?brand"), ("Hosting", r"hosting"),
    ("Joint Venture", r"joint venture|joint filing"), ("Strategic Alliance", r"alliance"), ("Affiliate", r"affiliate"),
    ("Outsourcing", r"outsourc"), ("Transportation", r"transport|shipping|freight"), ("Maintenance", r"maintenance|support"),
    ("Consulting", r"consult"), ("Reseller", r"resell"), ("Distributor", r"distribut"), ("Promotion", r"promot"),
    ("Collaboration/Cooperation", r"collaborat|cooperat"), ("Manufacturing", r"manufactur"), ("Supply", r"supply"),
    ("Development", r"develop"), ("Agency", r"agency|agent"), ("Marketing", r"marketing"), ("License", r"licen[cs]"),
    ("IP", r"intellectual property|\bip\b|patent|trademark"), ("Service", r"servic"),
]


def agreement_name(title: str) -> str:
    m = re.search(r"EX-[\d.()A-Z]+[-_ ](?:\d+_EX-[\d.()A-Z]+_)?(.*)$", title)
    name = m.group(1) if m and m.group(1).strip() else title.split(" - ")[-1]
    return name.replace("_", " ").strip()


def contract_type(title: str) -> str:
    name = agreement_name(title).lower()
    return next((t for t, pat in TYPE_RULES if re.search(pat, name)), "Other")


def filing_year(title: str):
    m = re.search(r"_\d{2}_\d{2}_((?:19|20)\d{2})", title) or re.search(r"_((?:19|20)\d{2})\d{4}_", title)
    return int(m.group(1)) if m else np.nan
