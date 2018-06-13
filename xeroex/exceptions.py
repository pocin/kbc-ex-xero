
class XeroexError(Exception):
    """All custom errors originate from this"""

class XeroexUserConfigError(XeroexError, ValueError):
    """User did something wrong!"""


