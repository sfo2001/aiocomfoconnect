"""Unit tests for Exception classes."""

import pytest
from aiocomfoconnect.exceptions import (
    ComfoConnectError,
    ComfoConnectBadRequest,
    ComfoConnectInternalError,
    ComfoConnectNotReachable,
    ComfoConnectOtherSession,
    ComfoConnectNotAllowed,
    ComfoConnectNoResources,
    ComfoConnectNotExist,
    ComfoConnectRmiError,
    AioComfoConnectNotConnected,
    AioComfoConnectTimeout,
    BridgeNotFoundException,
    UnknownActionException,
)


class TestComfoConnectError:
    """Test ComfoConnectError base exception."""
    
    def test_init(self):
        """Test ComfoConnectError initialization."""
        message = "Test error message"
        error = ComfoConnectError(message)
        
        assert str(error) == message
        assert error.message == message
    
    def test_inheritance(self):
        """Test ComfoConnectError inheritance."""
        error = ComfoConnectError("test")
        assert isinstance(error, Exception)
    
    def test_raise_and_catch(self):
        """Test raising and catching ComfoConnectError."""
        message = "Test error"
        
        with pytest.raises(ComfoConnectError) as exc_info:
            raise ComfoConnectError(message)
        
        assert str(exc_info.value) == message
        assert exc_info.value.message == message


class TestComfoConnectBadRequest:
    """Test ComfoConnectBadRequest exception."""
    
    def test_inheritance(self):
        """Test ComfoConnectBadRequest inheritance."""
        error = ComfoConnectBadRequest("test")
        assert isinstance(error, ComfoConnectError)
        assert isinstance(error, Exception)
    
    def test_raise_and_catch(self):
        """Test raising and catching ComfoConnectBadRequest."""
        message = "Bad request"
        
        with pytest.raises(ComfoConnectBadRequest) as exc_info:
            raise ComfoConnectBadRequest(message)
        
        assert str(exc_info.value) == message
    
    def test_catch_as_base_class(self):
        """Test catching ComfoConnectBadRequest as base ComfoConnectError."""
        message = "Bad request"
        
        with pytest.raises(ComfoConnectError) as exc_info:
            raise ComfoConnectBadRequest(message)
        
        assert isinstance(exc_info.value, ComfoConnectBadRequest)


class TestComfoConnectInternalError:
    """Test ComfoConnectInternalError exception."""
    
    def test_inheritance(self):
        """Test ComfoConnectInternalError inheritance."""
        error = ComfoConnectInternalError("test")
        assert isinstance(error, ComfoConnectError)
    
    def test_raise_and_catch(self):
        """Test raising and catching ComfoConnectInternalError."""
        message = "Internal error"
        
        with pytest.raises(ComfoConnectInternalError) as exc_info:
            raise ComfoConnectInternalError(message)
        
        assert str(exc_info.value) == message


class TestComfoConnectNotReachable:
    """Test ComfoConnectNotReachable exception."""
    
    def test_inheritance(self):
        """Test ComfoConnectNotReachable inheritance."""
        error = ComfoConnectNotReachable("test")
        assert isinstance(error, ComfoConnectError)
    
    def test_raise_and_catch(self):
        """Test raising and catching ComfoConnectNotReachable."""
        message = "Not reachable"
        
        with pytest.raises(ComfoConnectNotReachable) as exc_info:
            raise ComfoConnectNotReachable(message)
        
        assert str(exc_info.value) == message


class TestComfoConnectOtherSession:
    """Test ComfoConnectOtherSession exception."""
    
    def test_inheritance(self):
        """Test ComfoConnectOtherSession inheritance."""
        error = ComfoConnectOtherSession("test")
        assert isinstance(error, ComfoConnectError)
    
    def test_raise_and_catch(self):
        """Test raising and catching ComfoConnectOtherSession."""
        message = "Other session active"
        
        with pytest.raises(ComfoConnectOtherSession) as exc_info:
            raise ComfoConnectOtherSession(message)
        
        assert str(exc_info.value) == message


class TestComfoConnectNotAllowed:
    """Test ComfoConnectNotAllowed exception."""
    
    def test_inheritance(self):
        """Test ComfoConnectNotAllowed inheritance."""
        error = ComfoConnectNotAllowed("test")
        assert isinstance(error, ComfoConnectError)
    
    def test_raise_and_catch(self):
        """Test raising and catching ComfoConnectNotAllowed."""
        message = "Not allowed"
        
        with pytest.raises(ComfoConnectNotAllowed) as exc_info:
            raise ComfoConnectNotAllowed(message)
        
        assert str(exc_info.value) == message


class TestComfoConnectNoResources:
    """Test ComfoConnectNoResources exception."""
    
    def test_inheritance(self):
        """Test ComfoConnectNoResources inheritance."""
        error = ComfoConnectNoResources("test")
        assert isinstance(error, ComfoConnectError)
    
    def test_raise_and_catch(self):
        """Test raising and catching ComfoConnectNoResources."""
        message = "No resources"
        
        with pytest.raises(ComfoConnectNoResources) as exc_info:
            raise ComfoConnectNoResources(message)
        
        assert str(exc_info.value) == message


