"""
    lopper/app
    ~~~~~~~~~~

    Contains `chalice` app for running an AWS Lambda function responsible for receiving GitHub webhook requests.
"""
import chalice
import typing

from lopper import auth, conf, hub, payload, response


app = chalice.Chalice(app_name=conf.APPLICATION_NAME)


@app.route('/lopper')
def handler():
    # Authorize the request by validating it's signature against our shared secret token.
    resp = is_request_authentic(app.current_request)
    if not resp:
        return resp

    # Example the request payload to determine if it's an event we should process.
    resp = is_request_acceptable(app.current_request)
    if not resp:
        return resp

    # Process the request with the goal of deleting the head branch of a merged pull request.
    return process_request(app.current_request)


def is_request_authentic(request, secret_token: str = conf.WEBHOOK_SECRET_TOKEN):
    """
    Examine the given request object to determine if it was sent by an authorized source.

    :param request: Request object to examine for authenticity
    :type request: :class:`~chalice.app.Request`
    :param secret_token: Shared secret token used to create payload hash
    :type: :class:`~str`
    :return: Response object indicating whether or not the request is authentic
    :rtype: :class:`~lopper.response.Response`
    """
    signature = request.headers.get('X-Hub-Signature')
    if not signature:
        return response.unauthorized('Missing "X-Hub-Signature" header')

    return auth.is_authentic(signature, request.raw_body, secret_token)


def is_request_acceptable(request,
                          head_branch: str = conf.HEAD_BRANCH_PATTERN,
                          base_branch: str = conf.BASE_BRANCH_PATTERN,
                          repository_owner: str = conf.REPOSITORY_OWNER,
                          repository_name: str = conf.REPOSITORY_NAME,
                          head_branch_exclusion: typing.List[str] = conf.HEAD_BRANCH_EXCLUSION):
    """
    Examine the given request object to determine if it's a merged pull request that should be processed.

    :param request: Request object to examine for authenticity
    :type request: :class:`~chalice.app.Request`
    :param head_branch: Regular expression to match head branches to accept
    :type: :class:`~string`
    :param base_branch: Regular expression to match base branches to accept
    :type: :class:`~string`
    :param repository_owner: Regular expression to match repository owners to accept
    :type: :class:`~string`
    :param head_branch_exclusion: List of branch names to not accept
    :type: :class: `~list`
    :param repository_name: Regular expression to match repository names to accept
    :return: Response object indicating whether or not the request should be further processed
    :rtype: :class:`~lopper.response.Response`
    """
    # Nothing we can do if we received a request w/o a body or it wasn't using 'application/json' content-type.
    body = request.json_body
    if not body:
        return response.unprocessable_entity('Request body is not JSON or empty')

    return payload.is_acceptable_payload(body, head_branch, base_branch, repository_owner,
                                         repository_name, head_branch_exclusion)


def process_request(request, api_access_token: str = conf.API_ACCESS_TOKEN):
    """
    Examine the given request to find the merged head branch and invoke the GitHub API to delete it.

    :param request: Request object to process deleting the merged head branch of
    :type request: :class:`~chalice.app.Request`
    :param api_access_token: Access token for GitHub API client
    :type api_access_token: :class:`~str`
    :return: Response object indicating the success of deleting the merged head branch
    :rtype: :class:`~lopper.response.Response`
    """
    # Nothing we can do if we received a request w/o a body or it wasn't using 'application/json' content-type.
    body = request.json_body
    if not body:
        return response.unprocessable_entity('Request body is not JSON or empty')

    # Grab ref of merged pull request head branch and delete it.
    metadata = payload.get_target_branch_metadata(body)
    return hub.delete_branch(api_access_token, **metadata)
