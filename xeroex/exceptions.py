
class XeroexError(Exception):
    """All custom errors originate from this"""

class XeroexUserConfigError(XeroexError, ValueError):
    """User did something wrong!"""

class XeroexAuthorizationExpired(XeroexError):
    """When PublicCredentials expire after 30 minutes"""
