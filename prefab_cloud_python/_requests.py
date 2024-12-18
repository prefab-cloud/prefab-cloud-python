import importlib
from socket import socket
from typing import Optional

from ._internal_logging import (
    InternalLogger,
)
import requests
from requests import Response, RequestException
from requests.adapters import HTTPAdapter
from tenacity import (
    retry,
    stop_after_delay,
    wait_exponential,
    retry_if_exception_type,
)
from importlib.metadata import version

logger = InternalLogger(__name__)


try:
    from importlib.metadata import version
    Version = version("prefab-cloud-python")
except importlib.metadata.PackageNotFoundError:
    Version = "development"


VersionHeader = "X-PrefabCloud-Client-Version"

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


class NoRetryAdapter(HTTPAdapter):
    def send(
        self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None
    ):
        return super().send(request, stream, timeout, verify, cert, proxies)


class UnauthorizedException(Exception):
    def __init__(self, api_key):
        api_key_prefix = api_key[:10] if api_key else ""
        super().__init__(
            f"Prefab attempts to fetch data are unauthorized using api key starting with {api_key_prefix}. Please check your api key."
        )


class HostIterator:
    def __init__(self, hosts):
        self.hosts = hosts
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if not self.hosts:
            raise StopIteration
        host = self.hosts[self.index]
        self.index = (self.index + 1) % len(self.hosts)
        return host


class ApiClient:
    def __init__(self, options):
        self.hosts = options.prefab_api_urls
        self.session = requests.Session()
        self.session.mount("https://", NoRetryAdapter())
        self.session.mount("http://", NoRetryAdapter())
        self.session.headers.update({VersionHeader: f"prefab-cloud-python-{Version}"})

    def get_host(self, attempt_number, host_list):
        return host_list[attempt_number % len(host_list)]

    @retry(
        stop=stop_after_delay(8),
        wait=wait_exponential(multiplier=1, min=0.05, max=2),
        retry=retry_if_exception_type((RequestException, ConnectionError, OSError)),
    )
    def resilient_request(
        self, path, method="GET", hosts: Optional[list[str]] = None, **kwargs
    ) -> Response:
        # Get the current attempt number from tenacity's context
        attempt_number = self.resilient_request.statistics["attempt_number"]
        host = self.get_host(
            attempt_number - 1, hosts or self.hosts
        )  # Subtract 1 because attempt_number starts at 1
        url = f"{host.rstrip('/')}/{path.lstrip('/')}"

        try:
            logger.info(f"Attempt {attempt_number}: Requesting {url}")
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            logger.info(f"Attempt {attempt_number}: Successful request to {url}")
            return response
        except (RequestException, ConnectionError) as e:
            logger.warning(
                f"Attempt {attempt_number}: Request to {url} failed: {str(e)}. Will retry"
            )
            raise
        except OSError as e:
            if isinstance(e, socket.gaierror):
                logger.warning(
                    f"Attempt {attempt_number}: DNS resolution failed for {url}: {str(e)}. Will retry"
                )
                raise
            else:
                logger.error(
                    f"Attempt {attempt_number}: Non-retryable error occurred: {str(e)}"
                )
                raise
