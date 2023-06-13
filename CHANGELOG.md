# Changelog

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
