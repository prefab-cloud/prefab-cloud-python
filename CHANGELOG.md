# Changelog

## Unreleased

- Adds full telemetry support - will (configurably) send data back to Prefab about evaluations, logging counts, and context usage
- Reliability changes, increased test coverage
- Remove automatic `structlog` configuration. Adds helper methods to use Prefab in customer-configured structlog [#40]
- Filter extracted for standard `logging` usage [#32]
- Added types on client [#28]
- Changed default collect_sync_interval from None to 30 seconds [#54]
- Added package methods to configure, manage and reset a singleton instance of the client [#53]
- Removed GRPC [#56]

## [0.9.0] - 2024-01-13

- Add support for reading config from a local JSON datafile [#42]
- Add support for setting and using default contexts [#43]
- Add support for encrypted config values [#44]

## [0.8.0] - 2024-01-12

- Add support for `provided` config values via ENV vars
- Add `ConfigValueWrapper`

## [0.7.0] - 2023-12-22

- Set and load from local cache when specified

## [0.6.0] - 2023-11-14

- Loosen version requirements to allow Python 3.9

## [0.5.1] - 2023-06-28

- Migrate from a direct dependency on `urllib3` to using `requests`

## [0.5.0] - 2023-06-24

- Add ContextShape and ContextShapeAggregator
- Rename LogPathCollector to LogPathAggregator

## [0.4.0] - 2023-06-24

- Better handling for non-valid yaml in YamlParser
- Switch to using https://buf.build/ for generating protos

## [0.3.3] - 2023-06-21

- Move `pytest` and `timecop` to dev dependencies
- Remove outdated call to `base_client.logger()`

## [0.3.2] - 2023-06-20

- Allow using latest urllib 1.x version to avoid forcing users to upgrade to urllib 2+

## [0.3.1] - 2023-06-12

- Ensure `LoggerClient.config_client` is not set until the config client has initialized successfully
- Log collection no longer ignores logs that would not be printed
- Fix bug in read/write locks in ConfigClient during initialization

## [0.3.0] - 2023-06-12

- First published release, includes:
  - Config
  - Feature flags
  - Logging
    - Log metrics
