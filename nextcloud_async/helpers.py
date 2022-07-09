"""Helper functions for NextCloudAsync."""

import urllib

from typing import Dict


def recursive_urlencode(d: Dict):
    """URL-encode a multidimensional dictionary PHP-style.

    https://stackoverflow.com/questions/4013838/urlencode-a-multidimensional-dictionary-in-python/4014164#4014164

    Updated for python3.

    >>> data = {'a': 'b&c', 'd': {'e': {'f&g': 'h*i'}}, 'j': 'k'}
    >>> recursive_urlencode(data)
    u'a=b%26c&j=k&d[e][f%26g]=h%2Ai'
    """
    def _recursion(d, base=[]):
        pairs = []

        for key, value in d.items():
            new_base = base + [key]
            if hasattr(value, 'values'):
                pairs += _recursion(value, new_base)
            else:
                new_pair = None
                if len(new_base) > 1:
                    first = urllib.parse.quote(new_base.pop(0))
                    rest = map(lambda x: urllib.parse.quote(x), new_base)
                    new_pair = f'{first}[{"][".join(rest)}]={urllib.parse.quote(value)}'
                else:
                    new_pair = f'{urllib.parse.quote(key)}={urllib.parse.quote(value)}'
                pairs.append(new_pair)
        return pairs

    return '&'.join(_recursion(d))


def resolve_element_list(data: Dict, list_keys=[]):
    """Resolve all 'element' items into a list.

    A side-effect of using xmltodict on nextcloud results is that lists of
    items come back differently depending on how many results there are, and
    there is always an unnecessary parent 'element' key wrapping the list:

    Zero results returns:
        {
            'items': 'None'
        }

    One or more results returns a dict containing a list:
        {
            'items': {
                'element': [...]
            }
        }

    We want to get rid of the 'element' middle-man and turn all
    list items into their proper representation:

    Zero results:
        {
            'items': []
        }

    One or more results:
        {
            'items': [
                ...,
                ...,
            ]
        }
    """
    ret = {}
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict):
                if k == 'element':
                    ret = resolve_element_list(v, list_keys=list_keys)
                else:
                    ret.setdefault(k, resolve_element_list(v, list_keys=list_keys))
            elif isinstance(v, list) and k == 'element':
                ret = v
            elif k in list_keys and v is None:
                ret = {k: []}
            else:
                ret.setdefault(k, v)
    else:
        ret = resolve_element_list(data, list_keys=list_keys)

    return ret
