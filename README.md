# GraphSense TagPacks

A TagPack is a collection of cryptocurrency attribution tags with associated
provenance and categorization metadata. This repository defines a common
structure for TagPacks, provides the Git infrastructure for collaboratively
collecting TagPacks with detailed provenance information, and the necessary
scripts for ingesting TagPacks into GraphSense for further processing.

## What is an attribution tag?

An attribution tag is any form of context information that can be attributed to
a cryptocurrency address. The following example attributes a Bitcoin address to
the Internet Archive, which is, according to
[this source](https://archive.org/donate/cryptocurrency/), the holder of that
address:

    label: Internet Archive
    address: 1Archive1n2C579dMsAu3iC6tWzuQJz8dN
    source: https://archive.org/donate/cryptocurrency/

## Why are attribution tags important?

Cryptocurrency analytics relies on two complementary techniques: **address
clustering heuristics**, which are used to group multiple addresses into
maximal subsets that can likely be assigned to the same real-world actor, and
**attribution tags** as shown above. The strength lies in the combination of
these techniques: a tag attributed to a single address belonging to a larger
cluster can easily add contextual information to hundreds of thousands
cryptocurrency addresses.

**Note**: certain types of transactions (e.g., CoinJoins, Mixing Services) can
distort clustering results and lead to false, unreliable, or intentionally
misplaced attribution tags that could associate unrelated actors with a given
cluster.

## What is a TagPack?

A TagPack defines a structure for collecting and packaging attribution tags
with additional provenance information (e.g., creator, last modification
datetime, etc.). TagPacks can be shared via some Git-Service (Github in this
case), which enables version control and recording of modifications.

TagPacks are represented as [YAML](https://yaml.org/) files, which can easily
be created by hand or exported automatically from other systems. A tag pack
defines a **header** with a number of mandatory and optional fields and a
**body** containing a list of tags.

Here is a minimal TagPack example with mandatory properties:

    ---
    title: First TagPack Example
    creator: John Doe
    lastmod: 2019-03-15
    currency: BTC
    tags:
        - label: Internet Archive
          address: 1Archive1n2C579dMsAu3iC6tWzuQJz8dN
          source: https://archive.org/donate/cryptocurrency/
        - label: Example
          address: 1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2
          source: https://example.com

Body fields placed within a TagPack header (in the above example: `lastmod`,
`currency`) apply to all tags in the body and are automatically inherited by
each tag. Thus, in the above example `John Doe` is the creator of two tags that
assign human-readable labels to Bitcoin (BTC) addresses.

Please note that next to the `label` and `address` fields, the `source`
property is mandatory as it describes where a certain piece of information is
coming from (either in the form of a URI or a textual description). Thus it
must either appear in the header or as part of a single tag.

TagPack properties can also be associated on the tag-level and overwrite header
property values:

    ---
    title: Second TagPack Example
    creator: John Doe
    description: A collection of tags commonly used for demonstrating GraphSense features
    lastmod: 2019-03-15
    label: Internet Archive
    source: https://archive.org/donate/cryptocurrency
    category: Organization
    tags:
        - address: 1Archive1n2C579dMsAu3iC6tWzuQJz8dN
          currency: BTC
        - address: 1K1rgZ1dz9w7dsR1HGS1drmzfUHMtqx1Tc
          currency: BCH
        - address: "0xFA8E3920daF271daB92Be9B87d9998DDd94FEF08"
          currency: ETH
        - address: rGeyCsqc6vKXuyTGF39WJxmTRemoV3c97h
          currency: XRP
        - address: t1ZmpK4QFcvyQZ3ghTgSboBW8b4HgiZHQF9
          currency: ZEC
          lastmod: 2019-04-16


Above example shows several tags associating addresses from various
cryptocurrencies with the label `Internet Archive`. Most of them were collected
at the same time (2019-03-15), except the Zcash tag that has been collected
and added later (2019-03-20).

## How are Tags and TagPacks identified

A tag is treated as a first-class object and is unique across TagPacks. That
implies that the same label (e.g., `Internet Archive`) can be assigned several
times to the same address (e.g., `1Archive1n2C579dMsAu3iC6tWzuQJz8dN`),
typically by different parties.

Since TagPacks are essentially files pushed to some Git repository, they can be
uniquely identified by their Git URI
(e.g., `https://github.com/graphsense/graphsense-tagpacks/blob/master/packs/demo.yaml`).

The URI identifier of a TagPack is set in `config.yaml` in the root folder of each TagPack.

## How can I configure my local TagPack environment

In `config.yaml`, the base URI and the Cassandra keyspace are specified:

    baseURI: https://github.com/graphsense/graphsense-tagpacks
    targetKeyspace: tagpacks

## Which fields and categories can be used?

Permitted fields and categorization information can be defined by
adding them to the schema file (`schema.yaml`) of a TagPack repository.

That file also defines supported categories and possible forms of abuses.

    fields:
      header:
        - title
        - creator
        - description
        - tags
      tag:
        - address
        - label
        - source
        - currency
        - category
        - lastmod
        - abuse
      categories:
        - Exchange
        - Wallet Service
        - Miner
        - Marketplace
        - Gambling
        - Mixing Service
        - Other
        - Unspecified
      abuses:
        - Scam
        - Sextortion
        - Hack
        - Ransomware
        - Ponzi Scheme

Please note that additional fields must also be considered in the schema
definition (`./packs/schema_tagpacks.yaml`) when needed for further processing.


## How can I contribute TagPacks to this repository?

**Step 1**: [Fork](https://help.github.com/en/articles/fork-a-repo) this repository

**Step 2**: Add your TagPacks to the folder `packs`

**Step 3**: Validate your TagPack `./scripts/tag_pack_tool.py validate packs/demo.yaml`

**Step 4**: Contribute them to GraphSense public TagPack collection by submitting a [pull request](https://help.github.com/en/articles/about-pull-requests)

## What kind of tags will be accepted in the public GraphSense TagPack repository?

All pull requests will be reviewed by the GraphSense core development team and
only be accepted if the following conditions are met:

1.) None of the tags contains personally identifiable information (PII)

2.) All tags originate from public sources

3.) All tags provide a dereferenceable pointer to their origin

TagPacks not fulfilling above criteria can be maintained in some private
 Git repositories.

## How can I ingest TagPacks into my local GraphSense instance

Ensure that there is a keyspace `tagpacks` in your local Cassandra instance.

    ./scripts/create_tagpack_schema.sh

Put your TagPacks in the `packs` subfolder and validate and ingest them:

    ./scripts/tag_pack_tool.py validate <root_folder>
    ./scripts/tag_pack_tool.py ingest <root_folder>

The argument `<root_folder>` is by default the current folder, but it can be 
set to another TagPack folder with different `config.yaml` and `packs`.

When ingesting TagPacks, you can specify the batch size to improve performances 
with the `-b` parameter (default is 500).

After ingesting new TagPacks you should re-run the
[graphsense-transformation](https://github.com/graphsense/graphsense-transformation)
job in order to propagate newly added tags over all computation steps.
