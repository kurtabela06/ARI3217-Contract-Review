"""Knowledge-supported retrieval from the supplied notebook."""

from contract_review.features import details


LEXICON = {   # the team's clause lexicon: phrases a reviewer searches for. An assumption, versioned with the KB (task E1)
    "Document Name": ["agreement", "this agreement", "contract", "exhibit"],
    "Parties": ["by and between", "entered into by", "between", "corporation", "limited liability company", "hereinafter", "party", "parties"],
    "Agreement Date": ["dated as of", "made and entered into", "day of", "as of the date", "dated"],
    "Effective Date": ["effective date", "effective as of", "shall become effective", "commencement date", "effective upon"],
    "Expiration Date": ["initial term", "expire", "expiration", "remain in effect", "remain in full force", "years from", "term of this agreement"],
    "Renewal Term": ["renew", "renewal", "automatically renewed", "successive", "additional term", "extend the term"],
    "Notice Period To Terminate Renewal": ["notice of non-renewal", "prior to the expiration", "days prior", "not to renew", "written notice", "elect not to renew"],
    "Governing Law": ["governed by", "laws of the state", "construed in accordance", "governing law", "without regard to conflicts"],
    "Most Favored Nation": ["most favored", "most favoured", "no less favorable", "more favorable terms", "lower price", "better terms", "terms offered to any other"],
    "Non-Compete": ["compete", "competing", "competitive", "non-compete", "shall not engage", "directly or indirectly", "competitor"],
    "Exclusivity": ["exclusive", "exclusively", "sole and exclusive", "exclusive distributor", "exclusive right", "requirements", "shall not appoint"],
    "No-Solicit Of Customers": ["solicit", "customers", "clients", "induce", "divert", "entice", "accounts"],
    "Competitive Restriction Exception": ["notwithstanding", "except", "shall not apply", "shall not prevent", "provided however", "nothing in this", "exception"],
    "No-Solicit Of Employees": ["solicit", "hire", "employ", "employees", "personnel", "recruit"],
    "Non-Disparagement": ["disparage", "disparaging", "derogatory", "negative statements", "reputation"],
    "Termination For Convenience": ["terminate this agreement", "for any reason", "without cause", "for convenience", "at any time", "with or without cause"],
    "Rofr/Rofo/Rofn": ["right of first refusal", "first refusal", "right of first offer", "first negotiation", "right to match", "first option"],
    "Change Of Control": ["change of control", "change in control", "merger", "acquisition", "acquired", "controlling interest", "substantially all", "voting securities"],
    "Anti-Assignment": ["assign", "assignment", "transfer", "prior written consent", "delegate", "successors and assigns"],
    "Revenue/Profit Sharing": ["royalty", "royalties", "revenue share", "profits", "percentage of", "net sales", "commission", "share of revenue"],
    "Price Restrictions": ["price", "pricing", "shall not increase", "price increase", "price adjustment", "fixed price", "price protection"],
    "Minimum Commitment": ["minimum", "at least", "minimum purchase", "minimum order", "minimum quantity", "shall purchase", "annual minimum", "shortfall"],
    "Volume Restriction": ["volume", "exceed", "in excess of", "maximum", "threshold", "additional fee", "usage"],
    "Ip Ownership Assignment": ["hereby assigns", "shall own", "ownership", "work made for hire", "right title and interest", "vest", "sole property"],
    "Joint Ip Ownership": ["jointly owned", "joint ownership", "co-owned", "jointly", "joint inventions", "owned jointly"],
    "License Grant": ["hereby grants", "grants to", "license", "licence", "right to use", "sublicense"],
    "Non-Transferable License": ["non-transferable", "nontransferable", "non-assignable", "non-sublicensable", "may not sublicense", "personal"],
    "Affiliate License-Licensor": ["affiliates", "licensor and its affiliates", "its affiliates", "affiliate"],
    "Affiliate License-Licensee": ["affiliates", "licensee and its affiliates", "subsidiaries", "affiliate"],
    "Unlimited/All-You-Can-Eat-License": ["unlimited", "enterprise", "any number", "unlimited number", "all you can eat", "without limitation"],
    "Irrevocable Or Perpetual License": ["irrevocable", "perpetual", "fully paid", "royalty-free", "in perpetuity"],
    "Source Code Escrow": ["escrow", "source code", "escrow agent", "release condition", "deposit"],
    "Post-Termination Services": ["after termination", "following termination", "upon termination", "survive", "transition", "wind down", "sell off"],
    "Audit Rights": ["audit", "inspect", "examine", "books and records", "records", "accountant"],
    "Uncapped Liability": ["shall not apply", "gross negligence", "willful misconduct", "indemnification obligations", "breach of confidentiality", "unlimited liability", "exclusions"],
    "Cap On Liability": ["in no event", "liability", "shall not exceed", "aggregate liability", "limitation of liability", "consequential", "maximum"],
    "Liquidated Damages": ["liquidated damages", "termination fee", "penalty", "break fee", "liquidated"],
    "Warranty Duration": ["warranty", "warrants", "warranty period", "months from", "free from defects"],
    "Insurance": ["insurance", "insured", "policy", "coverage", "additional insured", "certificate of insurance"],
    "Covenant Not To Sue": ["not to sue", "contest", "challenge", "validity", "shall not challenge", "covenant not to", "claim"],
    "Third Party Beneficiary": ["third party beneficiary", "third-party beneficiaries", "intended beneficiary", "enforce", "no third party"],
}


def knowledge_queries(questions):
    """Build the notebook's description-plus-lexicon queries."""
    queries = []

    for category, question in zip(
        questions.category, questions.question
    ):
        base_query = f"{category} {details(question)}"
        queries.append(
            f"{base_query} " + " ; ".join(LEXICON[category])
        )

    return queries
