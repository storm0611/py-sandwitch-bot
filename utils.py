def match(addr_a: str, addr_b: str, caseIncensitive: bool = True):
    if caseIncensitive:
        return addr_a.lower() == addr_b.lower()
    else:
        return addr_a == addr_b