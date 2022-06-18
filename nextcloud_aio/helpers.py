import urllib


def recursive_urlencode(d):
    """
    URL-encode a multidimensional dictionary PHP-style.

    https://stackoverflow.com/questions/4013838/urlencode-a-multidimensional-dictionary-in-python/4014164#4014164

    Updated for python3.

    >>> data = {'a': 'b&c', 'd': {'e': {'f&g': 'h*i'}}, 'j': 'k'}
    >>> recursive_urlencode(data)
    u'a=b%26c&j=k&d[e][f%26g]=h%2Ai'
    """
    def recursion(d, base=[]):
        pairs = []

        for key, value in d.items():
            new_base = base + [key]
            if hasattr(value, 'values'):
                pairs += recursion(value, new_base)
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

    return '&'.join(recursion(d))
