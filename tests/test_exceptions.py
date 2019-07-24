from marshmallow.exceptions import MarshmallowError, ValidationError

from star_resty.exceptions import StartRestDumpError


def test_dump_error_normalize():
    e = StartRestDumpError()
    assert e.normalized_messages() == {'_schema': 'Error dump content'}

    e = StartRestDumpError(exc=MarshmallowError())
    assert e.normalized_messages() == {'_schema': 'Error dump content'}

    e = StartRestDumpError(exc=ValidationError({'a': ['Type error']}))
    assert e.normalized_messages() == {'a': ['Type error']}
