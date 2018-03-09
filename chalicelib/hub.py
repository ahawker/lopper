"""
    lopper/hub
    ~~~~~~~~~~

    Contains functionality for interacting with the GitHub API.
"""
import github

from chalicelib import response


def exception_to_response(func):
    """
    Decorator that catches :class:`~github.GithubException` and converts them to
    :class:`~lopper.response.Response` instances.
    """
    def decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except github.GithubException as e:
            partial = response.partial_for_status(e.status)
            return partial(str(e))
    return decorator


@exception_to_response
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
    api = github.Github(api_access_token)

    repository = api.get_repo(repo)
    repository_ref = repository.get_git_ref('heads/{}'.format(ref))
    repository_ref.delete()

    return response.success('Successfully deleted "{}" from repository "{}"'.format(ref, repo))
