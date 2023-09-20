The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [23.09] 2023-09-20
### Added
- new addresses related to the lazerus group
- added actor kurant
### Changed
- added actors to eth wordcloud

## [23.06] 2023-06-12
### Changed
- OFAC data update
- Updated "How to contribute" section in README

## [23.03] 2023-03-30
### Added
  - initial actors file and actors annotation [#39](https://github.com/graphsense/graphsense-tagpacks/issues/39), [#38](https://github.com/graphsense/graphsense-tagpacks/issues/38), [#43](https://github.com/graphsense/graphsense-tagpacks/issues/43)
  - Actors from Walletexplorer [#35](https://github.com/graphsense/graphsense-tagpacks/issues/35)  
  - Mining service actors
  - More proof-of-reserve tagpacks
  - USDT blacklist tagpack

## [23.01] 2023-01-30
### Added
- demo ActorPacks file
- ActorPacks: VASPs having proof-of-reserves, from Walletexplorer
- CTF tagpack

## Fixed
- github action
- CTF tagpack

## [22.11] 2022-11-24
### Added
- Lockbit Tattoo tagpack
- CEX transparency reserves wallets tagpacks (from preliminary sources)

## [22.10] 2022-10-11
### Added
- DeFi tagpack
- mixing_service tagpack
- miner tagpack
- gambling tagpacks
- market tagpack
- exchange tagpack

### Changed
- update miners tagpack with miners from the years 2020-current

## [1.0.0] 2022-07-12
### Added
- CITATION.cff file
- blender_io pack
- hydra pack
- ronin_bridge pack
### Fixed
- wrong currency entries in etherscamdb_tagpack.yaml
- wrong address in Alt-Right.yaml
### Changed
- etherscamdb_tagpack pack
- lazarus pack
- ofac pack
- wasabi_collector pack
- updated LICENSE
- updated README.md
- removed created field

## [0.5.2] 2022-03-15
### Added
- africrypt pack
- suidlanders pack
- alt-right pack
- ransomwhere pack
### Changed
- confidence value type, which is now categorical.
- category settings in several packs, to match updated [taxonomy schema](https://github.com/graphsense/DW-VA-Taxonomy/)
### Fixed
- wrong currency entries in several packs
### Removed
- entity-related components
- duplicate tag entries

## [0.5.1] 2021-11-17
### Added
- Etherscamdb tagpack
- OFAC tagpack
- mapped entity tagpacks
- new schema fields to existing address TagPacks
### Changed
- outdated concepts links
- taxonomy endpoints from Interpol to GraphSense Github repo
- schema documentation

### Removed
- tagpack with fake examples

## [0.5.0] 2021-05-31
### Changed
- add WalletExplorer address and entity tags
- update documentation for Entity Tags
- added EtherScan word cloud TagPack
- moved TagPack documentation from tagpack tool to tagpack collection

## [0.4.5] - 2020-11-16
### Added
- New tagpacks

## [0.4.4] - 2020-05-12

## [0.4.3] - 2020-05-11
### Added
- New tagpacks

### Changed
- Separated TagPack public repository from TagPack Management tool

## [0.4.2] - 2019-12-19
### Added
- New tagpacks
- Abuses field

### Changed
- Splitted config from schema
- Improved argparse
- Renaming categories

### Removed
- Jupyter notebooks

## [0.4.1] - 2019-06-28
### Added
- Tagpacks: walletexplorer, ransomware, sextortion (Talos), miners
- Schema creation, validate and ingest scripts
- Documentation, License, etc.
