"""Exception definitions for aiocomfoconnect.

This module defines custom exception classes for error handling in the
aiocomfoconnect package. All exceptions are documented according to PEP 257
and Google style, and use modern Python 3.10+ type annotations.
"""

from __future__ import annotations


class ComfoConnectError(Exception):
    """Base error for ComfoConnect.

    Args:
        message (str): Description of the error.

    Example:
        >>> raise ComfoConnectError("An error occurred")
    """

    def __init__(self, message: str) -> None:
        """Initialize ComfoConnectError.

        Args:
            message (str): Description of the error.
        """
        self.message = message
        super().__init__(message)
        self.message = message


class ComfoConnectBadRequest(ComfoConnectError):
    """Error raised when the request is malformed.

    Example:
        >>> raise ComfoConnectBadRequest("Invalid request format")
    """


class ComfoConnectInternalError(ComfoConnectError):
    """Error raised when request handling fails internally.

    Example:
        >>> raise ComfoConnectInternalError("Internal processing error")
    """


class ComfoConnectNotReachable(ComfoConnectError):
    """Error raised when the backend cannot route the request.

    Example:
        >>> raise ComfoConnectNotReachable("Backend not reachable")
    """


class ComfoConnectOtherSession(ComfoConnectError):
    """Error raised when another client has an active session.

    Example:
        >>> raise ComfoConnectOtherSession("Session already active")
    """


class ComfoConnectNotAllowed(ComfoConnectError):
    """Error raised when the request is not allowed.

    Example:
        >>> raise ComfoConnectNotAllowed("Request not allowed")
    """


class ComfoConnectNoResources(ComfoConnectError):
    """Error raised when resources are insufficient to complete the request.

    Example:
        >>> raise ComfoConnectNoResources("Not enough memory")
    """


class ComfoConnectNotExist(ComfoConnectError):
    """Error raised when a ComfoNet node or property does not exist.

    Example:
        >>> raise ComfoConnectNotExist("Node does not exist")
    """


class ComfoConnectRmiError(ComfoConnectError):
    """Error raised when the RMI fails.

    Example:
        >>> raise ComfoConnectRmiError("RMI error response")
    """


class AioComfoConnectNotConnected(Exception):
    """Error raised when the bridge is not connected.

    Example:
        >>> raise AioComfoConnectNotConnected("Bridge not connected")
    """


class AioComfoConnectTimeout(Exception):
    """Error raised when the bridge does not reply in time.

    Example:
        >>> raise AioComfoConnectTimeout("Bridge timeout")
    """


class BridgeNotFoundException(Exception):
    """Error raised when no bridge is found.

    Example:
        >>> raise BridgeNotFoundException("No bridge found")
    """


class UnknownActionException(Exception):
    """Error raised when an unknown action is provided.

    Example:
        >>> raise UnknownActionException("Unknown action")
    """
