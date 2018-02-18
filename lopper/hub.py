"""
    lopper/hub
    ~~~~~~~~~~

    Contains functionality for interacting with the GitHub API.
"""
from lopper import response


def delete_branch(ref: str) -> response.Response:
    """
    Delete the remote branch at the given ref.

    :param ref: GitHub branch ref to delete
    :type ref: :class:`~str`
    :return: Response object indicating result of branch deletion
    :rtype: :class:`~lopper.response.Response`
    """
    raise NotImplementedError('TODO - Implement')
