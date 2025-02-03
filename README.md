
# Resources for filtering Colloid data

Jordan Dehmel, 2023-2025, Colorado Mesa University

[GitHub](https://github.com/jorbDehmel/colloid-tracking)

## Overview

**Note:** This repository will be orphaned in Fall '25! If you
know python and use it, please take it over!

This repository contains code for the filtering of data
surrounding the motion of Colloids, given that the data has been
extracted via Speckle TrackerJ. These files aim to provide
accurate filtering, as well as reasonable automation. There are
also resources for the simplification of the workflow.

- To test the `speckle` package (doesn't test scripts):
    `make test`
- To launch a `podman` container: `make podman`
- To launch a `docker` container: `make docker`

## Usage

When in doubt, use the `main.py` script: This has a built-in
guide for using it. It should be run before *and* after speckle
tracking.

More documentation can be found in `docs/`.

## Disclaimer

FOSS under the MIT license. Supported by NSF grant 2126451.
Based upon work partially funded by Colorado Mesa University.
