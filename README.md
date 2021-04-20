# pdsw-muse-api-python-client
Python Muse Automation Client

---

[![GitHub license](https://img.shields.io/badge/license-UNLICENSED-blue.svg?style=for-the-badge)](.//LICENSE)
[![Maintained](https://img.shields.io/badge/Maintained%3F-yes-green.svg?style=for-the-badge)](https://github.com/Sonos-Inc/pdsw-muse-api-python-client/graphs/commit-activity)
<!-- More badges can be found at [shields.io](https://shields.io/). -->

---

This repository tracks the Muse Control API and related tools. If you are
looking to add to or change the Control API, you're at the right place.

## Quick Navigation

| [What is Muse?](https://github.com/Sonos-Inc/pdsw-muse-api-python-client/wiki) | [The Big Picture](https://github.com/Sonos-Inc/pdsw-muse-api/wiki/Muse-Overview) |  [Pull Request Guidelines](https://github.com/Sonos-Inc/pdsw-muse-api/wiki/Pull-Request-Guidelines) | [Making Muse Releases](https://github.com/Sonos-Inc/pdsw-muse-api/wiki/Making-Muse-Releases) |
|----------------------------|---------------------------------|-------------------------------|-------------------------------|
| Understanding the IDL and how it's used | Looking at the future of Muse and its current roadmap | Understanding the expectations for pull-requests | An overview of how releases work and how they relate to Perforce branches |

| [Light Weight Developer Portal](https://furry-lamp-d03d2b97.pages.github.io/) | [API Reference](https://furry-lamp-d03d2b97.pages.github.io/reference/redoc-static.html) | [IDL Schema](https://furry-lamp-d03d2b97.pages.github.io/reference/muse-namespace.xsd) |
|----|----|----|
| Landing page for developer documentation | OpenAPI reference documentation | Documentation describing the xml structure used to describe our API |

Or, just go straight to the wiki here: https://github.com/Sonos-Inc/pdsw-muse-api-python-client/wiki

---

## Quick Setup

> NOTE: This is just a quick setup guide and is missing a lot of important details. 
> Please see the [Making Changes to Muse](https://github.com/Sonos-Inc/pdsw-muse-api/wiki/Changing-the-Muse-API) and [Muse Releases Guide](https://github.com/Sonos-Inc/pdsw-muse-api/wiki/Muse-Releases-Guide) wiki pages for more details.

1. [Clone this repository and make your branch off of **mainline**](#1-Clone-this-repository-and-make-your-branch-off-of-mainline)
2. [Make your changes and run the validation script](#2-Make-your-changes-and-run-the-validation-script)
3. [Point your player at your branch and test](#3-Point-your-player-at-your-branch-and-test)
4. [Make a pull request to **mainline**](#4-Make-a-pull-request-to-mainline)
5. [Merge to **mainline** and make a release](#5-Merge-to-mainline-and-make-a-release)
6. [Update your player branch to point at the release](#6-Update-your-player-branch-to-point-at-the-release)

### 1. Clone this repository and make your branch off of **mainline**

You have to clone using SSH, so make sure that you've added your public SSH key to GitHub and that SSO is enabled. More information here:
- https://confluence.sonos.com/display/PDSW/1.+GIT+On-Boarding
- https://github.com/settings/keys

```
$ git clone git@github.com:Sonos-Inc/pdsw-muse-api.git
$ cd pdsw-muse-api
$ git checkout -b SWPBL-00000-my-super-cool-feature
```

### 2. Make your changes and run the validation script

```
$ ./tools/validate.sh
```

Visit the validation script's [README](tools/README.md) for more information or if you run into any issues.

### 3. Point your player at your branch and test

Update your player development branch to either point at your branch name or a specific commit.

```sh
$ vim mtools/api_version

# The Muse API version string
version: 1.22.0-alpha.1

# release_ref is a reference to the Muse API specification files.
# release_ref is optional and need not be provided for official
# releases. For pre-releases, release_ref can reference a Sonos
# artifact cache object or a Github ref, e.g:
#   Artifact cache: 1.19.0-alpha.3
#   Github (commit ref): c314f1
#   Github (branch name): pint-fusion-integ
#   Github (pre-release tag): v1.19.0-alpha.3
#   Github (release tag): v1.18.4
release_ref: SWPBL-00000-my-super-cool-feature
```

After it's all updated, make a player build and test your impacted namespace(s) and command(s), if applicable. We recommend using [Muse Explorer](https://github.com/Sonos-Inc/pdsw-muse-api/releases/tag/muse-explorer-2.2.0), but you can [read this Wiki page](https://github.com/Sonos-Inc/pdsw-muse-api/wiki/Testing-the-API-with-Postman) if you'd rather utilize Postman.

For more information, go to [Muse Development on the Player](https://github.com/Sonos-Inc/pdsw-muse-api/wiki/Muse-Development-on-the-Player).

### 4. Make a pull request to **mainline**

When you're ready to merge to **mainline_integ**, create a pull request to **mainline**. Be sure to utilize the pull request template and follow our [pull request guidelines](https://github.com/Sonos-Inc/pdsw-muse-api/wiki/Pull-Request-Guidelines).

### 5. Merge to **mainline** and make a release

After your pull request is approved, merge your IDL changes to **mainline**. Before merging your player changes to its final destination, you'll need make a release. Releases are generated manually
and they can be requested in the `#control-api` slack channel or explicitly in your pull-request.

Please review our [releases guide](https://github.com/Sonos-Inc/pdsw-muse-api/wiki/Muse-Releases-Guide) for more information.

### 6. Update your player branch to point at the release

Player builds __do not__ automatically track Github branches or releases, so you'll need to update `all/mtools/api_version` one last time to comment out your `release_ref` and instead update `version` to point at your new release.