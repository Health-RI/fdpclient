# SPDX-FileCopyrightText: 2024 Stichting Health-RI
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
from urllib.parse import urljoin

import requests
from requests import HTTPError, Response

logger = logging.getLogger(__name__)


class BasicAPIClient:
    """Basic REST API client

    When created, this client creates one Requests session to keep track of cookies and connections.
    """

    def __init__(self, base_url: str, headers: dict, timeout: float = 60):
        """Creates a Basic API client instance

        Parameters
        ----------
        base_url : str
            Base URL after which all requests are based. Needs to include protocol ("http" or "https")
        headers : dict
            Additional headers to include on every request. For example, Bearer / Tokens.
        timeout : float, optional
            Timeout (in seconds) for every API call, by default 60
        """
        self.base_url = base_url
        self.headers = headers
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.ssl_verification = None
        self.timeout = timeout

    def _call_method(self, method, path, params: dict | None = None, data=None, json=None) -> Response:
        if method.upper() not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
            error_msg = f"Unsupported method {method}"
            raise ValueError(error_msg)
        url = urljoin(self.base_url, path)

        logger.debug("%s: %s", method, url)

        response = None
        response = self.session.request(
            method,
            url,
            params=params,
            data=data,
            json=json,
            verify=self.ssl_verification,
            timeout=self.timeout,
        )

        try:
            response.raise_for_status()
        except HTTPError as e:
            logger.exception("%d %s: %s", e.response.status_code, e.response.reason, e.response.text)
            raise

        return response

    def get(self, path: str, params: dict | None = None, **kwargs) -> Response:
        return self._call_method("GET", path, params=params, **kwargs)

    def post(self, path: str, params: dict | None = None, data=None, **kwargs) -> Response:
        return self._call_method("POST", path, params=params, data=data, **kwargs)

    def update(self, path: str, params: dict | None = None, data=None, **kwargs) -> Response:
        return self._call_method("PUT", path, params=params, data=data, **kwargs)

    def patch(self, path: str, params: dict | None = None, data=None, **kwargs) -> Response:
        return self._call_method("PATCH", path, params=params, data=data, **kwargs)

    def delete(self, path: str, params: dict | None = None, data=None, **kwargs) -> Response:
        return self._call_method("DELETE", path, params=params, data=data, **kwargs)
