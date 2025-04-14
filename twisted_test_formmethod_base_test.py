from twisted.trial import unittest
from twisted.test.test_formmethod import (
    FormException,
    InputError,
    Argument,
    String,
    Text,
    Password,
    VerifiedPassword,
    Hidden,
    Integer,
    IntegerRange,
    Float,
    Choice,
    Flags,
    CheckGroup,
    RadioGroup,
    Boolean,
    File,
    Date,
    Submit,
    MethodSignature,
    FormMethod,
)


class FormMethodTests(unittest.TestCase):
    def test_form_exception(self):
        exception = FormException("Error occurred", description="Test error")
        self.assertEqual(str(exception), "Error occurred")
        self.assertEqual(exception.descriptions["description"], "Test error")

    def test_input_error(self):
        exception = InputError("Input error occurred")
        self.assertEqual(str(exception), "Input error occurred")

    def test_string_coerce(self):
        arg = String(name="testString", min=2, max=5)
        self.assertEqual(arg.coerce("test"), "test")
        self.assertRaises(InputError, arg.coerce, "t")
        self.assertRaises(InputError, arg.coerce, "toolong")

    def test_verified_password_coerce(self):
        arg = VerifiedPassword(name="password", min=3, max=8)
        self.assertEqual(arg.coerce(("pass", "pass")), "pass")
        self.assertRaises(InputError, arg.coerce, ("pass", "fail"))
        self.assertRaises(InputError, arg.coerce, ("short", "short"))

    def test_integer_coerce(self):
        arg = Integer(name="testInteger")
        self.assertEqual(arg.coerce("10"), 10)
        self.assertRaises(InputError, arg.coerce, "abc")

    def test_integer_range_coerce(self):
        arg = IntegerRange(name="range", min=1, max=10)
        self.assertEqual(arg.coerce("5"), 5)
        self.assertRaises(InputError, arg.coerce, "0")
        self.assertRaises(InputError, arg.coerce, "11")

    def test_float_coerce(self):
        arg = Float(name="testFloat")
        self.assertEqual(arg.coerce("10.5"), 10.5)
        self.assertRaises(InputError, arg.coerce, "abc")

    def test_choice_coerce(self):
        choices = [("one", 1, "First"), ("two", 2, "Second")]
        arg = Choice(name="choice", choices=choices)
        self.assertEqual(arg.coerce("one"), 1)
        self.assertRaises(InputError, arg.coerce, "three")

    def test_flags_coerce(self):
        flags = [("flag1", 1, "Flag 1"), ("flag2", 2, "Flag 2")]
        arg = Flags(name="flags", flags=flags)
        self.assertEqual(arg.coerce(["flag1", "flag2"]), [1, 2])
        self.assertRaises(InputError, arg.coerce, ["invalid"])

    def test_boolean_coerce(self):
        arg = Boolean(name="boolean")
        self.assertEqual(arg.coerce("yes"), 1)
        self.assertEqual(arg.coerce("no"), 0)
        self.assertEqual(arg.coerce("true"), 1)
        self.assertEqual(arg.coerce("false"), 0)

    def test_file_coerce(self):
        arg = File(name="file", allowNone=True)
        self.assertIsNone(arg.coerce(None))
        self.assertEqual(arg.coerce("file.txt"), "file.txt")
        arg = File(name="file", allowNone=False)
        self.assertRaises(InputError, arg.coerce, None)

    def test_date_coerce(self):
        arg = Date(name="date")
        self.assertEqual(arg.coerce(("2023", "12", "31")), (2023, 12, 31))
        self.assertRaises(InputError, arg.coerce, ("2023", "02", "30"))
        self.assertRaises(InputError, arg.coerce, ("", "", ""))

    def test_submit_coerce(self):
        arg = Submit(name="submit", choices=[("Submit", "submit", "Submit form")])
        self.assertEqual(arg.coerce("Submit"), "submit")
        self.assertRaises(InputError, arg.coerce, "Invalid")

    def test_method_signature_get_argument(self):
        sig = MethodSignature(String(name="arg1"), Integer(name="arg2"))
        arg = sig.getArgument("arg1")
        self.assertIsInstance(arg, String)
        self.assertEqual(arg.name, "arg1")
        self.assertIsNone(sig.getArgument("nonexistent"))

    def test_form_method_call(self):
        def sample_callable(arg1, arg2):
            return arg1 + arg2

        sig = MethodSignature(String(name="arg1"), Integer(name="arg2"))
        form_method = FormMethod(sig, sample_callable)
        self.assertEqual(form_method.call("hello", 5), "hello5")