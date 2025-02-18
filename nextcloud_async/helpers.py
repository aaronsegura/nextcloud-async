"""Helper functions for NextcloudAsync."""

from urllib.parse import quote
import httpx
# import asyncio

from typing import Dict, Hashable, Any, List, Optional


def recursive_urlencode(d: Dict[Hashable, Any]) -> str:
    """URL-encode a multidimensional dictionary PHP-style.

    https://stackoverflow.com/questions/4013838/urlencode-a-multidimensional-dictionary-in-python/4014164#4014164

    Updated for python3.

    >>> data = {'a': 'b&c', 'd': {'e': {'fg': 'hi'}}, 'j': 'k'}
    >>> recursive_urlencode(data)
    u'a=b%26c&j=k&d[e][f%26g]=h%2Ai'
    """
    def _recursion(d: Dict[str, str], base: List[str] = []) -> List[str]:
        pairs: List[str] = []

        for key, value in d.items():
            new_base: List[str] = base + [key]
            if hasattr(value, 'values'):
                pairs += _recursion(value, new_base)  # type: ignore
            else:
                new_pair = None
                if len(new_base) > 1:
                    first = quote(new_base.pop(0))
                    rest = map(lambda x: quote(x), new_base)
                    new_pair = f'{first}[{"][".join(rest)}]={quote(value)}'
                else:
                    new_pair = f'{quote(key)}={quote(value)}'
                pairs.append(new_pair)
        return pairs

    return '&'.join(_recursion(d))  # type: ignore


# def resolve_element_list(data: Dict|List, list_keys=[]):
#     """Resolve all 'element' items into a list.

#     A side-effect of using xmltodict on nextcloud results is that lists of
#     items come back differently depending on how many results there are, and
#     there is always an unnecessary parent 'element' key wrapping the list:

#     Zero results returns:
#         {
#             'items': 'None'
#         }

#     One or more results returns a dict containing a list:
#         {
#             'items': {
#                 'element': [...]
#             }
#         }

#     We want to get rid of the 'element' middle-man and turn all
#     list items into their proper representation:

#     Zero results:
#         {
#             'items': []
#         }

#     One or more results:
#         {
#             'items': [
#                 ...,
#                 ...,
#             ]
#         }
#     """
#     ret = {}
#     if isinstance(data, dict):
#         for k, v in data.items():
#             if isinstance(v, dict):
#                 if k == 'element':
#                     ret = resolve_element_list(v, list_keys=list_keys)
#                 else:
#                     ret.setdefault(k, resolve_element_list(v, list_keys=list_keys))
#             elif isinstance(v, list) and k == 'element':
#                 ret = v
#             elif k in list_keys and v is None:
#                 ret = {k: []}
#             else:
#                 ret.setdefault(k, v)
#     else:
#         ret = resolve_element_list(data, list_keys=list_keys)

#     return ret

def str2bool(s: str) -> bool:
    return True if s.lower() in ["true", "t", "1", "yes"] else False

def bool2str(b: bool) -> str:
    return "true" if b else "false"

def bool2int(b: bool) -> int:
    return 1 if b else 0

def none2str(v: Optional[str]) -> Optional[str]:
    return None if not v else v

def phone_number_to_E164(phone_number: str) -> str:
    new_format: List[str] = []
    for digit in reversed(phone_number):
        new_format.append(digit)

    return f'{".".join(new_format)}.e164.arpa'

def filter_headers(filter: List[str], headers: httpx.Headers) -> httpx.Headers:
    return httpx.Headers([x for x in headers.items() if x[0].lower() in filter])

def remove_key_prefix(d: Dict[str, Any]) -> Dict[str, Any]:
    return {k[k.find(':')+1:]: v for k, v in d.items()}
