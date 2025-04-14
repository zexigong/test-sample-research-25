import hug
from falcon import testing


@hug.get()
def echo(body):
    return body


def test_content_type():
    api = hug.API(__name__)

    @hug.format.content_type("text/yaml")
    def yaml(data, **kwargs):
        return data

    @hug.format.content_type("application/json")
    def json(data, **kwargs):
        return data

    @hug.format.content_type("application/xml")
    def xml(data, **kwargs):
        return data

    data = {"key1": "value1", "key2": "value2"}
    suffixes = {"yaml": yaml, "json": json, "xml": xml}
    hug.transform.content_type(
        {
            "text/yaml": yaml,
            "application/json": json,
            "application/xml": xml,
        },
        default=json,
    )(echo)
    for suffix in suffixes:
        echo(data, request=testing.create_environ(content_type=suffix))


def test_suffix():
    api = hug.API(__name__)

    @hug.format.content_type("text/yaml")
    def yaml(data, **kwargs):
        return data

    @hug.format.content_type("application/json")
    def json(data, **kwargs):
        return data

    @hug.format.content_type("application/xml")
    def xml(data, **kwargs):
        return data

    data = {"key1": "value1", "key2": "value2"}
    suffixes = {"yaml": yaml, "json": json, "xml": xml}
    hug.transform.suffix(suffixes, default=json)(echo)
    for suffix in suffixes:
        echo(data, request=testing.create_environ(path=f"/{suffix}"))


def test_prefix():
    api = hug.API(__name__)

    @hug.format.content_type("text/yaml")
    def yaml(data, **kwargs):
        return data

    @hug.format.content_type("application/json")
    def json(data, **kwargs):
        return data

    @hug.format.content_type("application/xml")
    def xml(data, **kwargs):
        return data

    data = {"key1": "value1", "key2": "value2"}
    suffixes = {"yaml": yaml, "json": json, "xml": xml}
    hug.transform.prefix(suffixes, default=json)(echo)
    for suffix in suffixes:
        echo(data, request=testing.create_environ(path=f"/{suffix}"))


def test_all():
    api = hug.API(__name__)

    @hug.format.content_type("text/yaml")
    def yaml(data, **kwargs):
        return data

    @hug.format.content_type("application/json")
    def json(data, **kwargs):
        return data

    @hug.format.content_type("application/xml")
    def xml(data, **kwargs):
        return data

    data = {"key1": "value1", "key2": "value2"}
    suffixes = {"yaml": yaml, "json": json, "xml": xml}
    hug.transform.all(
        hug.transform.prefix(suffixes, default=json),
        hug.transform.suffix(suffixes, default=json),
        hug.transform.content_type(
            {
                "text/yaml": yaml,
                "application/json": json,
                "application/xml": xml,
            },
            default=json,
        ),
    )(echo)
    for suffix in suffixes:
        echo(data, request=testing.create_environ(content_type=suffix, path=f"/{suffix}"))