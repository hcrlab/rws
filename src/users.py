from enum import Enum

class UserVerifierError(Enum):
  NO_COOKIE = 1
  INVALID_TOKEN = 2
  DISALLOWED_USER = 3

class UserVerifier(object):
  """Verifies user login using Google Identity Toolkit."""
  def __init__(self, gitkit_client, allowed_users):
    self._gitkit_client = gitkit_client
    self._allowed_users = allowed_users

  def check_user(self, request):
    """Checks the user login cookie.

    Returns: (email, error), Email is the string email address of the person who
      logged in, or None if the login was invalid. Error is a UserVerifierError
      describing why the login was invalid, or None if the login was valid.
    """
    if 'gtoken' not in request.cookies:
      return None, UserVerifierError.NO_COOKIE

    gitkit_user = self._gitkit_client.VerifyGitkitToken(request.cookies['gtoken'])
    if gitkit_user is None:
      return None, UserVerifierError.INVALID_TOKEN

    if gitkit_user.email in self._allowed_users:
      return gitkit_user.email, None
    else:
      return None, UserVerifierError.DISALLOWED_USER
