USER = 'dk'
NAME = 'Darren King'
PASSWORD = 'RIP MUTEMATH'
EMAIL = 'IAmATree@GuidedByVoices.com'
FILE = 'MatthewSweet.md'

ENDPOINT = 'https://cloud.example.com'

EMPTY_100 = bytes(
    '{"ocs":{"meta":{"status":"ok","statuscode":100,"message":"OK",'
    '"totalitems":"","itemsperpage":""},"data":[]}}', 'utf-8')

EMPTY_200 = bytes(
    '{"ocs":{"meta":{"status":"ok","statuscode":200,"message":"OK",'
    '"totalitems":"","itemsperpage":""},"data":[]}}', 'utf-8')

SIMPLE_100 = '{{"ocs":{{"meta":{{"status":"ok","statuscode":100,"message":"OK",'\
    '"totalitems":"","itemsperpage":""}},"data": {0} }}}}'
