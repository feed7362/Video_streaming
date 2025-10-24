import os
from typing import Any, Dict, Optional

import hvac


class VaultClient:
    """
    A client wrapper for HashiCorp Vault using the hvac library.

    Example:
        >>> vault = VaultClient()
        >>> secret = vault.read_secret(path="myapp/config", mount_point="secret")
        >>> print(secret["username"])
    """

    def __init__(self, url: Optional[str] = None, token: Optional[str] = None) -> None:
        """
        Initialize the Vault client.

        Args:
            url (str, optional): The Vault server address (defaults to VAULT_ADDR env var).
            token (str, optional): The Vault token (defaults to VAULT_TOKEN env var).

        Raises:
            ValueError: If authentication fails.
        """
        self.url = url or os.getenv("VAULT_ADDR")
        self.token = token or os.getenv("VAULT_TOKEN")

        if not self.url or not self.token:
            raise ValueError(
                "Vault address or token not provided (check VAULT_ADDR / VAULT_TOKEN)."
            )

        self.client = hvac.Client(url=self.url, token=self.token)

        if not self.client.is_authenticated():
            raise ValueError(
                "Vault authentication failed. Check your token and Vault address."
            )

    def read_secret(self, path: str, mount_point: str = "secret") -> Dict[str, Any]:
        """
        Read a secret from Vault KV v2.

        Args:
            path (str): The path to the secret within the mount point.
            mount_point (str): The mount point for the KV engine (default: "secret").

        Returns:
            dict: The secret data.

        Raises:
            hvac.exceptions.InvalidPath: If the secret path does not exist.
        """
        response = self.client.secrets.kv.v2.read_secret_version(
            path=path, mount_point=mount_point
        )
        return response["data"]["data"]
