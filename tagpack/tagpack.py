"""TagPack - A wrapper for TagPacks files"""
import datetime
import json
import os
import sys
import time
import yaml


def fields_to_timestamp(d):
    """Converts all datetime dict entries to int (timestamp)"""
    for k, v in d.items():
        if isinstance(v, datetime.date):
            d[k] = int(time.mktime(v.timetuple()))
    return d


class TagPackFileError(Exception):
    """Class for TagPack file (structure) errors"""

    def __init__(self, message):
        super().__init__(message)


class TagPack(object):
    """Represents a TagPack"""

    def __init__(self, baseuri, filename, schema):
        self.baseuri = baseuri
        self.filename = filename
        self.schema = schema
        self.tagpack = self._load_tagpack_from_file()
        self._check_tagpack_structure()

    def _load_tagpack_from_file(self):
        if not os.path.isfile(self.filename):
            sys.exit("This program requires {} to be a file"
                     .format(self.filename))
        file = yaml.safe_load(open(self.filename, 'r'))
        return file

    def _check_tagpack_structure(self):
        self.header_fields
        self.generic_tag_fields
        if self.tagpack.get('tags') is None:
            raise TagPackFileError('Mandatory tags field is missing')

    @property
    def tagpack_uri(self):
        """Return's a TagPack's globally unique identifier"""
        return self.baseuri + '/' + self.filename

    @property
    def all_header_fields(self):
        """Returns all TagPack header fields, including generic tag fields"""
        try:
            return {k: v for k, v in self.tagpack.items()}
        except AttributeError:
            raise TagPackFileError("Cannot extract TagPack fields")

    @property
    def header_fields(self):
        """Returns TagPack header fields that are defined as such"""
        try:
            return {k: v for k, v in self.tagpack.items()
                    if k in self.schema.header_fields}
        except AttributeError:
            raise TagPackFileError("Cannot extract TagPack fields")

    @property
    def generic_tag_fields(self):
        """Returns generic tag fields defined in the TagPack header"""
        try:
            return {k: v for k, v in self.tagpack.items()
                    if k != 'tags' and k in self.schema.tag_fields}
        except AttributeError:
            raise TagPackFileError("Cannot extract TagPack fields")

    @property
    def tags(self):
        """Returns all tags defined in a TagPack's body"""
        try:
            return [Tag(tag, self) for tag in self.tagpack['tags']]
        except AttributeError:
            raise TagPackFileError("Cannot extract TagPack fields")

    def to_json(self):
        """Returns a JSON representation of a TagPack's header"""
        tagpack = {}
        tagpack['uri'] = self.tagpack_uri
        for k, v in self.header_fields.items():
            if k != 'tags':
                tagpack[k] = v
        return json.dumps(tagpack)

    def __str__(self):
        """Returns a string serialization of the entire TagPack"""
        return str(self.tagpack)


class Tag(object):
    """Represents a single Tag"""

    def __init__(self, tag, tagpack):
        self.tag = tag
        self.tagpack = tagpack

    @property
    def explicit_fields(self):
        """Return only explicitly defined tag fields"""
        return {k: v for k, v in self.tag.items()}

    @property
    def fields(self):
        """Return all tag fields (explicit and generic)"""
        tag = {}
        for k, v in self.explicit_fields.items():
            tag[k] = self.tag[k]
        for k, v in self.tagpack.generic_tag_fields.items():
            tag[k] = self.tagpack.generic_tag_fields[k]
        tag = fields_to_timestamp(tag)
        return tag

    def to_json(self):
        """Returns a JSON serialization of all tag fields"""
        tag = self.fields
        tag['tagpack_uri'] = self.tagpack.tagpack_uri
        return json.dumps(tag)

    def __str__(self):
        """"Returns a string serialization of a Tag"""
        return str(self.fields)
