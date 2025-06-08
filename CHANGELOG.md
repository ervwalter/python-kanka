# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Documentation
- Added documentation for using Kanka's native `lastSync` parameter with the list() method
- Added example showing how to use lastSync for efficient synchronization in API_REFERENCE.md

## [2.0.0] - 2025-06-04

### Added
- Initial release of modern Python client for Kanka API
- Support for 12 core Kanka entity types: Calendar, Character, Creature, Event, Family, Journal, Location, Note, Organisation, Quest, Race, Tag
- Type-safe models using Pydantic v2
- Comprehensive error handling with specific exception types
- Automatic rate limiting with exponential backoff
- Entity posts/comments management
- Advanced filtering and search capabilities
- Built-in pagination handling
- Full integration test suite
- Comprehensive documentation and examples

## Acknowledgments

This project was originally inspired by [Kathrin Weihe's python-kanka](https://github.com/rbtnx/python-kanka). Thank you to Kathrin for the foundation and inspiration.
