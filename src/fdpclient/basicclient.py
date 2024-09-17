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
    """Basic class for API client"""

    def __init__(self, base_url: str, headers: dict, timeout: int = 60):
        self.base_url = base_url
        self.headers = headers
        self.session = requests.session()
        self.session.headers.update(self.headers)
        self.ssl_verification = None
        self.timeout = timeout

    def _call_method(
        self, method, path, params: dict | None = None, data=None
    ) -> Response:
        if method.upper() not in ["GET", "POST", "PUT", "DELETE"]:
            error_msg = f"Unsupported method {method}"
            raise ValueError(error_msg)
        url = urljoin(self.base_url, path)

        logger.debug("%s: %s", method, url)

        response = None
        response = self.session.request(
            method, url, params=params, data=data, verify=self.ssl_verification
        )

        try:
            response.raise_for_status()
        except HTTPError as e:
            logger.exception(
                "%d %s: %s", e.response.status_code, e.response.reason, e.response.text
            )
            raise

        return response

    def get(self, path: str, params: dict | None = None) -> Response:
        return self._call_method("GET", path, params=params)

    def post(self, path: str, params: dict | None = None, data=None) -> Response:
        return self._call_method("POST", path, params=params, data=data)

    def update(self, path: str, params: dict | None = None, data=None) -> Response:
        return self._call_method("PUT", path, params=params, data=data)

    def delete(self, path: str, params: dict | None = None, data=None) -> Response:
        return self._call_method("DELETE", path, params=params, data=data)
