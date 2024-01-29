from requests import Response
from requests.adapters import HTTPAdapter

DEFAULT_TIMEOUT = 5  # seconds


# from https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/
class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs) -> None:
        self.timeout = kwargs.pop("timeout", DEFAULT_TIMEOUT)
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs) -> Response:
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)
