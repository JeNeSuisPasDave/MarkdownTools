# Copyright 2015 Dave Hein
#
# This file is part of MarkdownTools
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

"""Module of classes to merge input files into a single output file."""

import os
import os.path
import sys
import re
import io
from collections import deque


class MarkdownMerge:

    """Merge the files."""

    def __init__(
            self,
            wildcard_extension_is=".html",
            book_txt_is_special=False,
            stdin_is_book=False,
            ignore_transclusions=False,
            just_raw=False):
        """Constructor."""
        self.__wildcard_extension_is = wildcard_extension_is
        self.__book_txt_is_special = book_txt_is_special
        self.__stdin_is_book = stdin_is_book
        self.__ignore_transclusions = ignore_transclusions
        self.__just_raw = just_raw

        self.__reo_code_fence = re.compile("^([~]{3,}|[`]{3,})[a-zA-Z0-9]+$")
        self.__reo_fence = re.compile("^([~]{3,}|[`]{3,})$")
        self.__reo_index_comment = re.compile("^#")
        self.__reo_leanpub_code_include = re.compile("^<<\[.*\]\((.+)\)$")
        self.__reo_leanpub_include = re.compile("^<<\((.+)\)$")
        self.__reo_leanpub_index_marker = re.compile("^frontmatter\:$")
        self.__reo_leanpub_index_meta = re.compile(
            "^(frontmatter\:|mainmatter:|backmatter:)$")
        self.__reo_markdown_heading = re.compile("^(#+)\s")
        self.__reo_marked_include = re.compile("^<<\[(.+)\]$")
        self.__reo_marked_raw_include = re.compile("^<<\{(.+)\}$")
        self.__reo_marked_raw_include_in_comment = re.compile(
            "^<!-- <<\{(.+)\} -->$")
        self.__reo_mmd_transclusion = re.compile("^\{\{(.+)\}\}$")
        self.__reo_multi_markdown_index_marker = re.compile("^#\s*merge$")
        self.__reo_path_and_wildcard_extension = re.compile("^(.+)\.\*$")
        self.__reo_wildcard_extension = re.compile("^(.+)\.\*$")
        self.__reo_yaml_start = re.compile("^---\s*$")
        self.__reo_yaml_end = re.compile("^...\s*$")
        self.__reo_multi_markdown_meta_data = re.compile(
            "^[a-zA-Z0-9][a-zA-Z0-9 \t_-]*\:\s+\S+")

        self.buf = deque()

    def _bump_level(self, level, line):
        """Increase the heading level of the line.

        Increase the heading level of the line by the integer level value.
        Lines that are not headings are unaffected. If level is zero, no
        change will be made.

        A warning will be issued if the total header level will exceed 6
        (because html only specifies h1-h6).

        Args:
            level: the number of heading levels to add to a heading line.
            line: the line to be processed.

        Returns:
            The adjusted line.

        """
        if 0 >= level:
            return line
        if not self._is_heading(line):
            return line

        # produce warning if the heading level is too deep
        #
        current_level = self._get_heading_level(line)
        if 6 < (current_level + level):
            sys.stderr.write(
                "Warning: Heading level is increased beyond 6 for line:\n")
            sys.stderr.write(self._shorten_line(line) + "\n")

        # adjust the heading level
        #
        prefix = '#' * level
        result = prefix + line
        return result

    def _count_indentation(self, line):
        """Count the indentations of the merge index line.

        Counts the number of positions that a merge index line is
        indented. A 'position' is one tab or 4 space characters. If
        spaces are used, extra spaces are ignore (i.e. a leading 4 spaces
        is equivalent to a leading 5, 6, or 7 spaces).

        Args:
            line: the merge index line to examine.

        Returns:
            The indentation level as an integer number of indent positions.

        """
        level = 0
        space_count = 0
        for i in range(len(line)):
            if '\t' == line[i]:
                level += 1
                space_count = 0
                continue
            if ' ' == line[i]:
                space_count += 1
                if 4 == space_count:
                    level += 1
                    space_count = 0
                    continue
                continue
            # stop at first character that is not a space or tab
            break
        return level

    def _find_include_path(self, lines):
        """Detect wheter line is an include specification.

        Args:
            lines: up to 5 lines of input to be examined for file
                include specifications
        Returns:
            A tuple containing, in order:
                includePath: None if the line is not an include
                    specification. Otherwise, returns the file
                    specification as a string value.
                is_code: True if the include specification is for code;
                    otherwise, False.
                needsFencing: True if the code include needs to be wrapped
                    in a fence; False if not a code include or if fence already
                    exists.

        """
        if None == lines:
            return None, False, False

        # look for code file transclusion specification, which is:
        #
        #   1. A blank line, followed by
        #   2. A code fence start (e.g. `~~~` or `~~~python` or similar,
        #      followed by
        #   3. A line containing only `{{file_path}}`, followed by
        #   4. A code fence termination (e.g. `~~~`), followed by
        #   5. Another blank line.
        #
        # Of course, the first line could be None, indicating top of file.
        # And the last line could be None, indicating end of file
        #
        if (5 == len(lines)):
            if (not self.__just_raw
                    and not self.__ignore_transclusions
                    and self._string_is_null_or_whitespace(lines[0])
                    and self._string_is_null_or_whitespace(lines[4])
                    and not self._string_is_null_or_whitespace(lines[1])
                    and not self._string_is_null_or_whitespace(lines[2])
                    and not self._string_is_null_or_whitespace(lines[3])
                    and self._line_is_code_fence(lines[1])
                    and self._line_is_ending_fence(lines[3])):
                spec = self._find_transclusion(lines[2])
                if (None != spec):
                    return spec, True, False

        # look for normal file transclusion specification, which is:
        #
        #   1. A blank line, followed by
        #   2. A line containing only `{{file_path}}`, followed by
        #   3. Another blank line.
        #
        if (3 == len(lines)):
            if (not self.__just_raw
                    and not self.__ignore_transclusions
                    and self._string_is_null_or_whitespace(lines[0])
                    and self._string_is_null_or_whitespace(lines[2])):
                spec = self._find_transclusion(lines[1])
                if (None != spec):
                    return spec, False, False

        # look for Marked file include specification, which is:
        #
        #   1. A blank line, followed by
        #   2. A line containing only `<<[file_path]`, followed by
        #   3. Another blank line.
        #
        if (3 == len(lines)):
            if (not self.__just_raw
                    and self._string_is_null_or_whitespace(lines[0])
                    and self._string_is_null_or_whitespace(lines[2])):
                spec = self._find_marked_include(lines[1])
                if (None != spec):
                    return spec, False, False

        # look for Marked raw file include specification, which is:
        #
        #   1. A blank line, followed by
        #   2. A line containing only `<<[file_path]`, followed by
        #   3. Another blank line.
        #
        if (3 == len(lines)):
            if (self.__just_raw
                    and self._string_is_null_or_whitespace(lines[0])
                    and self._string_is_null_or_whitespace(lines[2])):
                spec = self._find_marked_raw_include_post_processing(lines[1])
                if (None != spec):
                    return spec, False, False

        # look for Leanpub file include specification, which is:
        #
        #   1. A blank line, followed by
        #   2. A line containing only `<<(file_path)`, or
        #      `<<[code caption](file_path) followed by
        #   3. Another blank line.
        #
        if (3 == len(lines)):
            if (not self.__just_raw
                    and self._string_is_null_or_whitespace(lines[0])
                    and self._string_is_null_or_whitespace(lines[2])):
                spec = self._find_leanpub_include(lines[1])
                if (None != spec):
                    return spec, True, True

        # Get out
        #
        return None, False, False

    def _find_leanpub_include(self, line):
        """Look for Leanpub file include specification.

        Parse the line looking for a Leanpub file include
        specification.

        Args:
            line: The line of the input file to examine.

        Returns:
            `None` if no file include specification is found in the line.
            If a file include specification is found in the line, then
            the specified file path is returned.

        """
        m = self.__reo_leanpub_include.match(line)
        if not m:
            m = self.__reo_leanpub_code_include.match(line)
            if not m:
                return None
        file_path = m.group(1)
        return file_path

    def _find_marked_include(self, line):
        """Look for a Marked file include specification.

        Parse the line looking for a Marked file include
        specification.

        Args:
            line: The line of the input file to examine.

        Returns:
            `None` if no file include specification is found in the line.
            If a file include specification is found in the line, then
            the specified file path is returned.

        """
        m = self.__reo_marked_include.match(line)
        if not m:
            return None
        file_path = m.group(1)
        return file_path

    def _find_marked_raw_include_pre_processing(self, line):
        """Look for a starting Marked raw file include specification.

        Parse the line looking for a Marked raw file include
        specification.

        Args:
            line: The line of the input file to examine.

        Returns:
            `None` if no file include specification is found in the line.
            If a file include specification is found in the line, then
            the specified file path is returned.

        """
        m = self.__reo_marked_raw_include.match(line)
        if not m:
            return None
        file_path = m.group(1)
        return file_path

    def _find_marked_raw_include_post_processing(self, line):
        """Look for an ending Marked raw file include specification.

        Parse the line looking for a Marked raw file include
        specification.

        Args:
            line: The line of the input file to examine.

        Returns:
            `None` if no file include specification is found in the line.
            If a file include specification is found in the line, then
            the specified file path is returned.

        """
        m = self.__reo_marked_raw_include_in_comment.match(line)
        if not m:
            m = self.__reo_marked_raw_include.match(line)
            if not m:
                return None
        file_path = m.group(1)
        return file_path

    def _find_transclusion(self, line):
        """Look for a Multimarkdown file transclusion specification.

        Parse the line looking for a Multimarkdown file transclusion
        specification.

        Args:
            line: The line of the input file to examine.

        Returns:
            `None` if no file transclusion specification is found in the line.
            If a file transclusion specification is found in the line, then
            the specified file path is returned. If the specified path used
            a wildcard extension, the the wildcard is replaced with the
            export extension.

        """
        m = self.__reo_mmd_transclusion.match(line)
        if not m:
            return None
        file_path = m.group(1)
        if "TOC" == file_path:
            return None
        if file_path.endswith(".*"):
            m = self.__reo_path_and_wildcard_extension.match(file_path)
            if m:
                file_path = "{0}{1}".format(
                    m.group(1), self.__wildcard_extension_is)
        return file_path

    def _get_absolute_path(self, main_document_path, file_path):
        """Determine the absolution path of a file.

        A method to determine the absolute path of a file path
        that might be relative or in the users home directory.

        """
        abs_path = os.path.expandvars(file_path)
        abs_path = os.path.expanduser(abs_path)
        if os.path.isabs(abs_path):
            return abs_path
        abs_path = os.path.join(os.path.dirname(main_document_path), abs_path)
        return abs_path

    def _get_heading_level(self, line):
        """Get the heading level of a heading line.

        Determines the heading level of a markdown heading line. Counts
        the number of consecutive '#' at the start of the line.

        Args:
            line: the text line to be processed.

        Returns:
            The heading level of the line. 0 if no leading '#' chars.

        """
        m = self.__reo_markdown_heading.match(line)
        if not m:
            return 0
        h = m.group(1)
        return len(h)

    def _is_file_an_index(self, absfile_path):
        """Determine whether the file is an index file.

        Examines the initial lines of a file to determine whether it
        is an index file.

        Args:
            absfile_path: the full file path of the file to be examined.

        Returns:
            True if the file is a mmd_merge or a LeanPub index file.

        """
        if (None == absfile_path
                or not os.path.exists(absfile_path)):
            return False
        with io.open(absfile_path, 'r', encoding='utf-8') as idxfile:
            for line in idxfile:
                line = line.strip()
                if 0 == len(line):
                    continue
                if (self._is_leanpub_index_marker(line)
                        or self._is_multi_markdown_index_marker(line)):
                    return True
                if self._is_index_comment(line):
                    # skip blanks and comments
                    continue
                break
        return False

    def _is_heading(self, line):
        """Detect heading lines.

        Detect whether line begins with '# ', '## ', etc. Such lines
        are headings when in a markdown file.

        Args:
            line: the text line to be processed.

        Returns:
            True if the line begins with '# ', '## ', et cetera;
            otherwise, False.

        """
        m = self.__reo_markdown_heading.match(line)
        if not m:
            return False
        return True

    def _is_index_comment(self, line):
        """Detect index file comments.

        Detect whether line begins with '#'. Such lines are comments
        when in an index file.

        Returns:
            True if the line begins with '#'; otherwise, False.

        """
        m = self.__reo_index_comment.match(line)
        if not m:
            return False
        return True

    def _is_leanpub_index_marker(self, line):
        """Detect Leanpub index files.

        Detect whether line is 'frontmatter:', indicating the line
        is a marker for leanpub index files.

        Returns:
            True if the line is 'frontmatter:'; otherwise, False.

        """
        m = self.__reo_leanpub_index_marker.match(line)
        if not m:
            return False
        return True

    def _is_leanpub_index_meta(self, line):
        """Detect lLanpub meta tags.

        Detect whether line is some LeanPub meta tag. Specifically:
        'frontmatter:', 'mainmatter:', 'backmatter:'.

        Returns:
            True if the line is a LeanPub meta tag; otherwise, False.

        """
        m = self.__reo_leanpub_index_meta.match(line)
        if not m:
            return False
        return True

    def _is_metadata_end(self, line):
        """Detect end of yaml metadata."""
        if None == line:
            return True
        sline = line.strip()
        if 0 == len(sline):
            return True
        m = self.__reo_yaml_end.match(sline)
        if m:
            return True
        return False

    def _is_metadata_start(self, line):
        """Detect start of yaml metadata."""
        if None == line:
            return False
        sline = line.strip()
        m = self.__reo_yaml_start.match(sline)
        if m:
            return True
        m = self.__reo_multi_markdown_meta_data.match(sline)
        if m:
            return True
        return False

    def _is_multi_markdown_index_marker(self, line):
        """Detect mmd_merge index file.

        Detect whether line is '#merge', indicating the line
        is a marker for mmd_merge index files.

        Returns:
            True if the line is '#merge'; otherwise, False.

        """
        m = self.__reo_multi_markdown_index_marker.match(line)
        if not m:
            return False
        return True

    def _line_is_code_fence(self, line):
        """Detect whether the line contains a code fence directive.

        Args:
            line: the text line to examine

        Returns:
            True if the line is a code fence directive.
            Otherwise returns False.

        """
        m = self.__reo_code_fence.match(line)
        if not m:
            m = self.__reo_fence.match(line)
            if not m:
                return False
        return True

    def _line_is_ending_fence(self, line):
        """Detect whether the line contains a terminating fence directive.

        Args:
            line: the text line to examine

        Returns:
            True if the line is a terminating fence directive.
            Otherwise returns False.

        """
        m = self.__reo_fence.match(line)
        if not m:
            return False
        return True

    def _merged_lines(
            self,
            main_document_path, infile_node, infile, is_code, needs_fence,
            discard_metadata=False):
        """Recursively produce merged lines.

        A generator function that examines each line of the
        input file and recursively calls itself for each included
        file. If the file is code, then include specifications are not
        followed but are reproduced as is.

        Args:
            main_document_path: the absolute file path of the main document;
                used to determine the location of relative file paths found
                in include specifications.
            infile_node: the Node object representing the input file
            infile: the file object of the opened input file
            is_code: True if the include specification is for code;
                otherwise, False.
            needs_fence: True if the code include needs to be wrapped
                in a fence; False if not a code include or if fence already
                exists.
            discard_metadata: Whether to preserve or discard the Multimarkdown
                metadata found at the top of the infile.

        Returns:
            The next line to be written to the output file, or None
            if there are no more input lines.

        """
        # note 0: this is a generator function with multiple yield statements.
        # Sadly, it is very tricky.
        #
        # note 1: there are three line buffers in use. self.buf is the main
        # line buffer and it is the source of the content for the final
        # yield. buf5 is a five line buffer used to detect include
        # specifications that are within code fences. Lines popped off buf5
        # are appended to self.buf. And buf3 mirrors the last 3 lines of buf5
        # and is used to detect unfenced include specifications. Lines
        # popped off buf3 are discarded.
        #

        buf5 = deque(maxlen=5)
        buf3 = deque(maxlen=3)
        # indicate top of file
        buf5.append(None)
        # indicate top of file
        buf3.append(None)
        # align with buf3 so that buf3 always
        buf5.append(None)
        #   corresponds to buf5[2:5]
        buf5.append(None)

        start_fence_produced = False
        end_fence_produced = False

        is_eof = False

        should_check_metadata = discard_metadata
        if is_code:
            should_check_metadata = False
        have_checked_for_metadata = False
        in_metadata = False

        while True:
            if (needs_fence
                    and not start_fence_produced):
                self.buf.append("~~~")
                start_fence_produced = True
            # read the next line
            #
            line = infile.readline()
            # force EOF line to be None for cleaner logic below
            #
            if not line:
                line = None
            # if infile encoding is not specified, force UTF-8
            #
            if (None == infile.encoding
                    and None != line):
                line = line.decode('utf-8')
            # discard metadata if required
            #
            if should_check_metadata:
                if not have_checked_for_metadata:
                    have_checked_for_metadata = True
                    if self._is_metadata_start(line):
                        in_metadata = True
                        continue
                if in_metadata:
                    if not self._is_metadata_end(line):
                        continue
                    in_metadata = False
                    # eat the line that terminates the metadata
                    continue

            # Process the buffers
            #
            if is_eof:
                # special processing to empty buf5 when after EOF
                #
                # note: we delay detecting EOF immediately so that one None
                # line gets pushed into the buffers so that we can detect an
                # include specification that is the last line of a file
                #
                # at end of file, so just move buf5 into buf
                #
                if 0 != len(buf5):
                    bline = buf5.popleft()
                    if None != bline:
                        self.buf.append(bline)
                    else:
                        # skip leading None objects
                        continue
                # at end of line buffer, so close the fence if needed;
                # otherwise, just get out of the main loop
                #
                if 0 == len(self.buf):
                    if (needs_fence
                            and not end_fence_produced):
                        self.buf.append("~~~")
                        end_fence_produced = True
                    else:
                        break
            elif is_code:
                # code files are not processed for nested include specs
                #
                # detect end of file
                #
                if (None == line
                        and not is_eof):
                    is_eof = True
                # push content line into the line buffer
                #
                if None != line:
                    self.buf.append(line)
            else:
                # process nested include specs
                #
                # detect end of file
                #
                if (None == line
                        and not is_eof):
                    is_eof = True
                # pull line of the 5-line buffer and push onto the main
                # line buffer
                #
                if 5 == len(buf5):
                    # roll line out of buf5 into buf, so we don't lose it
                    bline = buf5.popleft()
                    if None != bline:
                        self.buf.append(bline)
                # add the new line to the deques
                buf5.append(line)
                buf3.append(line)
                # check whether this is a 5-line include pattern, ...
                includePath, lclis_code, lclneeds_fence = (
                    self._find_include_path(buf5))
                if includePath:
                    # consuming blank line, the start of the fence, and the
                    # include.
                    for x in range(2):
                        bline = buf5.popleft()
                        if None != bline:
                            self.buf.append(bline)
                    buf5.popleft()
                    # realign window buffers
                    buf3.clear()
                    for x in range(3):
                        buf5.appendleft(None)
                    for x in range(2, 5):
                        buf3.append(buf5[x])
                else:
                    # ... or a 3-line include pattern.
                    includePath, lclis_code, lclneeds_fence = (
                        self._find_include_path(buf3))
                    if includePath:
                        # consuming the preceding two buffered lines,
                        # then the blank line and the include
                        for x in range(2):
                            bline = buf5.popleft()
                            if None != bline:
                                self.buf.append(bline)
                        bline = buf5.popleft()
                        if None != bline:
                            self.buf.append(bline)
                        buf5.popleft()
                        # realign window buffers
                        buf3.clear()
                        for x in range(4):
                            buf5.appendleft(None)
                        for x in range(2, 5):
                            buf3.append(buf5[x])
                    elif (not self.__just_raw
                            and 3 == len(buf3)
                            and self._find_marked_raw_include_pre_processing(
                                buf3[1])):
                        # consuming the preceding two buffered lines,
                        # then the blank line and wrap the raw include
                        # in an html comment
                        #
                        for x in range(2):
                            bline = buf5.popleft()
                            if None != bline:
                                self.buf.append(bline)
                        bline = buf5.popleft()
                        if None != bline:
                            self.buf.append(bline)
                        self.buf.append("<!-- {0} -->".format(
                            buf5.popleft().rstrip("\r\n")))
                        # realign window buffers
                        buf3.clear()
                        for x in range(4):
                            buf5.appendleft(None)
                        for x in range(2, 5):
                            buf3.append(buf5[x])
                if includePath:
                    # merge in the include file
                    #
                    abs_include_path = self._get_absolute_path(
                        main_document_path, includePath)
                    abs_include_path = self._resolve_wildcard_extension(
                        abs_include_path)
                    included_file_node = infile_node.add_child(
                        abs_include_path)
                    with io.open(
                            abs_include_path, 'r',
                            encoding='utf-8') as includedfile:
                        for deeper_line in self._merged_lines(
                                main_document_path, included_file_node,
                                includedfile, lclis_code, lclneeds_fence,
                                discard_metadata=True):
                            yield deeper_line
            if 0 != len(self.buf):
                next_line = self.buf.popleft()
                yield next_line

    def _merge_file(
            self,
            infile, main_document_path, infile_node, level, outfile,
            discard_metadata=False):
        """Add the merged lines of a single top-level file to the output.

        Args:
            infile: the input file stream
            main_document_path: the absolute file path of the main document;
                used to determine the location of relative file paths found
                in include specifications.
            infile_node: the node representing the input file to process.
            level: the heading level to add to the headings found in the
                input file.
            outfile: the open output file in which to write the merged lines.
            discard_metadata: Whether to preserve or discard the Multimarkdown
                metadata found at the top of the file.

        """
        for line in self._merged_lines(
                main_document_path, infile_node, infile, False, False,
                discard_metadata):
            if None == line:
                continue
            outline = self._bump_level(level, line.rstrip("\r\n"))
            outline = outline + '\n'
            if None == outfile.encoding:
                outline = outline.encode('utf-8')
            outfile.write(outline)

    def _merge_stdin_file(
            self,
            infile_node, level, outfile):
        """Add the merged lines from stdin to the output.

        Args:
            infile_node: the node representing stdin as the input file.
            level: the heading level to add to the headings found in the
                input file.
            outfile: the open output file in which to write the merged lines.

        """
        main_document_path = os.path.join(infile_node.root_path(), "dummy")
        self._merge_file(
            sys.stdin, main_document_path, infile_node, level, outfile)

    def _merge_single_file(
            self,
            main_document_path, abs_infile_path, infile_node, level, outfile,
            discard_metadata=False):
        """Add the merged lines of a single top-level file to the output.

        Args:
            main_document_path: the absolute file path of the main document;
                used to determine the location of relative file paths found
                in include specifications.
            abs_infile_path: the full filename of the input file to process.
            infile_node: the node representing the input file to process.
            level: the heading level to add to the headings found in the
                input file.
            outfile: the open output file in which to write the merged lines.
            discard_metadata: Whether to preserve or discard the Multimarkdown
                metadata found at the top of the file.

        """
        abs_infile_path = self._resolve_wildcard_extension(abs_infile_path)
        with io.open(abs_infile_path, 'r', encoding='utf-8') as infile:
            self._merge_file(
                infile, main_document_path, infile_node, level, outfile,
                discard_metadata)

    def _merge_index(
            self,
            idxfile, main_document_path, idxfile_node, outfile):
        """Process index file lines, merging listed files.

        Treat each line of the index file as an input file. Process
        each input file to add the merged result to the output file.

        Args:
            idxfile: the index file stream to process.
            main_document_path: the absolute file path of the main document;
                used to determine the location of relative file paths found
                in include specifications.
            idxfile_node: the node representing the index file to process.
            outfile: the open output file in which to write the merged lines.

        """
        first_time = True
        discard_metadata = False
        for line in idxfile:
            infile_path = line.strip()
            if (0 == len(infile_path)
                    or self._is_index_comment(line)
                    or self._is_leanpub_index_meta(line)):
                continue
            abs_infile_path = self._get_absolute_path(
                main_document_path, infile_path)
            if not os.path.exists(abs_infile_path):
                # ignore non-extant files
                sys.stderr.write(
                    "Warning: file does not exist -- {0}\n".format(
                        abs_infile_path))
                continue
            infile_node = idxfile_node.add_child(abs_infile_path)
            if not first_time:
                # insert blank line between files
                outfile.write("\n")
                # keep only the 1st file's metadata
                discard_metadata = True
            first_time = False
            level = self._count_indentation(line)
            self._merge_single_file(
                main_document_path, abs_infile_path, infile_node, level,
                outfile, discard_metadata)

    def _merge_index_file(self, abs_idxfile_path, idxfile_node, outfile):
        """Merge index file.

        Treat each line of the index file as an input file. Process
        each input file to add the merged result to the output file.

        Args:
            abs_idxfile_path: the full filename of the index file to process.
            idxfile_node: the node representing the index file to process.
            outfile: the open output file in which to write the merged lines.

        """
        with io.open(abs_idxfile_path, 'r', encoding='utf-8') as idxfile:
            self._merge_index(idxfile, abs_idxfile_path, idxfile_node, outfile)

    def _merge_index_stdin(self, idxfile_node, outfile):
        """Merge index file from stdin.

        Treat each line of the index file as an input file. Process
        each input file to add the merged result to the output file.

        Args:
            abs_idxfile_path: the full filename of the index file to process.
            idxfile_node: the node representing the index file to process.
            outfile: the open output file in which to write the merged lines.

        """
        main_document_path = os.path.join(idxfile_node.root_path(), "dummy")
        self._merge_index(sys.stdin, main_document_path, idxfile_node, outfile)

    def _resolve_wildcard_extension(self, file_path):
        """Apply wildcard extension.

        Return the path with the wildcard extension resolve to match
        the export target. If no wildcard extension used, then the file path
        will be unchanged.

        Args:
            file_path: the relative or absolute file path to check for a
                wildcard extension.

        Returns:
            The file path with the wildcard extension replaced with a
            specific extension matching the export target. If no wilcard
            extension was used, then the return value is the file_path argument
            value.

        """
        m = self.__reo_wildcard_extension.match(file_path)
        if not m:
            return file_path
        resolved_path = m.group(1) + self.__wildcard_extension_is
        return resolved_path

    def _shorten_line(self, line):
        """Shorten long lines using ellipses.

        Shorten a long line to something less than 60 characters; append
        ellipses if the line was shortened. This is intended to be used
        for lines displayed in error and warning messages.

        Args:
            line: the text line to be shortened

        Returns:
            The shortened line, suitable for display.

        """
        if 60 >= len(line):
            return line
        return line[:55] + " ..."

    def _string_is_null_or_whitespace(self, s):
        """Determine if string is null or empty.

        Detect whether the string is null, empty, or contains only
        whitespace.

        Args:
            s: the string object to test

        Returns:
            True if the string is None, zero-length, or contains only
            whitespace characters. Otherwise returns False.

        """
        if None == s:
            return True
        if 0 == len(s):
            return True
        if s.isspace():
            return True
        return False

    def merge(self, infile_node, outfile, discard_metadata=False):
        """Perform the merge.

        Give the input file (via a Node object) and the output file
        stream object, process the input file, including other files as
        specified by the include specification encountered, writing the
        resulting output lines to the output file stream.

        Args:
            infile_node: a Node object that represents the input
                file to be processed.
            outfile: the output file stream to which the resulting
                lines will be written.
            discard_metadata: Whether to preserve or discard the Multimarkdown
                metadata found at the top of the file. Ignored for index files.

        """
        infile_path = infile_node.file_path()
        if None == infile_path:
            if self.__stdin_is_book:
                self._merge_index_stdin(infile_node, outfile)
            else:
                self._merge_stdin_file(infile_node, 0, outfile)
        else:
            abs_infile_path = os.path.abspath(infile_path)
            infile_name = os.path.basename(abs_infile_path)
            if (self.__book_txt_is_special
                    and "book.txt".casefold() == infile_name.casefold()):
                self._merge_index_file(abs_infile_path, infile_node, outfile)
            elif self._is_file_an_index(abs_infile_path):
                self._merge_index_file(abs_infile_path, infile_node, outfile)
            else:
                self._merge_single_file(
                    abs_infile_path, abs_infile_path, infile_node, 0, outfile,
                    discard_metadata)

# eof
