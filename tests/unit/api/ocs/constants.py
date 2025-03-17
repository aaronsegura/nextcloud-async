from ....constants import ENDPOINT, PASSWORD, USER

GET_RESPONSE = {
    "ocs": {
        "meta": {
            "status": "ok",
            "statuscode": 100,
            "message": "OK",
            "totalitems": "",
            "itemsperpage": "",
        },
        "data": {
            "id": 972,
            "mount_point": "/.nextcloud-async-pytest/groupfolders/groupfolder_0",
            "groups": [],
            "quota": -3,
            "size": 0,
            "acl": False,
            "manage": [],
            "group_details": [],
        },
    }
}

LIST_RESPONSE = {
    "ocs": {
        "meta": {
            "status": "ok",
            "statuscode": 100,
            "message": "OK",
            "totalitems": "",
            "itemsperpage": "",
        },
        "data": {
            "938": {
                "id": 938,
                "mount_point": "test",
                "groups": [],
                "quota": -3,
                "size": 0,
                "acl": False,
                "manage": [],
                "group_details": [],
            },
            "1032": {
                "id": 1032,
                "mount_point": "/.nextcloud-async-pytest/groupfolders/groupfolder_0",
                "groups": [],
                "quota": -3,
                "size": 0,
                "acl": False,
                "manage": [],
                "group_details": [],
            },
            "1033": {
                "id": 1033,
                "mount_point": "/.nextcloud-async-pytest/groupfolders/groupfolder_1",
                "groups": [],
                "quota": -3,
                "size": 0,
                "acl": False,
                "manage": [],
                "group_details": [],
            },
            "1034": {
                "id": 1034,
                "mount_point": "/.nextcloud-async-pytest/groupfolders/groupfolder_2",
                "groups": [],
                "quota": -3,
                "size": 0,
                "acl": False,
                "manage": [],
                "group_details": [],
            },
        },
    }
}
