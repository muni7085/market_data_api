import json
from typing import Any

import requests
from fastapi import HTTPException

from app.utils.headers import REQUEST_HEADERS
from app.utils.urls import NSE_BASE_URL


def fetch_nse_data(url: str, max_tries: int = 1000) -> Any:
    """
    Fetch the data from given nse url and decode the response as a key value paris.

    Parameters:
    -----------
    url: ``str``
        Url from nse to fetch the data.
    max_tries: ``int`` (defaults = 1000)
        Maximum number of times the request has to send to get response.
        Requests are made until either get the status code `200` or exceed max_tries.

    Raises:
    -------
    ``HTTPException``
        If not get response even after max_tries.


    Returns:
    --------
    ``Any``
        Json loaded response from the api.
    """
    if max_tries < 1:
        raise ValueError("max_tries should be greater than 0")

    session = requests.Session()
    request = session.get(NSE_BASE_URL, headers=REQUEST_HEADERS)

    for _ in range(max_tries):
        cookies = dict(request.cookies)
        response = session.get(url, headers=REQUEST_HEADERS, timeout=5, cookies=cookies)

        if response.status_code == 200:
            return json.loads(response.content.decode("utf-8"))

        if response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail={"Error": "Resource not found or invalid Url"},
            )

    raise HTTPException(
        status_code=503,
        detail={"Error": "Service Unavailable"},
    )
