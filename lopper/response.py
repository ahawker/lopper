"""
    lopper/response
    ~~~~~~~~~~~~~~~

    Contains functionality for creating API responses.
"""
import functools

import chalice


#: Default response HTTP status code to return if not explicitly defined.
DEFAULT_STATUS_CODE = 200


#: Default response HTTP headers to return if not explicitly defined.
DEFAULT_HEADERS = {
    'Content-Type': 'application/json'
}


class Response(chalice.Response):
    """
    Extend the :class:`~chalice.app.Response` type to make usage cleaner.
    """
    def __repr__(self):
        return '<{}(status_code={}, body={}, headers={})>'.format(self.__class__.__name__, self.status_code,
                                                                  self.body, self.headers)

    def __bool__(self):
        return self.status_code == 200


def response(message, status_code: int = DEFAULT_STATUS_CODE, headers: dict = DEFAULT_HEADERS):
    """
    Create :class:`~lopper.response.Response` instances with sensible defaults.

    :param message: Human readable response message indicating what happened
    :type message: :class:`~str`
    :param status_code: HTTP status code of the response; default: 200
    :type status_code: :class:`~int`
    :param headers: HTTP headers of the response; default: "Content-Type": "application/json"
    :type headers: :class:`~dict`
    :return: Response object containing HTTP metadata.
    :rtype: :class:`~looper.response.Response`
    """
    headers['Content-Type'] = 'application/json'
    return Response(message, headers, status_code)


#: Function partial for creating '200 OK' HTTP responses.
success = functools.partial(response, status_code=200)


#: Function partial for creating '401 Unauthorized' HTTP responses.
unauthorized = functools.partial(response, status_code=401)


#: Function partial for creating '422 Unprocessable Entity' HTTP responses.
unprocessable_entity = functools.partial(response, status_code=422)


#: Function partial for creating '500 Server Error' HTTP responses.
server_error = functools.partial(response, status_code=500)


#: Mapping for converting a numeric HTTP static code to the appropriate response partial function.
PARTIAL_BY_STATUS = {
    200: success,
    401: unauthorized,
    422: unprocessable_entity,
    500: server_error
}


def partial_for_status(status_code: int) -> functools.partial:
    """
    Retrieve a function partial that returns a :class:`~lopper.response.Response` instance
    for the given HTTP status code.

    :param status_code: HTTP status code of the response
    :type status_code: :class:`~int`
    :return: Function partial that returns a response object.
    :rtype: :class:`~functools.partial`
    """
    return PARTIAL_BY_STATUS.get(status_code, server_error)
