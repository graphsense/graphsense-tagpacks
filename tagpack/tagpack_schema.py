"""TagPack - A wrappers TagPack Schema"""
import datetime
import os
import sys
import yaml


TAGPACK_SCHEMA_FILE = 'tagpack/conf/tagpack_schema.yaml'


class ValidationError(Exception):
    """Class for schema validation errors"""

    def __init__(self, message):
        super().__init__("Schema Validation Error: " + message)


class TagPackSchema(object):
    """Defines the structure of a TagPack and supports validation"""

    def __init__(self):
        self.load_schema()
        self.definition = TAGPACK_SCHEMA_FILE

    def load_schema(self):
        if not os.path.isfile(TAGPACK_SCHEMA_FILE):
            sys.exit("This program requires a schema config file in {}"
                     .format(TAGPACK_SCHEMA_FILE))
        self.schema = yaml.safe_load(open(TAGPACK_SCHEMA_FILE, 'r'))

    @property
    def header_fields(self):
        return {k: v for k, v in self.schema['header'].items()}

    @property
    def mandatory_header_fields(self):
        return {k: v for k, v in self.schema['header'].items()
                if v['mandatory']}

    @property
    def tag_fields(self):
        return {k: v for k, v in self.schema['tag'].items()}

    @property
    def mandatory_tag_fields(self):
        return {k: v for k, v in self.schema['tag'].items()
                if v['mandatory']}

    @property
    def all_fields(self):
        """Returns all TagPack header and Tag fields"""
        header_tag_fields = dict(list(self.schema['header'].items()) +
                                 list(self.schema['tag'].items()))
        return header_tag_fields

    def field_type(self, field):
        return self.all_fields[field]['type']

    def field_taxonomy(self, field):
        return self.all_fields[field].get('taxonomy')

    def _check_types(self, field, value):
        """Checks whether a field's type matches the defintion"""
        schema_type = self.field_type(field)
        if schema_type == 'text':
            if not isinstance(value, str):
                raise ValidationError("Field {} must be of type text"
                                      .format(field))
        elif schema_type == 'datetime':
            if not isinstance(value, datetime.date):
                raise ValidationError("Field {} must be of type datetime"
                                      .format(field))
        elif schema_type == 'list':
            if not isinstance(value, list):
                raise ValidationError("Field {} must be of type list")
        else:
            raise ValidationError("Unsupported schema type {}"
                                  .format(schema_type))

    def _check_taxonomies(self, field, value, taxonomies):
        """Checks whether a field uses values from a given taxonomy"""
        if taxonomies and self.field_taxonomy(field):
            expected_taxonomy_id = self.field_taxonomy(field)
            expected_taxonomy = taxonomies.get(expected_taxonomy_id)

            if expected_taxonomy is None:
                raise ValidationError("Unknown taxonomy {}"
                                      .format(expected_taxonomy_id))

            if value not in expected_taxonomy.concept_ids:
                raise ValidationError("Undefined concept {} in field {}"
                                      .format(value, field))

    def validate(self, tagpack, taxonomies):
        """Validates a tagpack against this schema and used taxonmomies"""

        # check if mandatory header fields are used by a tagpack
        for schema_field in self.mandatory_header_fields:
            if schema_field not in tagpack.header_fields:
                raise ValidationError("Mandatory field {} missing"
                                      .format(schema_field))

        # check header fields' types, taxonomy and mandatory use
        for field, value in tagpack.all_header_fields.items():
            # check a field is defined
            if field not in self.all_fields:
                raise ValidationError("Field {} not allowed in header"
                                      .format(field))

            self._check_types(field, value)
            self._check_taxonomies(field, value, taxonomies)

        # iterate over all tags and check types, taxonomy and mandatory use
        for tag in tagpack.tags:

            # check if mandatory tag fields are defined
            for schema_field in self.mandatory_tag_fields:
                if schema_field not in tag.explicit_fields and \
                   schema_field not in tagpack.generic_tag_fields:
                    raise ValidationError("Mandatory field {} missing"
                                          .format(schema_field))

            for field, value in tag.explicit_fields.items():
                # check whether field is defined as body field
                if field not in self.tag_fields:
                    raise ValidationError("Field {} not allowed in tag"
                                          .format(field))

                # check types and taxomomy use
                self._check_types(field, value)
                self._check_taxonomies(field, value, taxonomies)
