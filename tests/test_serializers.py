from start_resty.serializers import JsonSerializer


def test_serialize_json():
    serializer = JsonSerializer()
    assert serializer.media_type == 'application/json'
    assert serializer.render({'items': [1, 2, 3]}) == b'{"items":[1,2,3]}'
