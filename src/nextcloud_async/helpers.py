"""Helper functions for NextcloudAsync."""

from typing import Any, Awaitable, Callable, Dict, List
from urllib.parse import quote

import httpx

from nextcloud_async.api import NextcloudModule
from nextcloud_async.exceptions import NextcloudForbiddenError


def recursive_urlencode(d: Dict[str, Any]) -> str:
    """URL-encode a multidimensional dictionary PHP-style.

    https://stackoverflow.com/questions/4013838/urlencode-a-multidimensional-dictionary-in-python/4014164#4014164

    >>> data = {'a': 'b&c', 'd': {'e': {'fg': 'hi'}}, 'j': 'k'}
    >>> recursive_urlencode(data)
    'a=b%26c&d[e][fg]=hi&j=k'
    """

    def _recursion(d: Dict[str, str], base: List[str] = []) -> List[str]:
        pairs: List[str] = []

        for key, value in d.items():
            new_base: List[str] = base + [key]
            if hasattr(value, "values"):
                pairs += _recursion(value, new_base)  # type: ignore
            else:
                new_pair = None
                if len(new_base) > 1:
                    first = quote(new_base.pop(0))
                    rest = [quote(x) for x in new_base]
                    new_pair = f"{first}[{']['.join(rest)}]={quote(value)}"
                else:
                    new_pair = f"{quote(key)}={quote(value)}"
                pairs.append(new_pair)
        return pairs

    return "&".join(_recursion(d))


def bool2int(b: bool) -> int:
    """Translate boolean values to integers.

    Args:
        b:
            Boolean value

    Returns:
        0 if False, 1 if True

    """
    if not isinstance(b, bool):
        raise TypeError("Given value is not a boolean.")
    return 1 if b else 0


def bool2str(b: bool) -> str:
    """Translate a boolean value to string."""
    if not isinstance(b, bool):
        raise TypeError("Given value is not a boolean.")
    return "true" if b else "false"


def phone_number_to_e164(phone_number: str | int) -> str:
    """Translate phone number to E164 format.

    Args:
        phone_number:
            Phone number

    Returns:
        E164 phone number

    """
    if not any([isinstance(phone_number, int), isinstance(phone_number, str)]):
        raise TypeError("Phone number must be string or integer.")

    new_format: List[str] = []

    if isinstance(phone_number, int):
        phone_number = str(phone_number)

    for digit in reversed(phone_number):
        if digit not in list(map(str, range(10))):
            raise ValueError(f"Found unrecognized digit: {digit}")
        new_format.append(digit)

    return f"{'.'.join(new_format)}.e164.arpa"


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
    filter = [x.lower() for x in filter]
    return httpx.Headers([x for x in headers.items() if x[0] in filter])


def password_confirmation_required(
    func: Callable[..., Awaitable],
) -> Callable[..., Awaitable]:
    """Wrap certain calls because of stupid Nextcloud API shenanigans.

    https://github.com/nextcloud/server/issues/51391

    This is an async decorator and can be used inside of NextcloudModule classes to
    wrap functions that require periodic password confirmations in the nextcloud API.
    If the wrapped function raises a 403 error with "confirmation" in the `reason` field,
    cookies will be cleared and the call will be tried again.  Any further exceptions
    (or exceptions other than 403/confirmation) are raised to the caller.

    ````
    @password_confirmation_required
    async def create(self, ...):
        ...
    ````

    Args:
        func:
            Function to be wrapped.

    """

    async def _wrapper(
        self: NextcloudModule, *args: Any, **kwargs: dict[Any, Any]
    ) -> Any:
        try:
            return await func(self, *args, **kwargs)
        except NextcloudForbiddenError as e:
            if "confirmation" in str(e):
                self.api.client.http_client.cookies.delete("oc_sessionPassphrase")
                return await func(self, *args, **kwargs)
            else:
                raise

    return _wrapper
