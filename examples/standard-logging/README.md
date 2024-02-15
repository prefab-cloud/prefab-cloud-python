## Standard Logging

This demonstrates use of the prefab logging filter with standard logging. 


`poetry install --no-root`

`poetry PREFAB_API_KEY=XXXXXXXX python standard-logger-example.py`


### standard-logger-example.py

Contains a loop logging at different log levels - changing the log level of the `prefab.python.test.logger` in the prefab UI or CLI will quickly affect which log lines are shown.

Also demonstrates use of the `on_ready_callback` to add the logging filter and lower the global log level to debug


