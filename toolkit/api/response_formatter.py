"""Module for formatting API responses using Pydantic models."""

import math
from typing import Any, Optional, Type, Union

from pydantic import BaseModel

from toolkit.annotations import JSON
from toolkit.api.enums import Status
from toolkit.api.schemas import Pagination


class ResponseFormatter:
    """A class used to format responses using a Pydantic model."""

    def format_response(
        self,
        /,
        pydantic_model: Type[BaseModel],
        status: Status,
        message: str,
        data: Union[BaseModel, JSON, list[BaseModel], list[JSON]],
        links: Optional[JSON] = None,
        pagination: Optional[Pagination] = None,
    ) -> Any:
        """
        Format a response using a Pydantic model.

        Parameters
        ----------
        pydantic_model : Type[BaseModel]
            The Pydantic model class to be used for formatting the response.
        status : Status
            The status of the response (e.g., 'success', 'error').
        message : str
            A message describing the response.
        data : Union[BaseModel, JSON, list[BaseModel], list[JSON]]
            The data to be included in the response.
        links : Optional[JSON]
            Additional links or metadata to be included in the response.
        pagination : Optional[Pagination]
            The pagination information to be included in the response.

        Returns
        -------
        Any
            An instance of the Pydantic model class populated with the provided status,
            message, data, and links.
        """
        links = {} if links is None else links
        return pydantic_model(
            status=status,
            message=message,
            data=data,
            links=links,
            pagination=pagination,
        )

    def format_pagination(
        self,
        /,
        total_items: int,
        page: int,
        page_size: int,
        endpoint: str,
    ) -> tuple[Pagination, dict[str, Optional[str]]]:
        """
        Format pagination details for an API response.

        Parameters
        ----------
        total_items : int
            The total number of items to paginate.
        page : int
            The current page number.
        page_size : int
            The number of items per page.
        endpoint : str
            The base endpoint to be used for constructing pagination links.

        Returns
        -------
        tuple[Pagination, dict[str, Optional[str]]]
            A tuple containing the Pagination instance and a dictionary of links for
            navigating to the next and previous pages.

            Pagination instance includes:
            - total_items: Total number of items.
            - total_pages: Total number of pages.
            - current_page: The current page number.

            Links dictionary includes:
            - next_page: endpoint for the next page or None if there is no next page.
            - previous_page: endpoint for the previous page or None if there is no
                             previous page.
        """
        # Pagination
        total_pages = math.ceil(total_items / page_size)
        total_pages = 1 if total_pages == 0 else total_pages
        pagination = Pagination(
            total_items=total_items,
            total_pages=total_pages,
            current_page=page,
        )

        # Links
        next_page = (
            endpoint + f"?page={page + 1}?page_size={page_size}"
            if page < total_pages and total_items != 0
            else None
        )
        previous_page = (
            endpoint + f"?page={page - 1}?page_size={page_size}"
            if page > 1 and total_items != 0
            else None
        )
        links = {
            "next_page": next_page,
            "previous_page": previous_page,
        }
        return pagination, links
