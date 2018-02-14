"""
    lopper/conf
    ~~~~~~~~~~~

    Contains access to configuration values.
"""
import os


#: Environment variable to configure the base (target) branch of a pull request merge to consider for closing.
BASE_BRANCH_PATTERN = os.environ.get('GITHUB_BASE_BRANCH_PATTERN', '^master$')


#: Environment variable to configure the head (merge) branch of a pull request merge to consider for closing.
HEAD_BRANCH_PATTERN = os.environ.get('GITHUB_HEAD_BRANCH_PATTERN', '.*')


#: Environment variable to configure the Github API Access Token used to make authenticated API requests
#: for actions such as closing branches.
API_ACCESS_TOKEN = os.environ.get('GITHUB_API_ACCESS_TOKEN')


#: Environment variable to configure the Github Webhook Secret Token used to authenticate all incoming
#: webhook HTTP request payloads.
WEBHOOK_SECRET_TOKEN = os.environ.get('GITHUB_WEBHOOK_SECRET_TOKEN')


def validate() -> None:
    """
    Perform late bound configuration validation to allow for patching after import.

    :return: Nothing
    :rtype: :class:`~NoneType`
    :raises: :class:`~RuntimeError` when any configuration values are invalid
    """
    if not BASE_BRANCH_PATTERN:
        raise RuntimeError('Must supply a regex pattern for matching base branches')
    if not HEAD_BRANCH_PATTERN:
        raise RuntimeError('Must supply a regex pattern for matching head branches')
    if not API_ACCESS_TOKEN:
        raise RuntimeError('Must supply a Github API access token')
    if not WEBHOOK_SECRET_TOKEN:
        raise RuntimeError('Must supply a Github secret token to validate webhook requests')
