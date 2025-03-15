from twisted.test_formmethod import formmethod


def test_coerce_string():
    string = formmethod.String("test")
    assert string.coerce("123") == "123"
    string = formmethod.String("test", min=3, max=6)
    assert string.coerce("123") == "123"
    assert string.coerce("123456") == "123456"


def test_coerce_text():
    text = formmethod.Text("test")
    assert text.coerce("123") == "123"
    text = formmethod.Text("test", min=3, max=6)
    assert text.coerce("123") == "123"
    assert text.coerce("123456") == "123456"


def test_coerce_password():
    password = formmethod.Password("test")
    assert password.coerce("123") == "123"
    password = formmethod.Password("test", min=3, max=6)
    assert password.coerce("123") == "123"
    assert password.coerce("123456") == "123456"


def test_coerce_verified_password():
    verified_password = formmethod.VerifiedPassword("test")
    assert verified_password.coerce(["123", "123"]) == "123"
    verified_password = formmethod.VerifiedPassword("test", min=3, max=6)
    assert verified_password.coerce(["123", "123"]) == "123"
    assert verified_password.coerce(["123456", "123456"]) == "123456"


def test_coerce_hidden():
    hidden = formmethod.Hidden("test")
    assert hidden.coerce("123") == "123"
    hidden = formmethod.Hidden("test", min=3, max=6)
    assert hidden.coerce("123") == "123"
    assert hidden.coerce("123456") == "123456"


def test_coerce_integer():
    integer = formmethod.Integer("test")
    assert integer.coerce("123") == 123
    assert integer.coerce("0") == 0


def test_coerce_integer_range():
    integer_range = formmethod.IntegerRange("test", 3, 6)
    assert integer_range.coerce("3") == 3
    assert integer_range.coerce("6") == 6


def test_coerce_float():
    float_value = formmethod.Float("test")
    assert float_value.coerce("123.45") == 123.45
    assert float_value.coerce("0.0") == 0.0


def test_coerce_choice():
    choice = formmethod.Choice("test", [("a", 1, "A"), ("b", 2, "B")])
    assert choice.coerce("a") == 1
    assert choice.coerce("b") == 2


def test_coerce_flags():
    flags = formmethod.Flags("test", [("a", 1, "A"), ("b", 2, "B")])
    assert flags.coerce(["a", "b"]) == [1, 2]
    assert flags.coerce(["a"]) == [1]


def test_coerce_check_group():
    check_group = formmethod.CheckGroup("test", [("a", 1, "A"), ("b", 2, "B")])
    assert check_group.coerce(["a", "b"]) == [1, 2]
    assert check_group.coerce(["a"]) == [1]


def test_coerce_radio_group():
    radio_group = formmethod.RadioGroup("test", [("a", 1, "A"), ("b", 2, "B")])
    assert radio_group.coerce("a") == 1
    assert radio_group.coerce("b") == 2


def test_coerce_boolean():
    boolean = formmethod.Boolean("test")
    assert boolean.coerce("True") == 1
    assert boolean.coerce("False") == 0


def test_coerce_file():
    file = formmethod.File("test")
    assert file.coerce("file.txt") == "file.txt"


def test_coerce_date():
    date = formmethod.Date("test")
    assert date.coerce(["2023", "03", "15"]) == (2023, 3, 15)
    assert date.coerce(["1970", "01", "01"]) == (1970, 1, 1)


def test_coerce_submit():
    submit = formmethod.Submit("test")
    assert submit.coerce("submit") == "submit"


def test_get_argument():
    signature = formmethod.MethodSignature(
        formmethod.Integer("test1"), formmethod.String("test2")
    )
    assert signature.getArgument("test1").name == "test1"
    assert signature.getArgument("test2").name == "test2"


def test_get_args():
    signature = formmethod.MethodSignature(
        formmethod.Integer("test1"), formmethod.String("test2")
    )
    form_method = signature.method(lambda: None)
    args = form_method.getArgs()
    assert args[0].name == "test1"
    assert args[1].name == "test2"


def test_form_method_call():
    signature = formmethod.MethodSignature(
        formmethod.Integer("test1"), formmethod.String("test2")
    )
    form_method = signature.method(lambda x, y: x + int(y))
    assert form_method.call(1, "2") == 3