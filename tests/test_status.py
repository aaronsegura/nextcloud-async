# noqa: D100

from nextcloud_async.api.ocs.status import StatusType as ST

from .base import BaseTestCase
from .helpers import AsyncMock
from .constants import USER, ENDPOINT, PASSWORD, EMPTY_200

import asyncio
import httpx
import datetime as dt

from unittest.mock import patch

CLEAR_AT = (dt.datetime.now() + dt.timedelta(seconds=300)).timestamp()


class OCSStatusAPI(BaseTestCase):  # noqa: D101

    def test_get_status(self):  # noqa: D102
        json_response = bytes(
            '{"ocs":{"meta":{"status":"ok","statuscode":200,"message":"OK"},'
            f'"data":{{"userId":"{USER}","message":null,"messageId":null,"mes'
            'sageIsPredefined":false,"icon":null,"clearAt":null,"status":"awa'
            'y","statusIsUserDefined":false}}}', 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=json_response)) as mock:
            asyncio.run(self.ncc.get_status())
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v2.php/apps/user_status/api/v1/user_status?format=json',
                data=None,
                headers={'OCS-APIRequest': 'true'})

    def test_set_status(self):  # noqa: D102
        STATUS = ST['away']
        json_response = bytes(
            '{"ocs":{"meta":{"status":"ok","statuscode":200,"message":"OK"},'
            f'"data":{{"userId":"{USER}","message":null,"messageId":null,"mes'
            'sageIsPredefined":false,"icon":null,"clearAt":null,"status":'
            f'"{STATUS.name}","statusIsUserDefined":true}}}}}}', 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=json_response)) as mock:
            asyncio.run(self.ncc.set_status(STATUS))
            mock.assert_called_with(
                method='PUT',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v2.php/apps/user_status/api/v1/user_status/status',
                data={'format': 'json', 'statusType': STATUS.name},
                headers={'OCS-APIRequest': 'true'})

    def test_get_predefined_statuses(self):  # noqa: D102
        json_response = bytes(
            '{"ocs":{"meta":{"status":"ok","statuscode":200,"message":"OK"},'
            '"data":[{"id":"meeting","icon":"\\ud83d\\udcc5","message":"In a '
            'meeting","clearAt":{"type":"period","time":3600}},{"id":"commuti'
            'ng","icon":"\\ud83d\\ude8c","message":"Commuting","clearAt":{"ty'
            'pe":"period","time":1800}},{"id":"remote-work","icon":"\\ud83c\\'
            'udfe1","message":"Working remotely","clearAt":{"type":"end-of","'
            'time":"day"}},{"id":"sick-leave","icon":"\\ud83e\\udd12","messag'
            'e":"Out sick","clearAt":{"type":"end-of","time":"day"}},{"id":"v'
            'acationing","icon":"\\ud83c\\udf34","message":"Vacationing","cle'
            'arAt":null}]}}', 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=json_response)) as mock:
            asyncio.run(self.ncc.get_predefined_statuses())
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v2.php/apps/user_status/api/v1/predefined_statuses?'
                    'format=json',
                data=None,
                headers={'OCS-APIRequest': 'true'})

    def test_choose_predefined_status(self):  # noqa: D102
        MESSAGEID = 'meeting'

        json_response = bytes(
            '{"ocs":{"meta":{"status":"ok","statuscode":200,"message":"OK"},'
            f'"data":{{"userId":"{USER}","message":null,"messageId":"{MESSAGEID}"'
            f',"messageIsPredefined":true,"icon":null,"clearAt":{CLEAR_AT},"statu'
            's":"away","statusIsUserDefined":true}}}', 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=json_response)) as mock:
            asyncio.run(self.ncc.choose_predefined_status(MESSAGEID, CLEAR_AT))
            mock.assert_called_with(
                method='PUT',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v2.php/apps/user_status/api/v1'
                    '/user_status/message/predefined',
                data={'format': 'json', 'messageId': MESSAGEID, 'clearAt': CLEAR_AT},
                headers={'OCS-APIRequest': 'true'})

    def test_set_status_message(self):  # noqa: D102
        MESSAGE = 'Stinkfist'
        json_response = bytes(
            '{"ocs":{"meta":{"status":"ok","statuscode":200,"message":"OK"},'
            f'"data":{{"userId":"admin","message":"{MESSAGE}","messageId":nul'
            f'l,"messageIsPredefined":false,"icon":null,"clearAt":{CLEAR_AT},'
            '"status":"away","statusIsUserDefined":true}}}', 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=json_response)) as mock:
            asyncio.run(self.ncc.set_status_message(MESSAGE, clear_at=CLEAR_AT))
            mock.assert_called_with(
                method='PUT',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v2.php/apps/user_status/api/v1'
                    '/user_status/message/custom',
                data={'format': 'json', 'message': MESSAGE, 'clearAt': CLEAR_AT},
                headers={'OCS-APIRequest': 'true'})

    def test_clear_status_message(self):  # noqa: D102
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=EMPTY_200)) as mock:
            asyncio.run(self.ncc.clear_status_message())
            mock.assert_called_with(
                method='DELETE',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v2.php/apps/user_status/api/v1/user_status/message',
                data={'format': 'json'},
                headers={'OCS-APIRequest': 'true'})

    def test_get_all_user_statuses(self):  # noqa: D102
        json_response = bytes(
            '{"ocs":{"meta":{"status":"ok","statuscode":200,"message":"OK"},'
            f'"data":[{{"userId":"{USER}","message":null,"icon":null,"clearA'
            't":null,"status":"away"}]}}', 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=json_response)) as mock:
            asyncio.run(self.ncc.get_all_user_statuses())
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v2.php/apps/user_status/api/v1/statuses?'
                    'limit=100&offset=0&format=json',
                data=None,
                headers={'OCS-APIRequest': 'true'})

    def test_get_user_status(self):  # noqa: D102
        json_response = bytes(
            '{"ocs":{"meta":{"status":"ok","statuscode":200,"message":"OK"},'
            f'"data":{{"userId":"{USER}","message":null,"icon":null,"clearAt"'
            ':null,"status":"away"}}}', 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=json_response)) as mock:
            response = asyncio.run(self.ncc.get_user_status(USER))
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v2.php/apps/user_status/api/v1/statuses/{USER}'
                '?format=json',
                data=None,
                headers={'OCS-APIRequest': 'true'})
            assert response['userId'] == USER
