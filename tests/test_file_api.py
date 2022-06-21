
from .base import BaseTestCase
from .helpers import AsyncMock
from .constants import (
    USER, ENDPOINT, PASSWORD, FILE)

import asyncio
import httpx

from unittest.mock import patch, mock_open


class DAVFileAPI(BaseTestCase):

    def test_list_files(self):
        FILE = ''
        PROPS = ['oc:fileid', 'oc:size', 'nc:has-preview']
        RESPONSE_FILES = [
            {'d:href': f'/remote.php/dav/files/{USER}/Nextcloud%20Manual.pdf',
                'd:propstat': {
                    'd:prop': {
                        'nc:has-preview': 'false',
                        'oc:fileid': '2438295',
                        'oc:size': '5748633'},
                    'd:status': 'HTTP/1.1 200 OK'}},
            {'d:href': f'/remote.php/dav/files/{USER}/',
                'd:propstat': {
                    'd:prop': {
                        'nc:has-preview': 'false',
                        'oc:fileid': '2438276',
                        'oc:size': '137546371275'},
                    'd:status': 'HTTP/1.1 200 OK'}}]

        xml_response = '<?xml version="1.0"?>\n'\
            '<d:multistatus xmlns:d="DAV:" xmlns:s="http://sabredav.org/ns" '\
            'xmlns:oc="http://owncloud.org/ns" xmlns:nc="http://nextcloud.org/ns">'\
            f'<d:response><d:href>/remote.php/dav/files/{USER}/</d:href>'\
            '<d:propstat><d:prop><oc:fileid>2438276</oc:fileid>'\
            '<oc:size>137546371275</oc:size><nc:has-preview>false</nc:has-preview>'\
            '</d:prop><d:status>HTTP/1.1 200 OK</d:status>'\
            '</d:propstat></d:response><d:response>'\
            f'<d:href>/remote.php/dav/files/{USER}/Nextcloud%20Manual.pdf</d:href>'\
            '<d:propstat><d:prop><oc:fileid>2438295</oc:fileid>'\
            '<oc:size>5748633</oc:size><nc:has-preview>false</nc:has-preview>'\
            '</d:prop><d:status>HTTP/1.1 200 OK</d:status></d:propstat>'\
            '</d:response></d:multistatus>\n'
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=xml_response)) as mock:
            response = asyncio.run(self.ncc.list_files(FILE, PROPS))
            mock.assert_called_with(
                method='PROPFIND',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/remote.php/dav/files/{USER}/',
                data='<?xml version=\'1.0\' encoding=\'us-ascii\'?>\n<d:propfi'
                     'nd xmlns:d="DAV:" xmlns:oc="http://owncloud.org/ns" xmln'
                     's:nc="http://nextcloud.org/ns"><d:prop><oc:fileid /><oc:'
                     'size /><nc:has-preview /></d:prop></d:propfind>', headers={})
            assert isinstance(response, list)
            assert len(response) == 2

            for f in RESPONSE_FILES:
                assert f in response
                for p in PROPS:
                    assert p in f['d:propstat']['d:prop']

            assert len(response) == 2

    def test_download_file(self):
        FILE_CONTENTS = b'[File Contents]'
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=FILE_CONTENTS)) as mock:
            response = asyncio.run(self.ncc.download_file(FILE))
            mock.assert_called_with(
                method='GET',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/remote.php/dav/files/{USER}/{FILE}?',
                data=None,
                headers={})
            assert response == FILE_CONTENTS

    def test_upload_file(self):
        REMOTE_PATH = 'Documents/Somefile.md'
        LOCAL_PATH = FILE

        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content='')) as mock:
            with patch('builtins.open', mock_open(read_data='[File Contents]')) as m_open:
                asyncio.run(self.ncc.upload_file(LOCAL_PATH, REMOTE_PATH))

            mock.assert_called_with(
                method='PUT',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/remote.php/dav/files/{USER}/{REMOTE_PATH}',
                data='[File Contents]',
                headers={})
            m_open.assert_called_once_with(FILE, 'r')

    def test_create_folder(self):
        FOLDER = FILE

        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content='')) as mock:
            asyncio.run(self.ncc.create_folder(FOLDER))

            mock.assert_called_with(
                method='MKCOL',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/remote.php/dav/files/{USER}/{FOLDER}',
                data={},
                headers={})

    def test_delete(self):
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content='')) as mock:
            asyncio.run(self.ncc.delete(FILE))

            mock.assert_called_with(
                method='DELETE',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/remote.php/dav/files/{USER}/{FILE}',
                data={},
                headers={})

    def test_move(self):
        TO = f'{ENDPOINT}/remote.php/dav/files/{USER}/Documents/file.md'

        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content='')) as mock:
            asyncio.run(self.ncc.move(FILE, TO))

            mock.assert_called_with(
                method='MOVE',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/remote.php/dav/files/{USER}/{FILE}',
                data={},
                headers={
                    'Destination': f'{ENDPOINT}/remote.php/dav/files/{USER}'
                    f'/https://cloud.example.com/remote.php/dav/files/dk/Documents/file.md',
                    'Overwrite': 'T'})

    def test_copy(self):
        FROM = 'file.md'
        TO = f'{ENDPOINT}/remote.php/dav/files/{USER}/Documents/file.md'

        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content='')) as mock:
            asyncio.run(self.ncc.copy(FROM, TO))

            mock.assert_called_with(
                method='COPY',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/remote.php/dav/files/{USER}/{FROM}',
                data={},
                headers={
                    'Destination': f'{ENDPOINT}/remote.php/dav/files/{USER}'
                    f'/https://cloud.example.com/remote.php/dav/files/dk/Documents/file.md',
                    'Overwrite': 'F'})

    def test_remove_favorite(self):
        xml_response = '<?xml version="1.0"?>\n<d:multistatus xmlns:d="DAV:" '\
            'xmlns:s="http://sabredav.org/ns" xmlns:oc="http://owncloud.org/ns" '\
            'xmlns:nc="http://nextcloud.org/ns"><d:response>'\
            f'<d:href>/remote.php/dav/files/{USER}/{FILE}</d:href><d:propstat>'\
            '<d:prop><oc:favorite/></d:prop><d:status>HTTP/1.1 200 OK</d:status>'\
            '</d:propstat></d:response></d:multistatus>'
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=xml_response)) as mock:
            response = asyncio.run(self.ncc.remove_favorite(FILE))
            mock.assert_called_with(
                method='PROPPATCH',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/remote.php/dav/files/{USER}/{FILE}',
                data='<?xml version="1.0"?>\n                <d:propertyupdate\n'
                     '                    xmlns:d="DAV:"\n                    xm'
                     'lns:oc="http://owncloud.org/ns">\n                <d:set><'
                     'd:prop>\n                <oc:favorite>0</oc:favorite>\n   '
                     '             </d:prop></d:set></d:propertyupdate>\n        ',
                headers={})
            assert response == {
                'd:href': f'/remote.php/dav/files/{USER}/{FILE}',
                'd:propstat': {
                    'd:prop': {
                        'oc:favorite': None},
                    'd:status': 'HTTP/1.1 200 OK'}}

    def test_set_favorite(self):
        xml_response = f"""<?xml version="1.0"?>\n<d:multistatus xmlns:d="DAV:"
        xmlns:s="http://sabredav.org/ns" xmlns:oc="http://owncloud.org/ns"
        xmlns:nc="http://nextcloud.org/ns"><d:response>
        <d:href>/remote.php/dav/files/{USER}/{FILE}</d:href><d:propstat>
        <d:prop><oc:favorite/></d:prop><d:status>HTTP/1.1 200 OK</d:status>
        </d:propstat></d:response></d:multistatus>"""
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=xml_response)) as mock:
            response = asyncio.run(self.ncc.set_favorite(FILE))
            mock.assert_called_with(
                method='PROPPATCH',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/remote.php/dav/files/{USER}/{FILE}',
                data='<?xml version="1.0"?>\n'
                     '                <d:propertyupdate\n'
                     '                    xmlns:d="DAV:"\n'
                     '                    xmlns:oc="http://owncloud.org/ns">\n'
                     '                <d:set><d:prop>\n'
                     '                <oc:favorite>1</oc:favorite>\n'
                     '                </d:prop></d:set></d:propertyupdate>\n'
                     '        ',
                headers={})
            assert response == {
                'd:href': f'/remote.php/dav/files/{USER}/{FILE}',
                'd:propstat': {
                    'd:prop': {
                        'oc:favorite': None},
                    'd:status': 'HTTP/1.1 200 OK'}}

    def test_get_favorites(self):
        xml_response = '<?xml version="1.0"?>\n'\
            '<d:multistatus xmlns:d="DAV:" xmlns:s="http://sabredav.org/ns" xmlns:'\
            'oc="http://owncloud.org/ns" xmlns:nc="http://nextcloud.org/ns">\n <d:'\
            'response>\n  <d:status>HTTP/1.1 200 OK</d:status>\n  <d:href>/remote.'\
            f'php/dav/files/{FILE}</d:href>\n  <d:propstat>\n'\
            '   <d:prop/>\n   <d:status>HTTP/1.1 418 I\'m a teapot</d:status>\n  <'\
            '/d:propstat>\n </d:response>\n <d:response>\n  <d:status>HTTP/1.1 200'\
            f' OK</d:status>\n  <d:href>/remote.php/dav/files/{USER}/{FILE}</d:href'\
            '>\n  <d:propstat>\n   <d:prop/>\n   <d:status>HTTP/1.1 418 I\'m a tea'\
            'pot</d:status>\n  </d:propstat>\n </d:response>\n</d:multistatus>\n'
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=xml_response)) as mock:
            response = asyncio.run(self.ncc.get_favorites())
            mock.assert_called_with(
                method='REPORT',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/remote.php/dav/files/{USER}/',
                data='<?xml version="1.0"?><oc:filter-files  xmlns:d="DAV:"\n'
                    '        xmlns:oc="http://owncloud.org/ns" xmlns:nc="http'
                    '://nextcloud.org/ns">\n        <oc:filter-rules><oc:favo'
                    'rite>1</oc:favorite></oc:filter-rules>\n        </oc:fil'
                    'ter-files>', headers={})
            assert {
                'd:status': 'HTTP/1.1 200 OK',
                'd:href': f'/remote.php/dav/files/{USER}/{FILE}',
                'd:propstat': {
                    'd:prop': None,
                    'd:status': "HTTP/1.1 418 I'm a teapot"}} in response

    def test_get_trashbin(self):
        xml_response = '<?xml version="1.0"?>\n<d:multistatus xmlns:d="DAV:" '\
            'xmlns:s="http://sabredav.org/ns" xmlns:oc="http://owncloud.org/ns" x'\
            'mlns:nc="http://nextcloud.org/ns"><d:response><d:href>/remote.php/da'\
            f'v/trashbin/{USER}/trash/</d:href><d:propstat><d:prop><d:resourcetyp'\
            'e><d:collection/></d:resourcetype></d:prop><d:status>HTTP/1.1 200 OK'\
            '</d:status></d:propstat></d:response><d:response><d:href>/remote.php'\
            f'/dav/trashbin/{USER}/trash/{FILE}.d1655760269</d:href><d:propstat><'\
            'd:prop><d:getlastmodified>Mon, 20 Jun 2022 21:24:29 GMT</d:getlastmo'\
            'dified><d:getcontentlength>0</d:getcontentlength><d:resourcetype/><d'\
            ':getetag>1655760269</d:getetag><d:getcontenttype>text/markdown</d:ge'\
            'tcontenttype></d:prop><d:status>HTTP/1.1 200 OK</d:status></d:propst'\
            'at><d:propstat><d:prop><d:quota-used-bytes/><d:quota-available-bytes'\
            '/></d:prop><d:status>HTTP/1.1 404 Not Found</d:status></d:propstat><'\
            '/d:response></d:multistatus>\n'
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=xml_response)) as mock:
            response = asyncio.run(self.ncc.get_trashbin())
            mock.assert_called_with(
                method='PROPFIND',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/remote.php/dav/trashbin/{USER}/trash',
                data={}, headers={})

            assert {
                'd:href': f'/remote.php/dav/trashbin/{USER}/trash/{FILE}.d1655760269',
                'd:propstat': [
                    {
                        'd:prop': {
                            'd:getlastmodified': 'Mon, 20 Jun 2022 21:24:29 GMT',
                            'd:getcontentlength': '0',
                            'd:resourcetype': None,
                            'd:getetag': '1655760269',
                            'd:getcontenttype': 'text/markdown'},
                        'd:status': 'HTTP/1.1 200 OK'},
                    {
                        'd:prop': {
                            'd:quota-used-bytes': None,
                            'd:quota-available-bytes': None},
                        'd:status': 'HTTP/1.1 404 Not Found'}]} in response

    def test_restore_from_trashbin(self):
        TRASH_FILE = f'{ENDPOINT}/remote.php/dav/trashbin/{USER}/trash/{FILE}.d1655760269'

        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content='')) as mock:
            asyncio.run(self.ncc.restore_from_trashbin(
                f'/remote.php/dav/trashbin/{USER}/trash/{FILE}.d1655760269'))

            mock.assert_called_with(
                method='MOVE',
                auth=(USER, PASSWORD),
                url=TRASH_FILE,
                data={},
                headers={
                    'Destination': f'{ENDPOINT}/remote.php/dav/trashbin/{USER}/restore/file'})

    def test_empty_trash(self):
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content='')) as mock:
            asyncio.run(self.ncc.empty_trashbin())

            mock.assert_called_with(
                method='DELETE',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/remote.php/dav/trashbin/{USER}/trash',
                data={},
                headers={})

    def test_get_file_versions(self):
        xml_response = '<?xml version="1.0"?>\n<d:multistatus xmlns:d="DAV:" x'\
            'mlns:s="http://sabredav.org/ns" xmlns:oc="http://owncloud.org/ns'\
            '" xmlns:nc="http://nextcloud.org/ns"><d:response><d:href>/remote'\
            f'.php/dav/files/{USER}/{FILE}</d:href><d:propstat><d:prop><oc:fi'\
            'leid>2875527</oc:fileid></d:prop><d:status>HTTP/1.1 200 OK</d:st'\
            'atus></d:propstat></d:response></d:multistatus>\n'
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=xml_response)) as mock:
            asyncio.run(self.ncc.get_file_versions(FILE))

            mock.assert_called_with(
                method='PROPFIND',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}/remote.php/dav/versions/{USER}/versions/2875527',
                data={},
                headers={})

    def test_restore_file_version(self):
        xml_response = ''
        FILE = f'/remote.php/dav/versions/{USER}/versions/2875527/1655762900'
        with patch(
                'httpx.AsyncClient.request',
                new_callable=AsyncMock,
                return_value=httpx.Response(
                    status_code=200,
                    content=xml_response)) as mock:
            asyncio.run(self.ncc.restore_file_version(FILE))

            mock.assert_called_with(
                method='MOVE',
                auth=(USER, PASSWORD),
                url=f'{ENDPOINT}{FILE}',
                data={},
                headers={
                    'Destination':
                        f'{ENDPOINT}/remote.php/dav/versions/{USER}/restore/file'})

    def test_upload_file_chunked(self):
        # TODO: ^-this-v
        pass
