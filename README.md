![Validate TagPacks](https://github.com/graphsense/graphsense-tagpacks/workflows/Validate%20TagPacks/badge.svg)

# GraphSense TagPacks

A TagPack is a collection of attribution tags, which associate cryptoasset
addresses or GraphSense entities with real-world actors such as exchanges. 

This repository provides a curated collection of TagPacks, which have been
collected from **public sources** either by the GraphSense core team or by other
contributors.

TagPacks make use of the [INTERPOL Dark Web and Virtual Assets Taxonomy][dw-va]
and can be validated and ingested into GraphSense using the 
[GraphSense TagPack Management Tool][tagpack-tool].

## Collection and Sharing Guidelines

### Public TagPack Criteria

All TagPacks in this repository must fulfill the following criteria:

1.) None of the tags contains personally identifiable information (PII)

2.) All tags originate from public sources

3.) All tags provide a dereferenceable pointer (link) to their origin

TagPacks that do not meet these criteria should be hosted in a private
environment, e.g., on the local filesystem or a local Git instance.

### How can I contribute TagPacks to this repository?

**Step 1**: [Fork](https://help.github.com/en/articles/fork-a-repo) this repository

**Step 2**: Add your TagPacks to the folder `packs`

**Step 3**: Validate your TagPack using the [GraphSense TagPack Management Tool][tagpack-tool]

**Step 4**: Contribute them by submitting a [pull request](https://help.github.com/en/articles/about-pull-requests)

## More About TagPacks

### What is an attribution tag?

An attribution tag is any form of context information that can be attributed to
a cryptoasset address or to a GraphSense entity, which represents a set of addresses.

The following example attributes a Bitcoin address to the
Internet Archive, which is, according to [this source](https://archive.org/donate/cryptocurrency/),
the holder of that address:

    label: Internet Archive
    address: 1Archive1n2C579dMsAu3iC6tWzuQJz8dN
    source: https://archive.org/donate/cryptocurrency/

It is also possible to attribute entire GraphSense clusters, which is shown in this example:

    label: Huobi.com
    entity: 19180422
    source: https://www.walletexplorer.com/wallet/Huobi.com

### What is a TagPack?

A TagPack defines a structure for collecting and packaging attribution tags with
additional provenance metadata (e.g., title, creator, etc.).

TagPacks are represented as [YAML][yaml] files, which can easily be created by
hand or exported automatically from other systems.

Here is a minimal TagPack example containing address tags with mandatory properties:

    ---
    title: First Address Tag Example
    creator: John Doe
    tags:
        - address: 1Archive1n2C579dMsAu3iC6tWzuQJz8dN
          label: Internet Archive
          source: https://archive.org/donate/cryptocurrency/
          lastmod: 2019-03-15
          currency: BTC
        - address: 1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2
          label: Example
          source: https://example.com
          lastmod: 2019-03-15
          currency: BTC

The following example associates tags directly with GraphSense entities and therefore with all addresses controlled by that entity:

    ---
    title: First Entity Tag Example
    creator: John Doe
    tags:
        - entity: 17642138
          label: Internet Archive
          source: https://archive.org/donate/cryptocurrency/
          lastmod: 2019-03-15
          currency: BTC

TagPacks can be shared among users using any communication channel (e.g., email).

They can also be managed using some Git-Service (Github in this case), which enables
version control and fine-grained recording of modifications, thus full provenance.

### Why are attribution tags important?

Cryptoasset analytics relies on two complementary techniques: **address
clustering**, which relies on heuristics to group multiple addresses into
maximal subsets that can likely be assigned to the same real-world actor,
and **attribution tags** as shown above. The strength lies in the combination
of these techniques: a tag attributed to a single address belonging to a larger
cluster can easily add contextual information to hundreds of thousands
cryptocurrency addresses.

**Note**: certain types of transactions (e.g., CoinJoins, Mixing Services) can
distort clustering results and lead to false, unreliable, or intentionally
misplaced attribution tags that could associate unrelated actors with a given
cluster.

For further details and an explanation of why we are hosting TagPacks on Github,
we refer to our paper [Safeguarding the evidential value of forensic
cryptocurrency investigations](https://www.sciencedirect.com/science/article/pii/S1742287619302567).

### TagPack properties

A TagPack defines a **header** with several mandatory and optional fields
and a **body** containing a list of tags. In the above example, `title` and
`creator` are part of the TagPack header; the list of `tags` represents the body.

Please note that allowed properties are defined in the TagPack schema, which
defines **mandatory** and **optional** fields for the TagPack header and body.
In the above example, `label`, `address`, and `source` are mandatory properties
as they describe where a certain piece of information is coming from (either
in the form of a URI or a textual description).

The range of defined properties is defined [here](https://github.com/graphsense/graphsense-tagpack-tool/blob/develop/tagpack/conf/tagpack_schema.yaml) and looks as follows:

    header:
      title:
        type: text
        mandatory: true
      creator:
        type: text
        mandatory: true
      owner:
        type: text
        mandatory: false
      description:
        type: text
        mandatory: false
      is_public:
        type: boolean
        mandatory: false
      tags:
        type: list
        mandatory: true
    generic_tag:
      label:
        type: text
        mandatory: true
      source:
        type: text
        mandatory: true
      currency:
        type: text
        mandatory: true
      context:
        type: text
        mandatory: false
      confidence:
        type: int
        mandatory: false
      is_cluster_definer:
        type: boolean
        mandatory: false
      created:
        type: datetime
        mandatory: false
      lastmod:
        type: datetime
        mandatory: false
      category:
        type: text
        mandatory: false
        taxonomy: entity
      abuse:
        type: text
        mandatory: false
        taxonomy: abuse
    address_tag:
      address:
        type: text
        mandatory: true
    entity_tag:
      entity:
        type: int
        mandatory: true


### Property inheritance

In the above example, the same `lastmod` and `currency` property values are
repeated for both tags, which represents an unnecessary repetition of the same
information.

To avoid repeating fields for all tags, one can add body fields to the header and thereby apply them to all tags in the body. Thus, they are *abstracted* into the header and then inherited by all body elements, as shown in the following example.

    ---
    title: Second TagPack Example
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

### Property override

It is also possible to override abstracted fields in the body. This could be
relevant if someone creates a TagPacks comprising several tags and then adds
additional tags later on, which then, of course, have different `lastmod`
property values.

The following example shows several tags associating addresses from various
cryptocurrencies with the label `Internet Archive`. Most of them were collected
at the same time (2019-03-15), except the Zcash tag that was collected and
added later (2019-03-20).

    ---
    title: Third TagPack Example
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

### Identification and Uniqueness of TagPacks and Tags

TagPacks are uniquely identified by a URI.

Since TagPacks are files pushed to some Git repository, they can be
uniquely identified by their Git URI
(e.g., `https://github.com/graphsense/graphsense-tagpacks/blob/master/packs/demo.yaml`).

Within a TagPack, tags are treated as **first-class objects** that are
identified by the combination of the mandatory body fields `address`, `label`,
`source`.

That implies that the same label (e.g., `Internet Archive`) can be assigned
several times to the same address (e.g., `1Archive1n2C579dMsAu3iC6tWzuQJz8dN`),
typically by different parties.

### Using Concepts from Public Taxonomies

The use of common terminology is essential for data sharing and establishing
interoperability across tools. Therefore, the TagPack schema defines two
properties that take concepts from agreed-upon taxonomies as values:

* `category`: defines the type of real-world entity that is in control of a
given address. Possible concepts (e.g., Exchange, Marketplace) are defined in
the [INTERPOL Darkweb and Cryptoassets Entity Taxonomy][dw-va].

* `abuse`: if an address was involved in some abusive behavior, this property's
value defines the type of abuse and can take values from the
[INTERPOL Darkweb and Cryptoassets Abuse Taxonomy][dw-va].

### Attribution Tag confidence score

Attribution tags originate from distinct sources, which have various confidence levels. E.g., Bitcoin addresses retrieved via a Web crawl are less trustworthy than a Bitcoin address with proven private key ownership. Therefore, the TagPack creator can assign one of the following confidence scores:

| Score | Label | Description |
| ---: | :--- | :--- |
| 100 | Proven address ownership | Creator knows address private keys |
| 90  | Trusted transaction | Creator transferred funds from known service x to known service y | 
| 80  | Service API | Creator retrieves addresses from a trusted service API |
| 60  | Authority data | Creator retrieves attribution tags from public authorities (e.g., OFAC) |
| 50  | Trusted data providers | Creator retrieved attribution tags from trusted third parties |
| 50  | Forensic reports | Creator retrieved data attribution data from somehow trusted reports (e.g., Academic papers) |
| 40  | Untrusted transaction | A third party transferred funds from known service x to known service y |
| 20  | Web crawls | Data retrieved from crawling the Web or other data dumps |

The chosen score range provides some flexibility for additional entries in the future.

### Mapping Address Tags to Clusters

An attribution tag assigned to an address could our could not apply to the entire cluster. This decision depends very much on the context of a TagPack, must be decided on an individual basis, and must be flagged using the specific field ``is_cluster_definer``, which can be ``true`` or ``false``.

As a generic rule-of-them, we consider the following generic aspects when doing the mapping.

  1. If an address maps to a cluster that already carries a tag with higher confidence, then the address tag does not define the cluster, i.e., `is_cluster_definer: false`.

  2. If an address maps to a cluster of size 1, then the address tag also defines the entity, i.e., `is_cluster_definer: true`

  3. If an address is not a service address (e.g., exchange) and maps to a large unknown cluster, then it might be some form of custodial wallet, ie., `is_cluster_definer: true`

One can finally end up with several address tags, which are mapped to a single cluster and carry the flat `is_cluster_definer: true`. In such cases, we select the one with the higher
`confidence` value. In case of conflicts, address tags mappings must be revised as part of an attribution tag curation workflow.


### TagPack Repository Configuration

TagPacks are stored in some Git repository - a so-called **TagPack Repository**.

Each TagPack repository must have a file `config.yaml`, which defines the TagPacks'
`baseURI` as well as pointers to used taxonomies.

    baseURI: https://github.com/graphsense/graphsense-tagpacks
    taxonomies:
      entity: https://graphsense.info/DW-VA-Taxonomy/assets/data/entities.csv
      abuse: https://graphsense.info/DW-VA-Taxonomy/assets/data/abuses.csv

[dw-va]: https://graphsense.info/DW-VA-Taxonomy/
[tagpack-tool]: (https://github.com/graphsense/graphsense-tagpack-tool)