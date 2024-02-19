## Structlogger Example

This demonstrates use of the prefab logging filter with standard logging.

`poetry install --no-root`

`poetry PREFAB_API_KEY=XXXXXXXX python structlogger-example.py`

### structlogger-example.py

Demonstrates subclassing LoggerProcessor to customize logger_name; in this case it'll use `module` added by `structlog.processors.CallsiteParameterAdder`

Contains a loop logging at different log levels - changing the log level of the `structlogger-example` (the module name) in the prefab UI or CLI will quickly affect which log lines are shown.