class TestComfoConnectNotExist:
    """Test ComfoConnectNotExist exception."""
    
    def test_inheritance(self):
        """Test ComfoConnectNotExist inheritance."""
        error = ComfoConnectNotExist("test")
        assert isinstance(error, ComfoConnectError)
    
    def test_raise_and_catch(self):
        """Test raising and catching ComfoConnectNotExist."""
        message = "Does not exist"
        
        with pytest.raises(ComfoConnectNotExist) as exc_info:
            raise ComfoConnectNotExist(message)
        
        assert str(exc_info.value) == message


class TestComfoConnectRmiError:
    """Test ComfoConnectRmiError exception."""
    
    def test_inheritance(self):
        """Test ComfoConnectRmiError inheritance."""
        error = ComfoConnectRmiError("test")
        assert isinstance(error, ComfoConnectError)
    
    def test_raise_and_catch(self):
        """Test raising and catching ComfoConnectRmiError."""
        message = "RMI error"
        
        with pytest.raises(ComfoConnectRmiError) as exc_info:
            raise ComfoConnectRmiError(message)
        
        assert str(exc_info.value) == message


class TestAioComfoConnectNotConnected:
    """Test AioComfoConnectNotConnected exception."""
    
    def test_inheritance(self):
        """Test AioComfoConnectNotConnected inheritance."""
        error = AioComfoConnectNotConnected("test")
        assert isinstance(error, Exception)
        assert not isinstance(error, ComfoConnectError)
    
    def test_raise_and_catch(self):
        """Test raising and catching AioComfoConnectNotConnected."""
        message = "Not connected"
        
        with pytest.raises(AioComfoConnectNotConnected) as exc_info:
            raise AioComfoConnectNotConnected(message)
        
        assert str(exc_info.value) == message


class TestAioComfoConnectTimeout:
    """Test AioComfoConnectTimeout exception."""
    
    def test_inheritance(self):
        """Test AioComfoConnectTimeout inheritance."""
        error = AioComfoConnectTimeout("test")
        assert isinstance(error, Exception)
        assert not isinstance(error, ComfoConnectError)
    
    def test_raise_and_catch(self):
        """Test raising and catching AioComfoConnectTimeout."""
        message = "Timeout"
        
        with pytest.raises(AioComfoConnectTimeout) as exc_info:
            raise AioComfoConnectTimeout(message)
        
        assert str(exc_info.value) == message


class TestBridgeNotFoundException:
    """Test BridgeNotFoundException exception."""
    
    def test_inheritance(self):
        """Test BridgeNotFoundException inheritance."""
        error = BridgeNotFoundException("test")
        assert isinstance(error, Exception)
        assert not isinstance(error, ComfoConnectError)
    
    def test_raise_and_catch(self):
        """Test raising and catching BridgeNotFoundException."""
        message = "Bridge not found"
        
        with pytest.raises(BridgeNotFoundException) as exc_info:
            raise BridgeNotFoundException(message)
        
        assert str(exc_info.value) == message


class TestUnknownActionException:
    """Test UnknownActionException exception."""
    
    def test_inheritance(self):
        """Test UnknownActionException inheritance."""
        error = UnknownActionException("test")
        assert isinstance(error, Exception)
        assert not isinstance(error, ComfoConnectError)
    
    def test_raise_and_catch(self):
        """Test raising and catching UnknownActionException."""
        message = "Unknown action"
        
        with pytest.raises(UnknownActionException) as exc_info:
            raise UnknownActionException(message)
        
        assert str(exc_info.value) == message


class TestExceptionHierarchy:
    """Test exception hierarchy and relationships."""
    
    def test_comfoconnect_error_hierarchy(self):
        """Test that all ComfoConnect* exceptions inherit from ComfoConnectError."""
        comfoconnect_exceptions = [
            ComfoConnectBadRequest,
            ComfoConnectInternalError,
            ComfoConnectNotReachable,
            ComfoConnectOtherSession,
            ComfoConnectNotAllowed,
            ComfoConnectNoResources,
            ComfoConnectNotExist,
            ComfoConnectRmiError,
        ]
        
        for exception_class in comfoconnect_exceptions:
            error = exception_class("test")
            assert isinstance(error, ComfoConnectError)
            assert isinstance(error, Exception)
    
    def test_aio_exceptions_separate_hierarchy(self):
        """Test that Aio* exceptions don't inherit from ComfoConnectError."""
        aio_exceptions = [
            AioComfoConnectNotConnected,
            AioComfoConnectTimeout,
        ]
        
        for exception_class in aio_exceptions:
            error = exception_class("test")
            assert not isinstance(error, ComfoConnectError)
            assert isinstance(error, Exception)
    
    def test_other_exceptions_separate_hierarchy(self):
        """Test that other exceptions don't inherit from ComfoConnectError."""
        other_exceptions = [
            BridgeNotFoundException,
            UnknownActionException,
        ]
        
        for exception_class in other_exceptions:
            error = exception_class("test")
            assert not isinstance(error, ComfoConnectError)
            assert isinstance(error, Exception)