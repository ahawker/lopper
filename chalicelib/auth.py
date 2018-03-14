"""
    lopper/auth
    ~~~~~~~~~~~

    Handles authenticating incoming requests.
"""
import hashlib
import hmac

from chalicelib import response


def is_authentic(payload_signature: str, payload: str, secret_token: bytes) -> response.Response:
    """
    Perform signature comparison to determine if the given data payload is authentic.

    :param payload_signature: Signature sent with payload to validate
    :type: :class:`~str`
    :param payload: Request payload
    :type: :class:`~str`
    :param secret_token: Shared secret token used to create payload hash
    :type: :class:`~bytes`
    :return: Response object indicating if the payload is authentic
    :rtype: :class:`~lopper.response.Response`
    """
    match = hmac.compare_digest(payload_signature, _signature(payload, secret_token))
    if not match:
        return response.unauthorized('Request signature does not match')
    return response.success('Request signature match')


def _signature(payload: str, secret_token: bytes) -> str:
    """
    Compute a SHA-1 signature for the given data payload based on our shared secret.

    :param payload: Request payload
    :type: :class:`~str`
    :param secret_token: Shared secret token used to create payload hash
    :type: :class:`~bytes`
    :return: Computed signature string for the payload
    :rtype: :class:`~str`
    """
    digest = hmac.new(secret_token, payload, hashlib.sha1).hexdigest()
    return 'sha1={}'.format(digest)
