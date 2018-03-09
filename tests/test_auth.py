"""
    test/auth
    ~~~~~~~~~

    Tests for the :mod:`~lopper/auth` module.
"""
import random
import string
import pytest

from lopper import auth


@pytest.fixture(scope='session')
def secret_token():
    """
    Fixture that yields a usable secret token.
    """
    return 'super-secret-token-string'.encode()


@pytest.fixture(scope='function')
def random_secret_token():
    """
    Fixture that yields a random secret token.
    """
    n = random.randint(12, 24)
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(n)).encode()


@pytest.fixture(scope='function')
def random_payload_bytes():
    """
    Fixture that yields the randomly generated payload string encoded as bytes.
    """
    n = random.randint(8, 128)
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(n)).encode()


@pytest.fixture(scope='function')
def random_payload_shuffled_bytes(random_payload_bytes):
    """
    Fixture that yields the randomly generated payload bytes but shuffled in a random order.
    """
    return random.sample(random_payload_bytes, len(random_payload_bytes))


def test_is_authenticate_with_same_secret_token(secret_token, random_payload_bytes):
    """
    Assert that :func:`~lopper.auth.is_authenticate` returns a response match when the computed signature
    uses the same secret token that the given payload was signed with.
    """
    signature = auth._signature(random_payload_bytes, secret_token)
    assert auth.is_authentic(signature, random_payload_bytes, secret_token)


def test_not_is_authenticate_with_different_secret_token(secret_token, random_secret_token, random_payload_bytes):
    """
    Assert that :func:`~lopper.auth.is_authenticate` returns a falsey response when the computed signature
    does not use the same secret token that the given payload was signed with.
    """
    signature = auth._signature(random_payload_bytes, secret_token)
    assert not auth.is_authentic(signature, random_payload_bytes, random_secret_token)

    signature = auth._signature(random_payload_bytes, random_secret_token)
    assert not auth.is_authentic(signature, random_payload_bytes, secret_token)
