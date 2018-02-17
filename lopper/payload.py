"""
    lopper/payload
    ~~~~~~~~~~~~~~

    Contains functionality for examining HTTP request payloads.
"""
import logging
import re


LOGGER = logging.getLogger(__name__)


def is_acceptable_payload(payload: dict, head_branch: str, base_branch: str, repository_owner: str,
                          repository_name: str) -> bool:
    """
    Determine if the payload meets the necessary requirements for being a target for processing.

    :param payload: Request payload to examine
    :type: :class:`~dict`
    :param head_branch: Regular expression to match head branches to accept
    :type: :class:`~string`
    :param base_branch: Regular expression to match base branches to accept
    :type: :class:`~string`
    :param repository_owner: Regular expression to match repository owners to accept
    :type: :class:`~string`
    :param repository_name: Regular expression to match repository names to accept
    :type: :class:`~string`
    :return: Boolean indicating if the payload should be processed further.
    :rtype: :class:`~bool`
    """
    if not _is_pull_request_closed(payload):
        LOGGER.info('Received payload for pull request that was not closed')
        return False

    repository = payload.get('repository')
    if not repository:
        LOGGER.error('Received payload that is missing "repository" data')
        return False

    if not _is_repository_owner_match(repository, repository_owner):
        LOGGER.info('Received payload for repository that does not match owner pattern: {}'.format(repository_owner))
        return False

    if not _is_repository_name_match(repository, repository_name):
        LOGGER.info('Received payload for repository that does not match name pattern: {}'.format(repository_name))
        return False

    pull_request = payload.get('pull_request')
    if not pull_request:
        LOGGER.error('Received payload that is missing "pull_request" data')
        return False

    if not _is_pull_request_merged(pull_request):
        LOGGER.info('Received payload for pull request that was not merged')
        return False

    if not _is_pull_request_head_branch_match(pull_request, head_branch):
        LOGGER.info('Received payload for pull request that does not match head branch pattern: {}'.format(head_branch))
        return False

    if not _is_pull_request_base_branch_match(pull_request, base_branch):
        LOGGER.info('Received payload for pull request that does not match base branch patter: {}'.format(base_branch))
        return False

    return True


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
    :type: :class:`~string`
    :return: Boolean indicating pull request state
    :rtype: :class:`~bool`
    """
    head = pull_request.get('head')
    return head and re.match(head_branch, head) is not None


def _is_pull_request_base_branch_match(pull_request: dict, base_branch: str) -> bool:
    """
    Determine if the pull request represents a notification for a base branch we should consider.

    :param pull_request: Pull request section of payload to examine
    :type: :class:`~dict`
    :param base_branch: Regular expression to match base branches to accept
    :type: :class:`~string`
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
    :type: :class:`~string`
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
    :type: :class:`~string`
    :return: Boolean indicating pull request state
    :rtype: :class:`~bool`
    """
    name = repository.get('name')
    return name and re.match(repository_name, name) is not None
