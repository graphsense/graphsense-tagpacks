![Validate TagPacks](https://github.com/graphsense/graphsense-tagpacks/workflows/Validate%20TagPacks/badge.svg)

# GraphSense Public TagPacks

A [GraphSense TagPack](https://github.com/graphsense/graphsense-tagpacks/wiki/GraphSense-TagPacks) is a data structure for packaging and sharing cryptoasset **attribution tags** in an interoperable, machine-processable format. The following example attributes a Bitcoin address  (`1Archive1n2C579dMsAu3iC6tWzuQJz8dN`) to the [Internet Archive](https://archive.org/), which according to [this source](https://archive.org/donate/cryptocurrency/) controls that address:

    label: Internet Archive
    address: 1Archive1n2C579dMsAu3iC6tWzuQJz8dN
    source: https://archive.org/donate/cryptocurrency/

This repository provides a curated collection of TagPacks, which have been collected from **public sources** either by the GraphSense core team or by other
contributors.

## Collection and Sharing Guidelines

All TagPacks in this repository must fulfill the following criteria:

1.) They must not contain personally identifiable information (PII)

2.) Attribution tags must originate from public sources

3.) Attribution tags must provide a dereferenceable pointer (link) to the source

TagPacks that do not meet these criteria should be hosted in a private environment, e.g., on the local filesystem or a local Git instance.

Finally, all provided TagPacks must pass the validation steps supported by the [GraphSense TagPack Tool][tagpack-tool]

## How can I contribute TagPacks to this repository?

**Step 1**: [Fork](https://help.github.com/en/articles/fork-a-repo) this repository

**Step 2**: Add your TagPacks to the folder `packs`

**Step 3**: Validate your TagPack using the [GraphSense TagPack Management Tool][tagpack-tool]

**Step 4**: Contribute them by submitting a [pull request](https://help.github.com/en/articles/about-pull-requests)

[tagpack-tool]: https://github.com/graphsense/graphsense-tagpack-tool

# GraphSense ActorPacks

A [GraphSense ActorPack](https://github.com/graphsense/graphsense-tagpacks/wiki/GraphSense-Actors) is a data structure for packaging and sharing information about real-world actors, such as an exchange. 
