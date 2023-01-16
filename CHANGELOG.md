# streamfield-migration-toolkit Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2023-01-16

### Added

- Generate migration names from operations (Sandil Ranasinghe)

### Changed

- Change `BaseBlockOperation` to be a subclass of `abc.ABC`
- Fix tests for Wagtail 4.1 and Django 4.1 (Matt Wescott)
- Improve child comparison when comparing blocks in autodetection (Sandil Ranasinghe)
- Refactor autodetection code and add caching (Sandil Ranasinghe)

## [0.1.0] - 2022-09-30

- Initial Release

## [Unreleased]

<!-- TEMPLATE - keep below to copy for new releases -->
<!--


## [x.y.z] - YYYY-MM-DD

### Added

- ...

### Changed

- ...

### Removed

- ...

-->