from nextcloud_async.api import Files
from nextcloud_async.exceptions import NextcloudMethodNotAllowedError


async def create_clean_test_directory(files_api: Files, dirpath: str) -> None:
    try:
        await files_api.mkdir(dirpath)
    except NextcloudMethodNotAllowedError:
        await files_api.delete(dirpath)
        await files_api.mkdir(dirpath)


async def create_remote_test_files(
    files_api: Files,
    test_directory: str,
    local_test_file: str,
    name_base: str = "file",
    num_files: int = 1,
    network_blocked: bool = False,
) -> list[str]:
    ret = []
    for filenum in range(0, num_files):
        filename = f"{test_directory}/{name_base}{filenum}.md"
        if not network_blocked:
            await files_api.upload(local_test_file, filename)
        ret.append(filename)
    return ret
