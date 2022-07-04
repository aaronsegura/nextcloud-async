
from unittest import TestCase

from nextcloud_async.helpers import (
    recursive_urlencode,
    resolve_element_list)


class TestHelpers(TestCase):

    def test_recursive_urlencode_nested_dict(self):
        a = {'configData': {'key1': 'val1', 'key2': 'val2'}}
        r = recursive_urlencode(a)
        assert r == 'configData[key1]=val1&configData[key2]=val2'

    def test_resolve_element_list(self):
        KEY = 'apps'
        EMPTY_ANSWER = []
        SINGLE_ANSWER = ['workflow_script']
        MULTI_ANSWER = ['workflow_script', 'epubreader']

        response_multi = {
            'ocs': {
                'meta': {
                    'status': 'ok',
                    'statuscode': '100',
                    'message': 'OK',
                    'totalitems': None,
                    'itemsperpage': None},
                'data': {
                    KEY: {
                        'element': MULTI_ANSWER}}}}
        result_multi = resolve_element_list(response_multi, list_keys=[KEY])
        assert result_multi['ocs']['data'][KEY] == MULTI_ANSWER

        response_single = {
            'ocs': {
                'meta': {
                    'status': 'ok',
                    'statuscode': '100',
                    'message': 'OK',
                    'totalitems': None,
                    'itemsperpage': None},
                'data': {
                    KEY: {
                        'element': SINGLE_ANSWER}}}}
        result_single = resolve_element_list(response_single, list_keys=[KEY])
        assert result_single['ocs']['data'][KEY] == SINGLE_ANSWER

        response_empty = {
            'ocs': {
                'meta': {
                    'status': 'ok',
                    'statuscode': '100',
                    'message': 'OK',
                    'totalitems': None,
                    'itemsperpage': None},
                'data': {
                    KEY: {
                        'element': EMPTY_ANSWER}}}}
        result_empty = resolve_element_list(response_empty, list_keys=[KEY])
        assert result_empty['ocs']['data'][KEY] == EMPTY_ANSWER
