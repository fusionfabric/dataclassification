# Versioning

This section describes Finastra Version Numbering conventions for this project.

1. [Intro](#intro)
1. [Versioning During Ongoing Development](#versioning-during-ongoing-development)
1. [References](#references)


## Intro

Version number should consist of 3 non-negative integer numbers separated by dots:

```
x.y.z
```

where
* ```x``` - major version number, represents "big" product releases to market
* ```y``` - minor version number, represents new features or critical bug fixes
* ```z``` - micro version number, represents minor updates and bug fixes

Versions should start from ```0.0.0``` at initial project commit to source code repository.

## Versioning During Ongoing Development

micro version number (z) should be updated when:
* new feature added during Sprint
* non-critical bug fixed during Sprint
* few minor issues fixed (typo, markup, layout etc)

_micro version updates may not be released to production as standalone updates._

Minor version number (y) should be updated:
* when Sprint finished successfully _(Note: minor version number may not equal to Sprint number)_
* when critical bug fixed (server fault, app crash)
* after security vulnerability fix

_Minor version updates may not be released to market/production unless they provide critical updates or bug fixes._

Major version number (x) should be updated when:
* product increment has significant number of completely new features added
* product made a pivot

_Major version updates must be released to market/production._

Examples:

* 1.0.1 - minor update or bug fix to first product release
* 1.1.0 - major update, security update or critical bug fix to first product release
* 1.2.0 - tool now supports python 3.2.6
* 1.3.0 - Sprint 46 product increment
* 1.3.1 - Issue with Rules fixed 
* 2.0.0 - App now supports YAML

## References

* [Semantic Versioning 2.0.0](http://semver.org/)
