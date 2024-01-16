# prefab-cloud-python

Python client for prefab.cloud, providing Config, FeatureFlags as a Service

**Note: This library is under active development**

[Sign up to be notified about updates](https://forms.gle/2qsjMFvjGnkTnA9T8)

## Example usage

```python
from prefab_cloud_python import Client, Options

options = Options(
    prefab_api_key="your-prefab-api-key"
)

context = {
  "user": {
    "team_id": 432,
    "id": 123,
    "subscription_level": 'pro',
    "email": "alice@example.com"
  }
}

client = Client(options)

result = client.enabled("my-first-feature-flag", context=context)

print("my-first-feature-flag is:", result)
```

See full documentation https://docs.prefab.cloud/docs/sdks/python

<<<<<<< HEAD
## Development

1. Ensure that `poetry` is installed: https://python-poetry.org/docs/#installation
2. From the root of this directory, run `poetry install` to ensure dependencies are installed
3. `poetry run python` to open a Python REPL with access to the project dependencies

### Running tests

To run all tests, including integration tests

```bash
poetry run pytest tests
```

To run only local tests and skip integration tests

```bash
poetry run pytest tests -k "not integration"
```

To run only one specific test file

```bash
poetry run pytest tests/name_of_test_file.py
```

### Releasing

1. Run pre-commit hooks to check and fix formatting, other rule enforcement.
   `poetry run pre-commit run --show-diff-on-failure --color=always --all-files`
2. On a branch
   1. Update the version in `pyproject.toml`
   2. Update `CHANGELOG.md`
3. Merge the branch
4. `git tag <version> && git push --tags`
5. `poetry release --build`
   1. To do this you will need an [pypi.org](https://pypi.org) account, and to be added to this project (ask Michael for an invitation)
 
## StructLog Configuration

### Simple Usage

There's a convenience method to access an opinionated structlog setup. **No configuration of structlog is performed by default**

```python
from prefab_cloud_python import default_structlog_setup;
default_structlog_setup(colors=True) # true is the default, false to remove ANSI color codes
```

### Using With Existing Structlog

We have a structlog processor that can be mixed into your existing structlog configuration.

The code below is an example configuration. **_See the note below about CallSiteParameterAdder_**

```python
import structlog
from prefab_cloud_python import create_prefab_structlog_processor
from prefab_cloud_python import STRUCTLOG_CALLSITE_IGNORES

structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
            ## ensure CallsiteparameterAdder is present before prefab_structlog_processor
            structlog.processors.CallsiteParameterAdder(
                [
                    structlog.processors.CallsiteParameter.PATHNAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                ],
                additional_ignores=STRUCTLOG_CALLSITE_IGNORES,
            ),
            create_prefab_structlog_processor(), ## add this
            structlog.dev.ConsoleRenderer(),
        ]
    )
```

#### CallSiteParameterAdder

We do require that `CallSiteParameterAdder` is present and configured to handle `PATHNAME` and `FUNCNAME` in addition to any parameters you may be using
Please also merge our `STRUCTLOG_CALLSITE_IGNORES` list into the `additional_ignores` list as shown below

```python
import structlog
from prefab_cloud_python import STRUCTLOG_CALLSITE_IGNORES

your_ignores = ["some", "ignores"]

structlog.processors.CallsiteParameterAdder(
                [
                    structlog.processors.CallsiteParameter.PATHNAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                ],
                additional_ignores=your_ignores + STRUCTLOG_CALLSITE_IGNORES,
            )
```
