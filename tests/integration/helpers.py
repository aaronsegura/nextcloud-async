from nextcloud_async.api import FilesApi


async def create_remote_test_files(
    files_api: FilesApi,
    test_directory: str,
    local_test_file: str,
    name_base: str = "file",
    num_files: int = 1,
    network_blocked: bool = False,
) -> list[str]:
    ret = []
    for filenum in range(num_files):
        filename = f"{test_directory}/{name_base}{filenum}.md"
        if not network_blocked:
            await files_api.upload(local_test_file, filename)
        ret.append(filename)
    return ret
