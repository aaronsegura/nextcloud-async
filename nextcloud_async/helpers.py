"""Helper functions for NextcloudAsync."""

from urllib.parse import quote
import httpx

from typing import Dict, Any, List


def recursive_urlencode(d: Dict[str, Any]) -> str:
    """URL-encode a multidimensional dictionary PHP-style.

    https://stackoverflow.com/questions/4013838/urlencode-a-multidimensional-dictionary-in-python/4014164#4014164

    Updated for python3.

    >>> data = {'a': 'b&c', 'd': {'e': {'fg': 'hi'}}, 'j': 'k'}
    >>> recursive_urlencode(data)
    'a=b%26c&d[e][fg]=hi&j=k'
    """
    def _recursion(d: Dict[str, str], base: List[str] = []) -> List[str]:
        pairs: List[str] = []

        for key, value in d.items():
            new_base: List[str] = base + [key]
            if hasattr(value, 'values'):
                pairs += _recursion(value, new_base)   # type: ignore
            else:
                new_pair = None
                if len(new_base) > 1:
                    first = quote(new_base.pop(0))
                    rest = [quote(x) for x in new_base]
                    new_pair = f'{first}[{"][".join(rest)}]={quote(value)}'
                else:
                    new_pair = f'{quote(key)}={quote(value)}'
                pairs.append(new_pair)
        return pairs

    return '&'.join(_recursion(d))

def bool2int(b: bool) -> int:
    """Translate boolean values to integers.

    Args:
        b:
            Boolean value

    Returns:
        0 if False, 1 if True
    """
    return 1 if b else 0

def phone_number_to_e164(phone_number: str) -> str:
    """Translate phone number to E164 format.

    Args:
        phone_number:
            Phone number

    Returns:
        E164 phone number
    """
    new_format: List[str] = []
    for digit in reversed(phone_number):
        new_format.append(digit)

    return f'{".".join(new_format)}.e164.arpa'

def filter_headers(filter: List[str], headers: httpx.Headers) -> httpx.Headers:
    """Filter result headers down to just the ones we want.

    Args:
        filter:
            List of headers we want

        headers:
            List of all headers

    Returns:
        List of filtered headers
    """
    return httpx.Headers([x for x in headers.items() if x[0].lower() in filter])

def remove_key_prefix(d: Dict[str, Any]) -> Dict[str, Any]:
    """Remove the namespace prefix on dictionary keys.

    DAV Endpoint shenanigans.

    {'oc:fileid': 3} -> {'fileid' : 3}

    Args:
        d:
            Dictionary

    Returns:
        Dictionary with trimmed keys
    """
    return {k[k.find(':')+1:]: v for k, v in d.items()}
