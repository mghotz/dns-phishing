import itertools
import tldextract


def generate_similar_domains(domain_name):
    tld = tldextract.extract(domain_name).suffix
    domain = domain_name.replace('.' + tld, '')

    # Generate domain permutations
    domain_permutations = set()
    for i in range(len(domain)):
        for j in range(len(domain)):
            if i != j:
                domain_permutations.add(domain[:i] + domain[j] + domain[i + 1:])

    # Generate typo-squatting domains
    typo_squatting_domains = set()
    for typo in domain_permutations:
        if typo != domain:
            typo_squatting_domains.add(typo + '.' + tld)

    # Generate Levenshtein distance based domains
    levenshtein_domains = set()
    for i in range(len(domain)):
        for c in itertools.combinations('abcdefghijklmnopqrstuvwxyz0123456789-', 2):
            typo = domain[:i] + c[0] + domain[i + 1:]
            if typo != domain:
                levenshtein_domains.add(typo + '.' + tld)
            typo = domain[:i] + c[1] + domain[i + 1:]
            if typo != domain:
                levenshtein_domains.add(typo + '.' + tld)

    # Combine the two sets and return as list
    similar_domains = list(typo_squatting_domains.union(levenshtein_domains))
    return similar_domains

# Example usage
domain = 'idda.az'
similar_domains = generate_similar_domains(domain)
print(similar_domains)