"""
Functions for authentication and storing Earthdata login credentials.
"""

import os
import requests
from netrc import netrc, NetrcParseError

class NetrcConflictError(Exception):
    """
    Raised when the machine already exists in netrc and 'force_update' is False.
    """
    pass

def store_creds_netrc(machine: str, username: str, password: str, force_update: bool = False):
        """
        Checks if ~/.netrc exists and has an entry for `machine`.
        If not present, creates or appends it. 
        If `force_update=True`, overwrites existing credentials for that machine.
        """
        
        #TODO - May need to account for _netrc
        netrc_path = os.path.expanduser("~/.netrc")

        # Create an empty ~/.netrc if not present
        if not os.path.exists(netrc_path):
            open(netrc_path, "w").close()
            # Set owner-read/write only (0600) for security
            os.chmod(netrc_path, 0o600)

        # Parse existing netrc
        try:
            nrc = netrc(netrc_path)
        except NetrcParseError as e:
            raise RuntimeError(f"Failed to parse {netrc_path}: {e}")

        # Check if machine already exists
        existing_auth = nrc.hosts.get(machine)
        if existing_auth and not force_update:
            raise NetrcConflictError(f"Credentials already exist for'{machine}' in .netrc file.")

        # Overwrite or create new entry
        nrc.hosts[machine] = (username, None, password)

        # Write updated netrc
        with open(netrc_path, "w") as f:
            # netrc doesn't provide an easy "write" method, so we manually reconstruct
            for host, auth in nrc.hosts.items():
                login, account, pwd = auth
                f.write(f"machine {host}\n  login {login}\n")
                if account:
                    f.write(f"  account {account}\n")
                f.write(f"  password {pwd}\n")

        # Set permissions
        os.chmod(netrc_path, 0o600)

def retrieve_stored_creds(machine):
    """
    Returns a (username, password) tuple for the given machine or (None, None) if machine is not found.
    """

    netrc_path = os.path.expanduser("~/.netrc")

    if not os.path.exists(netrc_path):
        return None, None

    try:
        nrc = netrc(netrc_path)
    except NetrcParseError as e:
        raise RuntimeError(f"Failed to parse {netrc_path}: {e}")

    existing_auth = nrc.hosts.get(machine)
    if not existing_auth:
        # No entry for this machine
        return None, None

    username, account, password = existing_auth
    return username, password    

def get_appeears_token(api_url:str, machine:str, username:str, password:str):
    """
    Use EDL credentials to retrieve a token for AppEEARS.
    """
    response = requests.post('{}login'.format(api_url), auth=(username, password))
    
    if response.status_code == 200:
        token = response.json()['token']

        if not token:
            raise ValueError("API response did not contain 'token'")
        return token
    
    else:
        raise RuntimeError(f"Token request failed with HTTP {response.status_code}: {response.text} ")
    
