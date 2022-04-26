![Validate TagPacks](https://github.com/graphsense/graphsense-tagpacks/workflows/Validate%20TagPacks/badge.svg)

# GraphSense Public TagPacks

A TagPack is a collection of attribution tags, which associate cryptoasset
addresses or GraphSense entities with real-world actors such as exchanges. 

This repository provides a curated collection of TagPacks, which have been
collected from **public sources** either by the GraphSense core team or by other
contributors. For further details and an explanation of why we are hosting TagPacks on Github,
we refer to our paper [Safeguarding the evidential value of forensic
cryptocurrency investigations](https://www.sciencedirect.com/science/article/pii/S1742287619302567).

Technical details about TagPacks (purpose, structure etc.), plus how to validate your TagPacks can be found over at the [GraphSense TagPack Management Tool repo](https://github.com/graphsense/graphsense-tagpack-tool/blob/master/README_tagpacks.md).


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


[tagpack-tool]: https://github.com/graphsense/graphsense-tagpack-tool


