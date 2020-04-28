import datetime
import pytest

from tagpack.tagpack_schema import TagPackSchema
from tagpack.tagpack import TagPack, Tag, fields_to_timestamp, TagPackFileError


TEST_SCHEMA = 'tests/testfiles/schema_1.yaml'
TEST_TAGPACK = 'tests/testfiles/tagpack_ok.yaml'


@pytest.fixture
def schema(monkeypatch):
    monkeypatch.setattr('tagpack.tagpack_schema.TAGPACK_SCHEMA_FILE',
                        TEST_SCHEMA)
    return TagPackSchema()


@pytest.fixture
def tagpack(schema):
    return TagPack('http://example.com',
                   TEST_TAGPACK,
                   schema)


def test_init(tagpack):
    assert tagpack.baseuri == 'http://example.com'
    assert tagpack.filename == \
        'tests/testfiles/tagpack_ok.yaml'
    assert tagpack.schema.definition == TEST_SCHEMA


def test_init_fail_invalid_file(schema):
    with pytest.raises(TagPackFileError) as e:
        TagPack('http://example.com',
                'tests/testfiles/tagpack_fail_invalid_file.yaml',
                schema)
    assert "Cannot extract TagPack fields" in str(e.value)


def test_tagpack_uri(tagpack):
    assert tagpack.tagpack_uri == \
        'http://example.com/tests/testfiles/tagpack_ok.yaml'


def test_all_header_fields(tagpack):
    assert all(field in tagpack.all_header_fields
               for field in ['title', 'creator', 'lastmod', 'tags'])


def test_header_fields(tagpack):
    assert all(field in tagpack.all_header_fields
               for field in ['title', 'creator'])


def test_generic_tag_fields(tagpack):
    assert all(field in tagpack.generic_tag_fields
               for field in ['lastmod'])


def test_tagpack_to_json(tagpack):
    json = tagpack.to_json()
    assert 'uri' in json
    assert 'title' in json
    assert 'creator' in json
    assert 'lastmod' not in json


def test_tagpack_to_str(tagpack):
    s = tagpack.__str__()
    assert 'Test TagPack' in s
    assert 'GraphSense Developer' in s


def test_tags(tagpack):
    assert len(tagpack.tags) == 2


def test_tags_explicit_fields(tagpack):
    for tag in tagpack.tags:
        assert all(field in tag.explicit_fields
                   for field in ['address', 'label'])


def test_tags_fields(tagpack):
    for tag in tagpack.tags:
        assert isinstance(tag, Tag)
        assert all(field in tag.fields
                   for field in ['address', 'label', 'lastmod'])
        assert isinstance(tag.fields['lastmod'], int)


def test_fields_to_timestamp():
    test_dict = {'lastmod': datetime.date(1970, 1, 2)}
    result = fields_to_timestamp(test_dict)
    assert isinstance(result['lastmod'], int)


def test_tag_to_json(tagpack):
    for tag in tagpack.tags:
        json = tag.to_json()
        assert 'tagpack_uri' in json
        assert 'lastmod' in json
        assert 'address' in json
        assert 'label' in json


def test_tag_to_str(tagpack):
    for tag in tagpack.tags:
        tag_string = tag.__str__()
        assert '1562104800' in tag_string
        if tag.fields['address'] == '1bacdeddg32dsfk5692dmn23':
            assert '1bacdeddg32dsfk5692dmn23' in tag_string
        elif tag.fields['address'] == '3bacadsfg3sdfafd2deddg32':
            assert '3bacadsfg3sdfafd2deddg32' in tag_string