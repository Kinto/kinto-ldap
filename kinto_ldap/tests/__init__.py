try:
    import unittest2 as unittest
except ImportError:
    import unittest

from kinto.tests.core.support import DummyRequest


__all__ = (DummyRequest, unittest)
