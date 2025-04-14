# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from io import StringIO
from typing import Any

from twisted.trial import unittest
from twisted.python.compat import intToBytes


class CompatTestCase(unittest.TestCase):
    """
    Tests for compatibility modules.
    """

    def test_intToBytes(self) -> None:
        """
        L{intToBytes} should convert an integer to C{bytes}.
        """
        self.assertEqual(b"3", intToBytes(3))

    def test_intToBytesNegative(self) -> None:
        """
        L{intToBytes} should convert a negative integer to C{bytes}.
        """
        self.assertEqual(b"-3", intToBytes(-3))

    def test_intToBytesZero(self) -> None:
        """
        L{intToBytes} should convert zero to C{bytes}.
        """
        self.assertEqual(b"0", intToBytes(0))

    def test_intToBytesTypeError(self) -> None:
        """
        L{intToBytes} raises L{TypeError} when called with a non-integer.
        """
        self.assertRaises(TypeError, intToBytes, 3.0)
        self.assertRaises(TypeError, intToBytes, "foo")
        self.assertRaises(TypeError, intToBytes, [])

    def test_intToBytesLong(self) -> None:
        """
        L{intToBytes} should convert a long integer to C{bytes}.
        """
        self.assertEqual(b"31415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679", intToBytes(31415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679))

    def test_intToBytesNegativeLong(self) -> None:
        """
        L{intToBytes} should convert a negative long integer to C{bytes}.
        """
        self.assertEqual(b"-31415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679", intToBytes(-31415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679))

    def test_intToBytesStringIO(self) -> None:
        """
        L{intToBytes} should convert a L{StringIO} object to C{bytes}.
        """
        self.assertEqual(b"3", intToBytes(StringIO("3")))

    def test_intToBytesStringIONegative(self) -> None:
        """
        L{intToBytes} should convert a negative L{StringIO} object to C{bytes}.
        """
        self.assertEqual(b"-3", intToBytes(StringIO("-3")))

    def test_intToBytesStringIOZero(self) -> None:
        """
        L{intToBytes} should convert zero L{StringIO} object to C{bytes}.
        """
        self.assertEqual(b"0", intToBytes(StringIO("0")))

    def test_intToBytesStringIOTypeError(self) -> None:
        """
        L{intToBytes} raises L{TypeError} when called with a non-integer
        L{StringIO} object.
        """
        self.assertRaises(TypeError, intToBytes, StringIO("3.0"))
        self.assertRaises(TypeError, intToBytes, StringIO("foo"))
        self.assertRaises(TypeError, intToBytes, StringIO(""))

    def test_intToBytesStringIOLong(self) -> None:
        """
        L{intToBytes} should convert a long L{StringIO} object to C{bytes}.
        """
        self.assertEqual(b"31415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679", intToBytes(StringIO("31415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679")))

    def test_intToBytesStringIONegativeLong(self) -> None:
        """
        L{intToBytes} should convert a negative long L{StringIO} object to
        C{bytes}.
        """
        self.assertEqual(b"-31415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679", intToBytes(StringIO("-31415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679")))

    def test_intToBytesStringIOEmpty(self) -> None:
        """
        L{intToBytes} raises L{TypeError} when called with an empty L{StringIO}
        object.
        """
        self.assertRaises(TypeError, intToBytes, StringIO(""))

    def test_intToBytesStringIOLeadingSpace(self) -> None:
        """
        L{intToBytes} should convert a L{StringIO} object with leading space to
        C{bytes}.
        """
        self.assertEqual(b"3", intToBytes(StringIO(" 3")))

    def test_intToBytesStringIOTrailingSpace(self) -> None:
        """
        L{intToBytes} should convert a L{StringIO} object with trailing space to
        C{bytes}.
        """
        self.assertEqual(b"3", intToBytes(StringIO("3 ")))

    def test_intToBytesStringIOLeadingTrailingSpace(self) -> None:
        """
        L{intToBytes} should convert a L{StringIO} object with leading and
        trailing space to C{bytes}.
        """
        self.assertEqual(b"3", intToBytes(StringIO(" 3 ")))

    def test_intToBytesStringIOLeadingNegativeSign(self) -> None:
        """
        L{intToBytes} should convert a L{StringIO} object with leading negative
        sign to C{bytes}.
        """
        self.assertEqual(b"-3", intToBytes(StringIO("-3")))

    def test_intToBytesStringIOTrailingNegativeSign(self) -> None:
        """
        L{intToBytes} should convert a L{StringIO} object with trailing negative
        sign to C{bytes}.
        """
        self.assertEqual(b"-3", intToBytes(StringIO("3-")))

    def test_intToBytesStringIOLeadingTrailingNegativeSign(self) -> None:
        """
        L{intToBytes} should convert a L{StringIO} object with leading and
        trailing negative sign to C{bytes}.
        """
        self.assertEqual(b"-3", intToBytes(StringIO("-3-")))

    def test_intToBytesStringIOLeadingZero(self) -> None:
        """
        L{intToBytes} should convert a L{StringIO} object with leading zero to
        C{bytes}.
        """
        self.assertEqual(b"3", intToBytes(StringIO("03")))

    def test_intToBytesStringIOTrailingZero(self) -> None:
        """
        L{intToBytes} should convert a L{StringIO} object with trailing zero to
        C{bytes}.
        """
        self.assertEqual(b"3", intToBytes(StringIO("30")))

    def test_intToBytesStringIOLeadingTrailingZero(self) -> None:
        """
        L{intToBytes} should convert a L{StringIO} object with leading and
        trailing zero to C{bytes}.
        """
        self.assertEqual(b"3", intToBytes(StringIO("030")))

    def test_intToBytesStringIOLeadingNegativeSignZero(self) -> None:
        """
        L{intToBytes} should convert a L{StringIO} object with leading negative
        sign and zero to C{bytes}.
        """
        self.assertEqual(b"-3", intToBytes(StringIO("-03")))

    def test_intToBytesStringIOTrailingNegativeSignZero(self) -> None:
        """
        L{intToBytes} should convert a L{StringIO} object with trailing negative
        sign and zero to C{bytes}.
        """
        self.assertEqual(b"-3", intToBytes(StringIO("30-")))

    def test_intToBytesStringIOLeadingTrailingNegativeSignZero(self) -> None:
        """
        L{intToBytes} should convert a L{StringIO} object with leading and
        trailing negative sign and zero to C{bytes}.
        """
        self.assertEqual(b"-3", intToBytes(StringIO("-30-")))

    def test_intToBytesStringIOLeadingSpaceNegativeSignZero(self) -> None:
        """
        L{intToBytes} should convert a L{StringIO} object with leading space,
        negative sign, and zero to C{bytes}.
        """
        self.assertEqual(b"-3", intToBytes(StringIO(" -03")))

    def test_intToBytesStringIOTrailingSpaceNegativeSignZero(self) -> None:
        """
        L{intToBytes} should convert a L{StringIO} object with trailing space,
        negative sign, and zero to C{bytes}.
        """
        self.assertEqual(b"-3", intToBytes(StringIO("30- ")))

    def test_intToBytesStringIOLeadingTrailingSpaceNegativeSignZero(self) -> None:
        """
        L{intToBytes} should convert a L{StringIO} object with leading and
        trailing space, negative sign, and zero to C{bytes}.
        """
        self.assertEqual(b"-3", intToBytes(StringIO(" -30- ")))

    def test_intToBytesStringIOLeadingTrailingSpaceZero(self) -> None:
        """
        L{intToBytes} should convert a L{StringIO} object with leading and
        trailing space and zero to C{bytes}.
        """
        self.assertEqual(b"3", intToBytes(StringIO(" 030 ")))

    def test_intToBytesStringIOLeadingTrailingSpaceNegativeSign(self) -> None:
        """
        L{intToBytes} should convert a L{StringIO} object with leading and
        trailing space and negative sign to C{bytes}.
        """
        self.assertEqual(b"-3", intToBytes(StringIO(" -3- ")))

    def test_intToBytesStringIOLeadingTrailingSpace(self) -> None:
        """
        L{intToBytes} should convert a L{StringIO} object with leading and
        trailing space to C{bytes}.
        """
        self.assertEqual(b"3", intToBytes(StringIO(" 3 ")))

    def test_intToBytesStringIOLeadingTrailingSpaceNegativeSignZeroSpace(self) -> None:
        """
        L{intToBytes} should convert a L{StringIO} object with leading and
        trailing space, negative sign, zero, and space to C{bytes}.
        """
        self.assertEqual(b"-3", intToBytes(StringIO(" - 03 - ")))

    def test_intToBytesStringIOMultiline(self) -> None:
        """
        L{intToBytes} raises L{TypeError} when called with a multiline
        L{StringIO} object.
        """
        self.assertRaises(TypeError, intToBytes, StringIO("3\n4"))

    def test_intToBytesStringIOMultilineWithLeadingSpace(self) -> None:
        """
        L{intToBytes} raises L{TypeError} when called with a multiline
        L{StringIO} object with leading space.
        """
        self.assertRaises(TypeError, intToBytes, StringIO(" 3\n4"))

    def test_intToBytesStringIOMultilineWithTrailingSpace(self) -> None:
        """
        L{intToBytes} raises L{TypeError} when called with a multiline
        L{StringIO} object with trailing space.
        """
        self.assertRaises(TypeError, intToBytes, StringIO("3\n4 "))

    def test_intToBytesStringIOMultilineWithLeadingTrailingSpace(self) -> None:
        """
        L{intToBytes} raises L{TypeError} when called with a multiline
        L{StringIO} object with leading and trailing space.
        """
        self.assertRaises(TypeError, intToBytes, StringIO(" 3\n4 "))

    def test_intToBytesStringIOMultilineWithLeadingTrailingSpaceNegativeSignZero(
        self,
    ) -> None:
        """
        L{intToBytes} raises L{TypeError} when called with a multiline
        L{StringIO} object with leading and trailing space, negative sign, and
        zero.
        """
        self.assertRaises(TypeError, intToBytes, StringIO(" - 03 \n 4 "))

    def test_intToBytesStringIOMultilineWithLeadingTrailingSpaceNegativeSignZeroSpace(
        self,
    ) -> None:
        """
        L{intToBytes} raises L{TypeError} when called with a multiline
        L{StringIO} object with leading and trailing space, negative sign, zero,
        and space.
        """
        self.assertRaises(TypeError, intToBytes, StringIO(" - 03 \n 4 "))