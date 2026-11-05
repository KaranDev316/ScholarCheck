"""Conservative numeric and qualifier checks; ambiguous values never match."""
import re
from decimal import Decimal, InvalidOperation

NUMBER = re.compile(r"(?<![\w.,+\-])(?:\d{1,3}(?:[, \u00a0\u202f]\d{3})+(?:[.,]\d{1,2})?|\d+(?:[.,]\d{1,2})?)(?![\w.,%])")


def number(value: str) -> Decimal:
    value = re.sub(r"[\s\u00a0\u202f]", "", value)
    if ',' in value and '.' in value:
        decimal = ',' if value.rfind(',') > value.rfind('.') else '.'
        value = value.replace('.' if decimal == ',' else ',', '').replace(decimal, '.')
    elif ',' in value:
        value = value.replace(',', '.' if len(value.rsplit(',', 1)[1]) == 2 else '')
    return Decimal(value)


def amount_in_text(amount: Decimal, text: str) -> bool:
    return any(
        number(match.group()) == amount
        and not text[:match.start()].rstrip().endswith(('-', '+', '−'))
        and not re.match(r"\s*(?:%|percent\b|per cent\b)", text[match.end():], re.I)
        for match in NUMBER.finditer(text)
    )


def same_amount(left: str, right: str) -> bool:
    try:
        return number(left) == number(right)
    except InvalidOperation:
        return False


def words(text: str) -> str:
    return ' '.join(text.casefold().replace('_', ' ').split())


def value_in_text(kind: str, value: str, excerpt: str) -> bool:
    text = words(excerpt)
    value = words(value)
    if kind == 'amount':
        try:
            return amount_in_text(number(value), excerpt)
        except InvalidOperation:
            return False
    if kind == 'currency':
        aliases = {'cad': ('cad', 'ca$', 'c$', 'canadian dollars'),
                   'aud': ('aud', 'a$', 'au$', 'australian dollars'),
                   'usd': ('usd', 'us$', 'us dollars'), 'eur': ('eur', '€', 'euros')}
        return any(re.search(r'(?<!\w)' + re.escape(term) + r'(?![a-z])', text)
                   for term in aliases.get(value, (value,)))
    if kind == 'period':
        aliases = {'per year': ('per year', 'p.a.', 'annually', 'par année'),
                   'per month': ('per month', 'monthly', 'par mois')}
        return any(term in text for term in aliases.get(value, (value,)))
    if kind == 'funding_relationship':
        aliases = {'grant': ('scholarship', 'stipend', 'award', 'grant', 'bourse'),
                   'tuition reduction': ('tuition', 'fee offset', 'exemption'),
                   'loan': ('loan',), 'employment': ('employment', 'salary')}
        return any(term in text for term in aliases.get(value, (value,)))
    if kind == 'coverage':
        if re.search(r'\b(not|no|partial|partially|excluding|excludes)\b', text):
            return False
        patterns = {'full tuition': ('100% tuition', 'full tuition', 'all tuition'),
                    'living costs': ('stipend', 'living allowance', 'living costs'),
                    'flights': ('airfare', 'flights', 'air ticket')}
        return value in patterns and any(term in text for term in patterns[value])
    if kind == 'rate_year':
        return re.search(r'(?<!\d)' + re.escape(value) + r'(?!\d)', text) is not None
    if kind in {'deadline', 'intake', 'application_route'}:
        return value in text
    return True  # prose semantics require the separate evidence checker
