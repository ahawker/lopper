"""
    lopper/payload
    ~~~~~~~~~~~~~~

    Contains functionality for examining HTTP request payloads.
"""
import re
import typing

from lopper import response


def get_target_branch_metadata(payload: dict) -> typing.Dict[str, str]:
    """
    Retrieve metadata of the head branch that was merged in the pull request.

    :param payload: Request payload to examine
    :type: :class:`~dict`
    :return: Metadata of the merged head branch that should be deleted
    :rtype: :class:`~dict`
    """
    head = payload['pull_request']['head']
    return dict(repo=head['repo']['full_name'], ref=head['ref'])


def is_acceptable_payload(payload: dict, head_branch: str, base_branch: str, repository_owner: str,
                          repository_name: str, head_branch_exclusion: typing.List[str]) -> response.Response:
    """
    Determine if the payload meets the necessary requirements for being a target for processing.

    :param payload: Request payload to examine
    :type: :class:`~dict`
    :param head_branch: Regular expression to match head branches to accept
    :type: :class:`~str`
    :param base_branch: Regular expression to match base branches to accept
    :type: :class:`~str`
    :param repository_owner: Regular expression to match repository owners to accept
    :type: :class:`~str`
    :param repository_name: Regular expression to match repository names to accept
    :type: :class:`~str`
    :param head_branch_exclusion: List of branch names to not accept
    :type: :class: `~list`
    :return: Response object indicating if the payload should be processed further.
    :rtype: :class:`~lopper.response.Response`
    """
    if not _is_pull_request_closed(payload):
        return response.unprocessable_entity('Received payload for pull request that was not closed')

    repository = payload.get('repository')
    if not repository:
        return response.unprocessable_entity('Received payload that is missing "repository" data')

    if not _is_repository_owner_match(repository, repository_owner):
        msg = 'Received payload for repository that does not match owner pattern: {}'.format(repository_owner)
        return response.unprocessable_entity(msg)

    if not _is_repository_name_match(repository, repository_name):
        msg = 'Received payload for repository that does not match name pattern: {}'.format(repository_name)
        return response.unprocessable_entity(msg)

    pull_request = payload.get('pull_request')
    if not pull_request:
        return response.unprocessable_entity('Received payload that is missing "pull_request" data')

    if not _is_pull_request_merged(pull_request):
        return response.unprocessable_entity('Received payload for pull request that was not merged')

    if not _is_pull_request_head_branch_match(pull_request, head_branch):
        msg = 'Received payload for pull request that does not match head branch pattern: {}'.format(head_branch)
        return response.unprocessable_entity(msg)

    if not _is_pull_request_head_branch_included(pull_request, head_branch_exclusion):
        msg = 'Received payload for pull request that matches an excluded head branch name'
        return response.unprocessable_entity(msg)

    if not _is_pull_request_base_branch_match(pull_request, base_branch):
        msg = 'Received payload for pull request that does not match base branch patter: {}'.format(base_branch)
        return response.unprocessable_entity(msg)

    return response.success('Pull request payload is acceptable to process')


def _is_pull_request_closed(payload: dict) -> bool:
    """
    Determine if the payload represents a notification of a pull request being closed.

    :param payload: Request payload to examine
    :type: :class:`~dict`
    :return: Boolean indicating payload state
    :rtype: :class:`~bool`
    """
    action = payload.get('action')
    return action and action.lower() == 'closed'


def _is_pull_request_merged(pull_request: dict) -> bool:
    """
    Determine if the pull request contains meta-data indicating it was merged.

    :param pull_request: Pull request section of payload to examine
    :type: :class:`~dict`
    :return: Boolean indicating pull request state
    :rtype: :class:`~bool`
    """
    merged_at = pull_request.get('merged_at')
    merged_commit_sha = pull_request.get('merged_commit_sha')
    return all((merged_at, merged_commit_sha))


def _is_pull_request_head_branch_match(pull_request: dict, head_branch: str) -> bool:
    """
    Determine if the pull request represents a notification for a head branch we should consider.

    :param pull_request: Pull request section of payload to examine
    :type: :class:`~dict`
    :param head_branch: Regular expression to match head branches to accept
    :type: :class:`~str`
    :return: Boolean indicating pull request state
    :rtype: :class:`~bool`
    """
    head = pull_request.get('head')
    return head and re.match(head_branch, head) is not None


def _is_pull_request_head_branch_included(pull_request: dict, head_branch_exclusion: typing.List[str]) -> bool:
    """
    Determine if the pull request represents a notification for a head branch we should consider
    based on the fact that it is not in the exclusion list.

    :param pull_request: Pull request section of payload to examine
    :type: :class:`~dict`
    :param head_branch_exclusion: List of branches to exclude
    :type: :class:`~list`
    :return: Boolean indicating pull request state
    :rtype: :class:`~bool`
    """
    head = pull_request.get('head')
    return head and head not in head_branch_exclusion


def _is_pull_request_base_branch_match(pull_request: dict, base_branch: str) -> bool:
    """
    Determine if the pull request represents a notification for a base branch we should consider.

    :param pull_request: Pull request section of payload to examine
    :type: :class:`~dict`
    :param base_branch: Regular expression to match base branches to accept
    :type: :class:`~str`
    :return: Boolean indicating pull request state
    :rtype: :class:`~bool`
    """
    base = pull_request.get('base')
    return base and re.match(base_branch, base) is not None


def _is_repository_owner_match(repository: dict, repository_owner: str) -> bool:
    """
    Determine if the payload represents a notification for a repository we should consider.

    :param repository: Repository section of payload to examine
    :type: :class:`~dict`
    :param repository_owner: Regular expression to match repository owners to accept
    :type: :class:`~str`
    :return: Boolean indicating pull request state
    :rtype: :class:`~bool`
    """
    owner = repository.get('owner')
    if not owner:
        return False
    login = owner.get('login')
    return login and re.match(repository_owner, login) is not None


def _is_repository_name_match(repository: dict, repository_name: str) -> bool:
    """
    Determine if the payload represents a notification for a repository we should consider.

    :param repository: Repository section of payload to examine
    :type: :class:`~dict`
    :param repository_name: Regular expression to match repository name to accept
    :type: :class:`~str`
    :return: Boolean indicating pull request state
    :rtype: :class:`~bool`
    """
    name = repository.get('name')
    return name and re.match(repository_name, name) is not None
