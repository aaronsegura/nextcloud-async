"""Test Nextcloud Activity API

Reference:
    https://github.com/nextcloud/activity/blob/master/docs/endpoint-v2.md
"""

from .base import BaseTestCase
from .helpers import AsyncMock
from .constants import USER, ENDPOINT, PASSWORD

import asyncio
import httpx

from urllib.parse import urlencode
from unittest.mock import patch


class OCSGeneralAPI(BaseTestCase):  # noqa: D101

    def test_get_activity(self):  # noqa: D102
        OBJ_ID = 30
        OBJ_TYPE = 'files'
        SINCE = 0
        LIMIT = 3
        OFFSET = 0
        SORT = 'desc'
        json_response = bytes(
            '{"ocs":{"meta":{"status":"ok","statuscode":200,"message":"OK"},'
            '"data":[{"activity_id":43,"app":"files_sharing","type":"shared",'
            f'"user":"{USER}","subject":"Shared with Test User","subject_rich'
            f'":["Shared with {{user}}",{{"file":{{"type":"file","id":"{OBJ_ID}'
            '","name":"Nextcloud Manual.pdf","path":"Nextcloud Manual.pdf","l'
            'ink":"http:\\/\\/localhost:8181\\/f\\/30"},"user":{"type":"user"'
            ',"id":"testuser","name":"Test User"}}],"message":"","message_ric'
            f'h":["",[]],"object_type":"files","object_id":{OBJ_ID},"object_n'
            f'ame":"\\/Nextcloud Manual.pdf","objects":{{"{OBJ_ID}":"\\/Nextc'
            'loud Manual.pdf"},"link":"http:\\/\\/localhost:8181\\/apps\\/fil'
            'es\\/?dir=\\/","icon":"http:\\/\\/localhost:8181\\/core\\/img\\/'
            'actions\\/share.svg","datetime":"2022-06-24T18:11:11+00:00"}]}}',
            'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=json_response)) as mock:
            asyncio.run(self.ncc.get_activity(
                since=SINCE, limit=LIMIT, filter_object=OBJ_ID, filter_object_type=OBJ_TYPE))
            url_data = urlencode({
                'object_type': OBJ_TYPE,
                'object_id': OBJ_ID,
                'limit': LIMIT,
                'sort': SORT,
                'since': SINCE,
                'offset': OFFSET,
                'format': 'json'
            })
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/ocs/v2.php/apps/activity/api/v2/activity/filter?{url_data}',
                data=None,
                headers={'OCS-APIRequest': 'true'})

    def test_get_file_guest_link(self):
        FILE_ID = 30
        json_response = bytes(
            '{"ocs":{"meta":{"status":"ok","statuscode":200,"message":"OK"},'
            '"data":{"url":"http:\\/\\/localhost:8181\\/remote.php\\/direct'
            '\\/HAMSci2FPfdZEtetn7XwtgxVsd17GdRMbQWchMK93QRDaEFxP8bZW2EgSVtR"}}}', 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=json_response)) as mock:
            asyncio.run(self.ncc.get_file_guest_link(FILE_ID))
        mock.assert_called_with(
            method='POST',
            auth=(USER, PASSWORD),
            url=f'{ENDPOINT}/ocs/v2.php/apps/dav/api/v1/direct',
            data={'fileId': FILE_ID, 'format': 'json'},
            headers={'OCS-APIRequest': 'true'})

    def test_get_capabilities(self):
        json_response = bytes(
            '{"ocs":{"meta":{"status":"ok","statuscode":100,"message":"OK","t'
            'otalitems":"","itemsperpage":""},"data":{"version":{"major":24,"'
            'minor":0,"micro":1,"string":"24.0.1","edition":"","extendedSuppo'
            'rt":false},"capabilities":{"core":{"pollinterval":60,"webdav-roo'
            't":"remote.php\\/webdav"},"bruteforce":{"delay":0},"metadataAvai'
            'lable":{"size":["\\/image\\\\\\/.*\\/"]},"files":{"bigfilechunki'
            'ng":true,"blacklisted_files":[".htaccess"],"directEditing":{"url'
            '":"http:\\/\\/localhost:8181\\/ocs\\/v2.php\\/apps\\/files\\/api'
            '\\/v1\\/directEditing","etag":"c748e8fc588b54fc5af38c4481a19d20"'
            '},"comments":true,"undelete":true,"versioning":true},"activity":'
            '{"apiv2":["filters","filters-api","previews","rich-strings"]},"c'
            'ircles":{"version":"24.0.0","status":{"globalScale":false},"sett'
            'ings":{"frontendEnabled":true,"allowedCircles":262143,"allowedUs'
            'erTypes":31,"membersLimit":-1},"circle":{"constants":{"flags":{"'
            '1":"Single","2":"Personal","4":"System","8":"Visible","16":"Open'
            '","32":"Invite","64":"Join Request","128":"Friends","256":"Passw'
            'ord Protected","512":"No Owner","1024":"Hidden","2048":"Backend"'
            ',"4096":"Local","8192":"Root","16384":"Circle Invite","32768":"F'
            'ederated","65536":"Mount point"},"source":{"core":{"1":"Nextclou'
            'd User","2":"Nextcloud Group","4":"Email Address","8":"Contact",'
            '"16":"Circle","10000":"Nextcloud App"},"extra":{"10001":"Circles'
            ' App","10002":"Admin Command Line"}}},"config":{"coreFlags":[1,2'
            ',4],"systemFlags":[512,1024,2048]}},"member":{"constants":{"leve'
            'l":{"1":"Member","4":"Moderator","8":"Admin","9":"Owner"}},"type'
            '":{"0":"single","1":"user","2":"group","4":"mail","8":"contact",'
            '"16":"circle","10000":"app"}}},"ocm":{"enabled":true,"apiVersion'
            '":"1.0-proposal1","endPoint":"http:\\/\\/localhost:8181\\/ocm","'
            'resourceTypes":[{"name":"file","shareTypes":["user","group"],"pr'
            'otocols":{"webdav":"\\/public.php\\/webdav\\/"}}]},"dav":{"chunk'
            'ing":"1.0"},"files_sharing":{"api_enabled":true,"public":{"enabl'
            'ed":true,"password":{"enforced":false,"askForOptionalPassword":f'
            'alse},"expire_date":{"enabled":false},"multiple_links":true,"exp'
            'ire_date_internal":{"enabled":false},"expire_date_remote":{"enab'
            'led":false},"send_mail":false,"upload":true,"upload_files_drop":'
            'true},"resharing":true,"user":{"send_mail":false,"expire_date":{'
            '"enabled":true}},"group_sharing":true,"group":{"enabled":true,"e'
            'xpire_date":{"enabled":true}},"default_permissions":31,"federati'
            'on":{"outgoing":true,"incoming":true,"expire_date":{"enabled":tr'
            'ue},"expire_date_supported":{"enabled":true}},"sharee":{"query_l'
            'ookup_default":false,"always_show_unique":true},"sharebymail":{"'
            'enabled":true,"send_password_by_mail":true,"upload_files_drop":{'
            '"enabled":true},"password":{"enabled":true,"enforced":false},"ex'
            'pire_date":{"enabled":true,"enforced":false}}},"notifications":{'
            '"ocs-endpoints":["list","get","delete","delete-all","icons","ric'
            'h-strings","action-web","user-status"],"push":["devices","object'
            '-data","delete"],"admin-notifications":["ocs","cli"]},"password_'
            'policy":{"minLength":10,"enforceNonCommonPassword":true,"enforce'
            'NumericCharacters":false,"enforceSpecialCharacters":false,"enfor'
            'ceUpperLowerCase":false,"api":{"generate":"http:\\/\\/localhost:'
            '8181\\/ocs\\/v2.php\\/apps\\/password_policy\\/api\\/v1\\/genera'
            'te","validate":"http:\\/\\/localhost:8181\\/ocs\\/v2.php\\/apps'
            '\\/password_policy\\/api\\/v1\\/validate"}},"provisioning_api":'
            '{"version":"1.14.0","AccountPropertyScopesVersion":2,"AccountPro'
            'pertyScopesFederatedEnabled":true,"AccountPropertyScopesPublishe'
            'dEnabled":true},"spreed":{"features":["audio","video","chat-v2",'
            '"conversation-v4","guest-signaling","empty-group-room","guest-di'
            'splay-names","multi-room-users","favorites","last-room-activity"'
            ',"no-ping","system-messages","delete-messages","mention-flag","i'
            'n-call-flags","conversation-call-flags","notification-levels","i'
            'nvite-groups-and-mails","locked-one-to-one-rooms","read-only-roo'
            'ms","listable-rooms","chat-read-marker","chat-unread","webinary-'
            'lobby","start-call-flag","chat-replies","circles-support","force'
            '-mute","sip-support","chat-read-status","phonebook-search","rais'
            'e-hand","room-description","rich-object-sharing","temp-user-avat'
            'ar-api","geo-location-sharing","voice-message-sharing","signalin'
            'g-v3","publishing-permissions","clear-history","direct-mention-f'
            'lag","notification-calls","conversation-permissions","rich-objec'
            't-list-media","rich-object-delete","reactions"],"config":{"attac'
            'hments":{"allowed":true,"folder":"\\/Talk"},"chat":{"max-length"'
            ':32000,"read-privacy":0},"conversations":{"can-create":true},"pr'
            'eviews":{"max-gif-size":3145728}}},"theming":{"name":"Nextcloud"'
            ',"url":"https:\\/\\/nextcloud.com","slogan":"a safe home for all'
            ' your data","color":"#0082c9","color-text":"#ffffff","color-elem'
            'ent":"#0082c9","color-element-bright":"#0082c9","color-element-d'
            'ark":"#0082c9","logo":"http:\\/\\/localhost:8181\\/core\\/img\\/'
            'logo\\/logo.svg?v=0","background":"http:\\/\\/localhost:8181\\/c'
            'ore\\/img\\/background.png?v=0","background-plain":false,"backgr'
            'ound-default":true,"logoheader":"http:\\/\\/localhost:8181\\/cor'
            'e\\/img\\/logo\\/logo.svg?v=0","favicon":"http:\\/\\/localhost:8'
            '181\\/core\\/img\\/logo\\/logo.svg?v=0"},"user_status":{"enabled'
            '":true,"supports_emoji":true},"weather_status":{"enabled":true}}}}}', 'utf-8')
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=json_response)) as mock:
            asyncio.run(self.ncc.get_capabilities())
        mock.assert_called_with(
            method='GET',
            auth=(USER, PASSWORD),
            url=f'{ENDPOINT}/ocs/v1.php/cloud/capabilities?format=json',
            data=None,
            headers={'OCS-APIRequest': 'true'})