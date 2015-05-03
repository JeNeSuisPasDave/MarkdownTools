# Copyright 2015 Dave Hein
#
# This file is part of MarkdownTools
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

"""
Copyright (c) 2015 Dave Hein <dhein@acm.org>.

This module is a command line utility for merging Markdown files
into a single file. It examines each file for include statements of the
form:

    <<[rel-or-abs-path]
    <<()[rel-or-abs-path]
    {{rel-or-abs-path}}

"""

__author__ = "Dave Hein <dhein@acm.org>"
__copyright__ = "Copyright 2015 Dave Hein"
__license__ = "MPL-2.0"
__version__ = "1.0.1"
