"""
    lopper/auth
    ~~~~~~~~~~~

    Handles authenticating incoming requests.
"""
import hashlib
import hmac


def is_authentic(payload_signature: str, payload: str, secret_token: str) -> bool:
    """
    Perform signature comparison to determine if the given data payload is authentic.

    :param payload_signature: Signature sent with payload to validate
    :type: :class:`~str`
    :param payload: Request payload
    :type: :class:`~str`
    :param secret_token: Shared secret token used to create payload hash
    :type: :class:`~str`
    :return: Boolean indicating authenticity of the payload
    :rtype: :class:`~bool`
    """
    return hmac.compare_digest(payload_signature, signature(payload, secret_token))


def signature(payload: str, secret_token: str) -> str:
    """
    Compute a SHA-1 signature for the given data payload based on our shared secret.

    :param payload: Request payload
    :type: :class:`~str`
    :param secret_token: Shared secret token used to create payload hash
    :type: :class:`~str`
    :return: Computed signature string for the payload
    :rtype: :class:`~str`
    """
    digest = hmac.new(secret_token, payload, hashlib.sha1).hexdigest()
    return 'sha1={}'.format(digest)
