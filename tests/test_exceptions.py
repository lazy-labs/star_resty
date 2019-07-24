from marshmallow.exceptions import MarshmallowError, ValidationError

from star_resty.exceptions import DumpError


def test_dump_error_normalize():
    e = DumpError()
    assert e.normalized_messages() == {'_schema': 'Error dump content'}

    e = DumpError(exc=MarshmallowError())
    assert e.normalized_messages() == {'_schema': 'Error dump content'}

    e = DumpError(exc=ValidationError({'a': ['Type error']}))
    assert e.normalized_messages() == {'a': ['Type error']}
