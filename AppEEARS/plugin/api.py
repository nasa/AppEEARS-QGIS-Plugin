import requests
from datetime import datetime, timezone
from typing import Optional, Union

DEFAULT_TIMEOUT = 30


class ApiError(Exception):
    """
    General error involving the API
    """
    pass


class LoginError(Exception):
    """
    When bad creds are used in call to login endpoint
    """


class DataRetrivalError(Exception):
    """
    When data cannot be obtained or parsed
    """

class StopPagination(Exception):
    """
    A sentinel for when no more pagination is necessary
    """
    pass


class Client:

    def __init__(self, creds: tuple):
        self._url = 'https://appeears.earthdatacloud.nasa.gov/api/'
        self._creds = creds
        self._token, self._token_exp = None, None

    def _handle_token(self):
        # if no token, or expired token, obtain one
        if self._token is None or (
            self._token is not None and self._token_exp < datetime.now(tz=timezone.utc)
        ):
            response = requests.post(
                f"{self._url}login", auth=self._creds, timeout=DEFAULT_TIMEOUT
            )
            if response.status_code == 200:
                data = response.json()
                if not (token := data["token"]):
                    raise LoginError("API response did not contain 'token'")
                self._token = token
                self._token_exp = datetime.strptime(
                    data["expiration"], '%Y-%m-%dT%H:%M:%SZ'
                ).replace(tzinfo=timezone.utc)
            else:
                raise LoginError(
                    f"Token request failed with HTTP {response.status_code}: {response.text}"
                )

    @property
    def token(self):
        self._handle_token()  # refresh done if necessary
        return self._token

    def update_creds(self, creds):
        self._creds = creds

    def _get_auth_header(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"}

    def fetch_task_data(self, max: Optional[Union[int, None]] = None) -> dict:
        """
        Uses the AppEEARS token to retrieve task info from the API endpoint.
        Paginates to retrieve all applicable results.

        Args:
            max (None or int): if int, only a maximum of that
                many tasks are returned.

        Yields:
            task (dict): all info for the task
        """
        limit, has_max = 1000, isinstance(max, int)
        offset, count = 0, 0
        try:
            while True:
                response = requests.get(
                    f'{self._url}task?limit={limit}&offset={offset}',
                    headers=self._get_auth_header(),
                    timeout=DEFAULT_TIMEOUT
                )
                if response.status_code == 200:
                    tasks = response.json()
                    for task in tasks:
                        yield task
                        count += 1
                        if has_max and count >= max:
                            # return limit reached
                            raise StopPagination
                    if len(tasks) < limit:
                        # end of tasks
                        raise StopPagination
                    offset += 1
        except StopPagination:
            pass
        except LoginError as e:
            raise ApiError(str(e)) from e
        except Exception as e:
            raise DataRetrivalError(str(e)) from e

    def fetch_bundle_data(self, task_id: str):
        """
        Retrieves the AppEEARS bundle using a task id.
        """
        try:
            response = requests.get(
                f'{self._url}bundle/{task_id}', headers=self._get_auth_header(),
                timeout=DEFAULT_TIMEOUT
            )
            if response.status_code == 200:
                return response.json()['files']
            else:
                return None
        except LoginError as e:
            raise ApiError(str(e)) from e
        except Exception as e:
            raise DataRetrivalError(str(e)) from e

    def build_file_url(self, task_id: str, file_id: str, file_name: str) -> str:
        """
        Composes the file url when given the AppEEARS API url, task id, file id, and file name.
        """
        return f"{self._url}bundle/{task_id}/{file_id}/{file_name}"
