from nextcloud_async.helpers import recursive_urlencode


class TestHelpers:

    def test_recursive_urlencode_nested_dict(self):
        a = {"configData": {"key1": "val1", "key2": "val2"}}
        r = recursive_urlencode(a)
        assert r == "configData[key1]=val1&configData[key2]=val2"
