"""Client for making HTTP requests using the httpx library."""

from typing import Any, Optional
from urllib.parse import urljoin

import httpx


class AsyncAPIClient:
    """AsyncAPIClient class for making asynchronous HTTP requests."""

    def __init__(
        self,
        base_url: str,
        timeout: int = 10,
        default_headers: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize the AsyncAPIClient."""
        self.base_url = base_url
        self.timeout = timeout
        self.default_headers = default_headers or {}
        self._client = httpx.AsyncClient

    async def _request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        payload: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Make an asynchronous HTTP request.

        Parameters
        ----------
        method : str
            HTTP method (GET, POST, PUT, PATCH, DELETE).
        endpoint : str
            API endpoint.
        headers : dict, optional
            Additional headers for the request.
        params : dict, optional
            URL parameters.
        payload : dict, optional
            Request payload for methods like POST, PUT, PATCH.
        **kwargs
            Additional keyword arguments for httpx.AsyncClient.request.

        Returns
        -------
        httpx.Response
            The HTTP response object.
        """
        full_url = urljoin(self.base_url, endpoint)
        request_headers = {**self.default_headers, **(headers or {})}

        async with self._client() as client:
            response: httpx.Response = await client.request(
                method,
                full_url,
                headers=request_headers,
                params=params,
                data=payload,
                timeout=self.timeout,
                **kwargs,
            )
            response.raise_for_status()
            return response

    async def get(
        self,
        endpoint: str = "",
        headers: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Make an asynchronous HTTP GET request.

        Parameters
        ----------
        endpoint : str, optional
            API endpoint.
        headers : dict, optional
            Additional headers for the request.
        params : dict, optional
            URL parameters.
        **kwargs
            Additional keyword arguments for httpx.AsyncClient.request.

        Returns
        -------
        httpx.Response
            The HTTP response object.
        """
        response = await self._request(
            method="GET", endpoint=endpoint, headers=headers, params=params, **kwargs
        )
        return response

    async def post(
        self,
        endpoint: str = "",
        headers: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        payload: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Make an asynchronous HTTP POST request.

        Parameters
        ----------
        endpoint : str, optional
            API endpoint.
        headers : dict, optional
            Additional headers for the request.
        params : dict, optional
            URL parameters.
        payload : dict, optional
            Request data.
        **kwargs
            Additional keyword arguments for httpx.AsyncClient.request.

        Returns
        -------
        httpx.Response
            The HTTP response object.
        """
        response = await self._request(
            method="POST",
            endpoint=endpoint,
            headers=headers,
            params=params,
            payload=payload,
            **kwargs,
        )
        return response

    async def put(
        self,
        endpoint: str = "",
        headers: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        payload: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Make an asynchronous HTTP PUT request.

        Parameters
        ----------
        endpoint : str, optional
            API endpoint.
        headers : dict, optional
            Additional headers for the request.
        params : dict, optional
            URL parameters.
        payload : dict, optional
            Request data.
        **kwargs
            Additional keyword arguments for httpx.AsyncClient.request.

        Returns
        -------
        httpx.Response
            The HTTP response object.
        """
        response = await self._request(
            method="PUT",
            endpoint=endpoint,
            headers=headers,
            params=params,
            payload=payload,
            **kwargs,
        )
        return response

    async def patch(
        self,
        endpoint: str = "",
        headers: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        payload: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Make an asynchronous HTTP PATCH request.

        Parameters
        ----------
        endpoint : str, optional
            API endpoint.
        headers : dict, optional
            Additional headers for the request.
        params : dict, optional
            URL parameters.
        payload : dict, optional
            Request data.
        **kwargs
            Additional keyword arguments for httpx.AsyncClient.request.

        Returns
        -------
        httpx.Response
            The HTTP response object.
        """
        response = await self._request(
            method="PATCH",
            endpoint=endpoint,
            headers=headers,
            params=params,
            payload=payload,
            **kwargs,
        )
        return response

    async def delete(
        self,
        endpoint: str = "",
        headers: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Make an asynchronous HTTP DELETE request.

        Parameters
        ----------
        endpoint : str, optional
            API endpoint.
        headers : dict, optional
            Additional headers for the request.
        params : dict, optional
            URL parameters.
        **kwargs
            Additional keyword arguments for httpx.AsyncClient.request.

        Returns
        -------
        httpx.Response
            The HTTP response object.
        """
        response = await self._request(
            method="DELETE", endpoint=endpoint, headers=headers, params=params, **kwargs
        )
        return response

    def __str__(self) -> str:
        """Return a human-readable string representation of the AsyncAPIClient."""
        return f"AsyncAPIClient - Base URL: {self.base_url}, Timeout: {self.timeout}s"

    def __repr__(self) -> str:
        """Return an unambiguous string representation of the AsyncAPIClient."""
        return (
            f"AsyncAPIClient(base_url={self.base_url}, "
            f"timeout={self.timeout}, "
            f"default_headers={self.default_headers})"
        )
