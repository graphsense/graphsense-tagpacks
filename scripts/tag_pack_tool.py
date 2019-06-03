#!/usr/bin/env python3

import yaml
from yaml.parser import ParserError
from argparse import ArgumentParser

CONFIG_FILE = "config.yaml"

config = yaml.safe_load(open(CONFIG_FILE, 'r'))

config_header_fields = config['fields']['header']
config_tag_fields = config['fields']['tag']
config_categories = config['categories']


class TagPackException(Exception):
    pass


def extract_meta(tag_pack):
    tag_pack_meta = {k: v for k, v in tag_pack.items() if k in config_header_fields and k != "tags"}
    return tag_pack_meta


def extract_tags(tag_pack):
    # Retrieve generic tag fields from tag pack header
    generic_tag_fields = {k: v for k, v in tag_pack.items() if k not in config_header_fields and k != "tags"}
    # Iterate each tag and enrich them with generic fields
    for tag in tag_pack['tags']:
        final_tag = generic_tag_fields.copy()
        final_tag.update(tag)
        yield final_tag


def check_categories(d):
    for k, v in d.items():
        if isinstance(v, dict):
            check_categories(v)
        else:
            if k == 'categories' and v not in config_categories:
                return(k, v)


def verify_tag_pack(tag_pack):
    # Header should only contain header and generic body fields
    unknown_header = set(tag_pack.keys()) - \
        set(config_header_fields) - set(config_tag_fields)
    if(len(unknown_header) > 0):
        raise TagPackException(
            'Found unknown header field: {}.'.format(unknown_header))
    # Tags should only contain body fields
    for tag in tag_pack['tags']:
        unknown_tag_field = set(tag.keys()) - set(config_tag_fields)
        if(len(unknown_tag_field) > 0):
            raise TagPackException(
                'Found unknown tag field {} assigned with tag {}.'.format(unknown_tag_field, tag))
    # Check that categories are taken from defined vocabulary
    wrong_category = check_categories(tag_pack)
    if(wrong_category is not None):
        raise TagPackException(
            'Found unknown category {}'.format(wrong_category))


def validate(args):
    tag_pack_files = args.tagpacks

    try:
        for tag_pack_file in tag_pack_files:
            tag_pack = yaml.safe_load(open(tag_pack_file, 'r'))
            verify_tag_pack(tag_pack)
    except TagPackException as tagpack_error:
        print("Please check field usage:" + str(tagpack_error))
    except ParserError as parser_error:
        print("Cannot parse YAML file:" + str(parser_error))


def ingest(args):
    tag_pack_files = args.tagpacks
    db_nodes = args.db_nodes

    for tag_pack_file in tag_pack_files:
        tag_pack = yaml.safe_load(open(tag_pack_file, 'r'))
        tag_pack_meta = extract_meta(tag_pack)
        # TODO jsonify and ingest into TagPack table
        print(tag_pack_meta)
        tags = list(extract_tags(tag_pack))
        # TODO jsonify and ingest into Tags table
        print(tags)



def main():
    parser = ArgumentParser(description='TagPack validation and ingest utility',
                            epilog='GraphSense - http://graphsense.info')
    subparsers = parser.add_subparsers(title='subcommands',
                                       description='valid subcommands',
                                       help='additional help')

    # create parser for ingest command
    parser_i = subparsers.add_parser("ingest", help="Ingest TagPacks into GraphSense")
    parser_i.add_argument('-d', '--db_nodes', dest='db_nodes', nargs='+',
                        default='localhost', metavar='DB_NODE',
                        help='list of Cassandra nodes; default "localhost")')
    parser_i.set_defaults(func=ingest)

    # create parser for validate command
    parser_v = subparsers.add_parser("validate", help="Validate TagPacks")
    parser_v.set_defaults(func=validate)


    parser.add_argument("tagpacks", metavar='TAGPACK_FILE(s)', 
                                    type=str, nargs='+', help="TagPacks to be processed")

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
