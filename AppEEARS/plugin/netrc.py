import os
from typing import Tuple, Union
from netrc import netrc, NetrcParseError


class ConflictError(Exception):
    """
    netrc machine creds already exist in the file, but aren't to be overwritten.
    """
    pass


def _get_user_netrc_path() -> str:
    """
    Return:
        (str): the absolute path to the user's netcdf file
    """
    return os.path.expanduser("~/.netrc")


def _parse_netrc(file_path: str) -> 'netrc':
    """
    Creates a useful object for parsing netrc data.

    Returns:
        (netrc)

    Raises:
        (NetrcParseError): if file couldn't be parsed
    """
    try:
        return netrc(file_path)
    except NetrcParseError as e:
        raise NetrcParseError(f"Failed to parse {file_path}: {e}")


def store_creds(
    machine: str, username: str, password: str, force_update: bool = False
):
    """
    Stores credentials for a machine in the current user's netrc file. If the file
    does not exist, it is created.

    Args:
        machine (str):       name of machine/host
        username (str):      account user
        password (str):      user's password
        force_update (bool): if True, overwrites any existing credentials
            for the machine.

    Returns:
        (None): the file is created/modified as necessary

    Raises:
        (ConflictError):
            if creds exist but overwrite not allowed
    """
    netrc_path = _get_user_netrc_path()
    # Create an empty file if not present
    if not os.path.exists(netrc_path):
        open(netrc_path, "w").close()
        # Set owner-read/write only (0600) for security
        os.chmod(netrc_path, 0o600)
    nrc = _parse_netrc(netrc_path)

    # Check if machine already exists
    existing_auth = nrc.hosts.get(machine)
    if existing_auth and not force_update:
        raise ConflictError(
            f"Credentials already exist for machine '{machine}' in user netrc file."
        )

    # Overwrite or create new entry
    nrc.hosts[machine] = (username, None, password)

    # Write updated netrc
    with open(netrc_path, "w") as f:
        # netrc doesn't provide an easy "write" method, so we manually reconstruct
        for host, creds in nrc.hosts.items():
            login, account, pwd = creds
            f.write(f"machine {host}\n  login {login}\n")
            if account:
                f.write(f"  account {account}\n")
            f.write(f"  password {pwd}\n")


def retrieve_creds(machine: str) -> Union[Tuple[None, None], Tuple[str, str]]:
    """
    Gets the credentials for a machine.

    Args:
        machine (str): the name of the machine/host
    """
    netrc_path = _get_user_netrc_path()
    if not os.path.exists(netrc_path):
        return None, None

    creds = _parse_netrc(netrc_path).hosts.get(machine)
    if not creds:
        # No entry for this machine
        return None, None

    return creds[0], creds[2]
