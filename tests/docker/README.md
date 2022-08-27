# Docker things

## ---- Deprecated ----

Borrowed, hacked, and mangled from https://github.com/luffah/nextcloud-API

These are here to facilitate quick setup of docker nextcloud containers.

    $ vi source .env

Set your desired NEXTCLOUD_VERSION and GROUPFOLDERS_VERSION if you want
to use Group Folders.  Also make sure NEXTCLOUD_PORT is available for use.

    $ source .env
    $ docker-compose -d up

You can now access your nextcloud on http://localhost:${NEXTCLOUD_PORT}/
