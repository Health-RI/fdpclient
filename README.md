<!--
SPDX-FileCopyrightText: 2024 Stichting Health-RI

SPDX-License-Identifier: MIT
-->

# FAIR Data Point client

-----

[![PyPI - Version](https://img.shields.io/pypi/v/fairclient.svg)](https://pypi.org/project/fairclient)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fairclient.svg)](https://pypi.org/project/fairclient)
[![Codecov](https://img.shields.io/codecov/c/github/health-ri/fairclient?logo=codecov)](https://app.codecov.io/github/Health-RI/fairclient)

A simple client for the REST API that a FAIR Data Point (FDP) provides. Specifically tuned for the
FDP reference implementation.

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation

Installation can be done using standard pip:

```console
pip install fairclient
```

## Related packages

This package is complementary to [SeMPyRO](https://github.com/health-RI/sempyro), a Python library
to generate RDF and DCAT(-AP) metadata. The RDF output from SeMPyRO can be uploaded to an FDP.

For an example, see [img2catalog](https://github.com/Health-RI/img2catalog).

## License

`fairclient` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
