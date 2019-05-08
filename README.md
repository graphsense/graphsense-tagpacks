# GraphSense TagPacks

A TagPack is a collection of cryptocurrency attribution tags with associated provenance and categorization metadata. This repository defines a common schema for TagPacks, provices the Git infrastructure for collaboratively collecting TagPacks with detailed provenance information, and the necessary scripts for ingesting TagPacks into GraphSense for further processing.

## What is an attribution tag?

An attribution tag is any form of context information that can be attributed to a cryptocurrency address. The following example attributes a Bitcoin address to the Internet Archive, which is, according to [this source][https://archive.org/donate/cryptocurrency/], the holder of that address:

	label: Internet Archive
	address: 1Archive1n2C579dMsAu3iC6tWzuQJz8dN
	source: https://archive.org/donate/cryptocurrency/

## Why are attribution tags important?

Crypocurrency analytics relies on two complentary techniques: **address clustering heuristics**, which are used to group multiple addresses into maximal subsets that can likely be assigned to the same real-world actor, and **attribution tags** as shown above. The strength lies in the combination of these techniques: a tag attributed to a single address belonging to a larger cluster can easily add contextual information to hundreds of thousands cryptocurrency addresses.

**Note**: certain types of transactions (e.g., CoinJoins, Mixing Services) can distort clustering results and lead to false, unreliable, or intentionally misplaced attribution tags could associate unrelated actors with a given cluster.

## What is a TagPack?

A TagPack defines a structure for collecting and packaging attribution tags with additional provenance information (e.g., creator, last modification datetime, etc.). TagPacks are intended to be created by users having a Git-service (in this case Github) account. This enables version control for TagPacks and records modifications as part of the Git history.

TagPacks are represented as [YAML][https://yaml.org/] files, which can easily be created by hand or exported automatically from other systems. A tag pack defines a **header** with a number of mandatory and optional fields and a **body** containing a list of tags.

Here is a minimal TagPack example with mandatory properties:

	title: First Tag Pack Example
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

Properties in the TagPack header (in the above example: title, creator, lastmod, currency) are automatically inherited by each tag. Thus, in the above example `John Doe` is the creator of two tags that assign human-readable labels to Bitcoin (BTC) addresses. The `source` property is mandatory and describes where this piece of information is coming from (either in the form of a URI or a textual description).

TagPack properties can also be associated on the tag-level and overwrite header property values:

---
	title: Example Tag Pack
	creator: John Doe
	lastmod: 2019-03-15
	tags:
		- label: Internet Archive
	      source: https://archive.org/donate/cryptocurrency/
		  addresses:
		  	- address: 1Archive1n2C579dMsAu3iC6tWzuQJz8dN	  
		  	  currency: BTC
		  	- address: qrzeh0y2uv2rdmjmkfqcmd39h9yqjrqwmqzaztef9w
		  	  currency: BCH
		  	- address: 0xFA8E3920daF271daB92Be9B87d9998DDd94FEF08
		  	  currency: ETH
		  	- address: rGeyCsqc6vKXuyTGF39WJxmTRemoV3c97h
		  	  currency: XRP
		  	- address: t1ZmpK4QFcvyQZ3ghTgSboBW8b4HgiZHQF9
		  	  currency: ZSH
		  	  lastmod: 2019-03-20

Above example shows several tags associating addresses from various cryptocurrencies with the label `Internet Archive`. Most of them were collected at the same timme (2019-03-15), except the Zcash tag that has been collected and added later (2019-03-20).

## How are Tags and TagPacks identified

A tag is treated as a first-class object and is unique across TagPacks. That implies that the same label (e.g., `Internet Archive`) can be assigned several times to the same address (e.g., `1Archive1n2C579dMsAu3iC6tWzuQJz8dN`), typically by different parties.

Since TagPacks are essentially files pushed to some Git repository, they can be uniquely identified by their Git URI (e.g., `https://github.com/graphsense/graphsense-tagpacks/packs/example.yaml`).

Uniquness of individual tags is guaranteed by computing unique tag identifiers (hashes) across the following fields:

	gitURI
	label
	address
	source

## How can I add additional fields or categorization information

Additional permitted fields and categorization information can be defined by adding them to the configuration file (`config.yaml`) of a TagPack repository.

	---
	baseURI: https://github.com/graphsense/graphsense-tagpacks
	fields:
	  header:
	    - title
	    - creator
	    - lastmod
	    - currency
	    - category
	  tags:
	    - label
	    - source
	    - address
	    - addresses
	categories:
	  - miner
	  - exchange
	  - walletprovider
	  - marketplace
	  - mixingservice

Please note that additional fields must also be considered in the schema definition (`./packs/schema_tagpacks.yaml`) when needed for further processing.


## How can I contribute TagPacks to this repository?

**Step 1**: [Fork](https://help.github.com/en/articles/fork-a-repo) this repository

**Step 2**: Add your TagPacks to the folder `packs`

**Step 3**: Contribute them to GraphSense public TagPack collection by submitting a [pull request](https://help.github.com/en/articles/about-pull-requests)


## What kind of tags will be accepted in the public GraphSense TagPack repository?

All pull requests will be reviewed by the GraphSense core development team and only be accepted if the following conditions are met:

1.) None of the tags contains personally identifyable information (PII)

2.) All tags originate from public sources

3.) All tags provide a dereferencable pointer to their origin

TagPacks not fulfilling above criteria can be maintained in some private Git repositories.

## How can I ingest TagPacks into my local GraphSense instance

Ensure that there is a keyspace `tagPacks` in your local Cassandra instance.

	./scripts/create_schema.sh

Run this script to ingest all TagPacks

	./bin/ingest_tagspacks.sh

Re-run the transformation job as described in [graphsense-transformation](https://github.com/graphsense/graphsense-transformation)