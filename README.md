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

**Step 1**: [Fork](https://help.github.com/en/articles/fork-a-repo) this repository.

**Step 2**: Add your TagPack(s) to the folder `packs`. 
* Large datasets should be broken down into [smaller TagPacks][large-packs].
* Put multiple TagPacks that are related in their own subfolder, e.g. `packs/walletexplorer_exchanges`

**Step 3**: Validate your TagPack using the [GraphSense TagPack Management Tool][tagpack-tool].
* This is also a good opportunity to get acquainted with the **Actor** concept. You can enhance your TagPacks by adding actors to your TagPacks: refer to the [add actor feature][actor-feature] of the TagPack Management Tools.

**Step 4**: Contribute them by submitting a [pull request](https://help.github.com/en/articles/about-pull-requests).

[actor-feature]: https://github.com/graphsense/graphsense-tagpack-tool#interactive-tagpack-update
[tagpack-tool]: https://github.com/graphsense/graphsense-tagpack-tool
[large-packs]: https://github.com/graphsense/graphsense-tagpacks/wiki/GraphSense-TagPacks#large-tagpack-files

# GraphSense ActorPacks

A [GraphSense ActorPack](https://github.com/graphsense/graphsense-tagpacks/wiki/GraphSense-Actors) is a data structure for packaging and sharing information about real-world actors, such as an exchange. 

### Aliases and relations between actors

Besides its own fields, an actor can point to other actors:

- `aliases` (actor level): other ids or spellings of **this** actor; tags
  using an alias are stored under the actor's id.
- In `context`, for **separate** actor entries that may tag the same
  addresses without a conflict:
  - `same_as`: the same organisation (rebrand, duplicate entry)
  - `sub_service_of`: a product or division of the same organisation (one id)
  - `nested_in`: a separate organisation running on the listed actors'
    addresses or accounts (e.g. an exchange at a custodian)
  - `related_actors`: separate organisations on the same addresses for
    another reason (e.g. a token and its custodian)

Relations must name actor ids, not aliases. Record the evidence in
`context.notes` / `context.refs`. Details, validation rules and a guide on
which field to use: [graphsense-lib tagpack docs](https://github.com/graphsense/graphsense-lib/blob/develop/tagpack/docs/README.md#aliases).

### Checking actor links

`tools/check_actor_links.py` checks the links of every actor: the logo (first
entry of `context.images`: it must have an image file extension, because the
dashboard draws it with `<object>`, which crops images whose URL has none,
and load as an image), the website (`uri`), the references (`context.refs`)
and, when a website's host has no DNS record, whether its domain is still
registered (RDAP). It never edits the actorpack.

```bash
uv run tools/check_actor_links.py                       # all actors, report to stdout
uv run tools/check_actor_links.py --actors binance okex  # some actors
uv run tools/check_actor_links.py --changed-from origin/master --fail-on-broken
uv run tools/check_actor_links.py --report report.md --csv results.csv
```

Findings are `broken` (404/410, no DNS record, connection refused, domain not
registered or being deleted, logo not an image or without file extension),
`unknown` (403/429/5xx, timeouts, TLS errors: often bot protection, so never
reported as broken) or `moved` (redirects to another domain: rebrand, sale or
a parked domain; worth a look). Social media links (X, LinkedIn, ...), data
APIs (CoinGecko, DefiLlama) and placeholder websites (`*.dummy`) are skipped.
A dead website or domain is a hint that an actor may be defunct
(`active: false`); decide by hand.

The workflow `.github/workflows/actor-links.yml` runs it on every pull request
that changes `actors/` (only new or changed links; it fails if one of them is
broken) and every Monday on all actors, keeping the report in an open issue
labelled `actor-links` (full CSV as a workflow artifact). Run it by hand from
the Actions tab ("Run workflow").
