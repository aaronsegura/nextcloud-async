# Changelog

## [Unreleased]

## [v1.0.0] - 2025-03-16

🔥🔥🔥 THIS VERSION IS NOT BACKWARDS COMPATIBLE 🔥🔥🔥

There have been major improvements in this version that I have been meaning to
get done for a long time. There is a laundry list of changes, but here are the
highlights:

- There are now individual modules for individual parts of the API.
- The NextCloudAsync client is DEPRECATED. It is replaced with NextcloudClient.
- There is now full coverage for the entire Talk API, amongst others.
- Better code structure makes your IDE happy.

Things are done fairly differently now. See the Documentation #TODO: LINK
or the README for a quick update.

### Changed

- NextCloudAsync is no longer a monolithic entryway to the entire system.
- Each Nextcloud API is its own module.

```python
  from nextcloud_async import NextcloudClient
  from nextcloud_async.api import Files, Users, Conversations

  nc = NextcloudClient(ENDPOINT, USER, PASSWORD)
  conversations_api = Conversations(nc)
  conversations = await conversations_api.list()
  for conversation in conversations:
      print(conversation.display_name)
```

### Added

- Full coverage of Talk API
- Support for app_token authentication
- Unit tests
- Integration tests with multiple versions of Nextcloud server
- Sphinx Documentation

### Deprecated

- NextCloudAsync

---

## Previous Releases

**v0.0.10**: <https://github.com/aaronsegura/nextcloud-async/compare/v0.0.9...v0.0.10>

**v0.0.9**: <https://github.com/aaronsegura/nextcloud-async/compare/v0.0.8...v0.0.9>

**v0.0.8**: <https://github.com/aaronsegura/nextcloud-async/compare/v0.0.7...v0.0.8>

**v0.0.7**: <https://github.com/aaronsegura/nextcloud-async/compare/v0.0.6...v0.0.7>

**v0.0.6**: <https://github.com/aaronsegura/nextcloud-async/compare/v0.0.5...v0.0.6>

**v0.0.5**: <https://github.com/aaronsegura/nextcloud-async/compare/v0.0.4...v0.0.5>

**v0.0.4**: <https://github.com/aaronsegura/nextcloud-async/compare/v0.0.3...v0.0.4>

**v0.0.3**: <https://github.com/aaronsegura/nextcloud-async/compare/v0.0.2...v0.0.3>

---

[[Keep a Changelog](https://keepachangelog.com/en/1.1.0/)]
