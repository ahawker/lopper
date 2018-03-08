"""
    lopper/hub
    ~~~~~~~~~~

    Contains functionality for interacting with the GitHub API.
"""
from lopper import response


def delete_branch(api_access_token: str, repo: str, ref: str) -> response.Response:
    """
    Delete the remote branch on the given repo at the given ref.

    :param api_access_token: Access token for GitHub API client
    :type api_access_token: :class:`~str`
    :param repo: GitHub repository that owns the ref
    :type repo: :class:`~str`
    :param ref: GitHub branch ref to delete
    :type ref: :class:`~str`
    :return: Response object indicating result of branch deletion
    :rtype: :class:`~lopper.response.Response`
    """
    raise NotImplementedError('TODO - Implement')
