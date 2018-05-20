#!/bin/sh

# This script gets called from CI to run doctests in the sagemath build

# Usage: ./test-doctest.sh IMAGE-NAME --new|--short|--long

# ****************************************************************************
#       Copyright (C) 2018 Julian Rüth <julian.rueth@fsfe.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
# ****************************************************************************

set -ex

case "$2" in
    --new)
        # Try to go back to the latest commit by the release manager
        git reset `git log --author release@sagemath.org -1 --format=%H` || true
        export DOCTEST_PARAMETERS="--new"
        ;;
    --short)
        # TODO: Upgrade this with https://trac.sagemath.org/ticket/25270
        export DOCTEST_PARAMETERS="--all"
        ;;
    --long)
        export DOCTEST_PARAMETERS="--long"
        ;;
    *)
        exit 1
        ;;
esac

# Run tests once, and then try the failing files twice to work around flaky doctests.
docker run --entrypoint sh -e DOCTEST_PARAMETERS "$1" -c 'sage -tp $DOCTEST_PARAMETERS ||
                                                               sage -tp --failed $DOCTEST_PARAMETERS ||
                                                               sage -tp --failed $DOCTEST_PARAMETERS'

