# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
"""
Copyright (c) 2014  Dave Hein <dhein@acm.org>

This module is a command line utility for mergeing Markdown files
into a single file. It examines each file for include statements of the 
form:

    <<[file-name-or-path]
    <<[][code file-name-or-path]def 

"""

__author__ = "Dave Hein <dhein@acm.org>"
__license__ = "MPL"
__version__ = "1.0a1.dev1"
