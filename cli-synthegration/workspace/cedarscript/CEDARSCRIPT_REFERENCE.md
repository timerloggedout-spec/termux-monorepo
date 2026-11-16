# CEDARscript Complete Reference

## Installation
`pip install cedarscript-editor` (already present)

## Location
`/data/data/com.termux/files/usr/lib/python3.13/site-packages/cedarscript_editor`

## Public API

### Class: `CEDARScriptASTParser`
Constructor: `CEDARScriptASTParser(self)`
  * `find_first_by_field_name(node: <built-in function any>, field_names)`
  * `find_first_by_type(nodes: collections.abc.Sequence[any], child_type)`
  * `find_primitive(self, node)`
  * `parse_case_action(self, node) -> cedarscript_ast_parser.cedarscript_ast_parser.CaseAction`
    Parse a THEN clause in a CASE statement
  * `parse_case_stmt(self, node) -> cedarscript_ast_parser.cedarscript_ast_parser.CaseStatement`
    Parse a CASE statement
  * `parse_case_when(self, node) -> cedarscript_ast_parser.cedarscript_ast_parser.CaseWhen`
    Parse a WHEN clause in a CASE statement
  * `parse_command(self, node)`
  * `parse_content(self, node) -> str | tuple[cedarscript_ast_parser.cedarscript_ast_parser.BodyOrWhole | cedarscript_ast_parser.cedarscript_ast_parser.Marker | cedarscript_ast_parser.cedarscript_ast_parser.Segment, int | None] | None`
  * `parse_content_from_segment_clause(self, node) -> tuple[cedarscript_ast_parser.cedarscript_ast_parser.BodyOrWhole | cedarscript_ast_parser.cedarscript_ast_parser.Marker | cedarscript_ast_parser.cedarscript_ast_parser.Segment, int | None]`
  * `parse_content_literal(self, node) -> str`
  * `parse_create_command(self, node)`
  * `parse_delete_clause(self, node)`
  * `parse_ed_stmt(self, node) -> cedarscript_ast_parser.cedarscript_ast_parser.EdScript`
    Parse an ED script statement
  * `parse_identifier_from_file(self, node)`
  * `parse_insert_clause(self, node) -> cedarscript_ast_parser.cedarscript_ast_parser.InsertClause`
  * `parse_line_filter(self, node) -> cedarscript_ast_parser.cedarscript_ast_parser.LineFilter`
  * `parse_marker(self, node) -> cedarscript_ast_parser.cedarscript_ast_parser.Marker`
  * `parse_move_clause(self, node)`
  * `parse_multiline_string(node)`
  * `parse_mv_file_command(self, node)`
  * `parse_region(self, node) -> cedarscript_ast_parser.cedarscript_ast_parser.BodyOrWhole | cedarscript_ast_parser.cedarscript_ast_parser.Marker | cedarscript_ast_parser.cedarscript_ast_parser.Segment`
  * `parse_relative_indent_block(self, node) -> str`
  * `parse_relative_indentation(self, node) -> int | None`
  * `parse_replace_clause(self, node)`
  * `parse_rm_file_command(self, node)`
  * `parse_script(self, code_text: str) -> tuple[collections.abc.Sequence[cedarscript_ast_parser.cedarscript_ast_parser.Command], collections.abc.Sequence[cedarscript_ast_parser.cedarscript_ast_parser.ParseError]]`
    Parses the CEDARScript code and returns a tuple containing:
- A list of Command objects if parsing is successful.
- A list of ParseError objects if there are parsing errors.
  * `parse_segment(self, node) -> cedarscript_ast_parser.cedarscript_ast_parser.Segment`
  * `parse_singlefile_clause(self, node)`
  * `parse_string(node)`
  * `parse_to_value_clause(self, node)`
  * `parse_update_action(self, node)`
  * `parse_update_command(self, node)`
  * `parse_update_target(self, node)`
  * `parse_where_clause(self, node)`
### Class: `CEDARScriptEditor`
Constructor: `CEDARScriptEditor(self, root_path)`
  * `apply_commands(self, commands: collections.abc.Sequence[cedarscript_ast_parser.cedarscript_ast_parser.Command])`
  * `find_identifier(self, source_info: tuple[str, str | collections.abc.Sequence[str]], marker: cedarscript_ast_parser.cedarscript_ast_parser.Marker) -> text_manipulation.range_spec.IdentifierBoundaries`
  * `find_index_range_for_region(self, region: cedarscript_ast_parser.cedarscript_ast_parser.BodyOrWhole | cedarscript_ast_parser.cedarscript_ast_parser.Marker | cedarscript_ast_parser.cedarscript_ast_parser.Segment | cedarscript_ast_parser.cedarscript_ast_parser.RelativeMarker, lines: collections.abc.Sequence[str], identifier_resolver: Callable[[cedarscript_ast_parser.cedarscript_ast_parser.Marker], text_manipulation.range_spec.IdentifierBoundaries], search_range: text_manipulation.range_spec.RangeSpec | text_manipulation.range_spec.IdentifierBoundaries | None = None) -> text_manipulation.range_spec.RangeSpec`
### Module: `cedarscript_editor`
#### Class: `BodyOrWhole`
Constructor: `BodyOrWhole(self, *args, **kwds)`
  * `capitalize(self, /)`
    Return a capitalized version of the string.

More specifically, make the first character have upper case and the rest lower
case.
  * `casefold(self, /)`
    Return a version of the string suitable for caseless comparisons.
  * `center(self, width, fillchar=' ', /)`
    Return a centered string of length width.

Padding is done using the specified fill character (default is a space).
  * `count()`
    Return the number of non-overlapping occurrences of substring sub in string S[start:end].

Optional arguments start and end are interpreted as in slice notation.
  * `encode(self, /, encoding='utf-8', errors='strict')`
    Encode the string using the codec registered for encoding.

  encoding
    The encoding in which to encode the string.
  errors
    The error handling scheme to use for encoding errors.
    The default is 'strict' meaning that encoding errors raise a
    UnicodeEncodeError.  Other possible values are 'ignore', 'replace' and
    'xmlcharrefreplace' as well as any other name registered with
    codecs.register_error that can handle UnicodeEncodeErrors.
  * `endswith()`
    Return True if the string ends with the specified suffix, False otherwise.

  suffix
    A string or a tuple of strings to try.
  start
    Optional start position. Default: start of the string.
  end
    Optional stop position. Default: end of the string.
  * `expandtabs(self, /, tabsize=8)`
    Return a copy where all tab characters are expanded using spaces.

If tabsize is not given, a tab size of 8 characters is assumed.
  * `find()`
    Return the lowest index in S where substring sub is found, such that sub is contained within S[start:end].

Optional arguments start and end are interpreted as in slice notation.
Return -1 on failure.
  * `format(self, /, *args, **kwargs)`
    Return a formatted version of the string, using substitutions from args and kwargs.
The substitutions are identified by braces ('{' and '}').
  * `format_map(self, mapping, /)`
    Return a formatted version of the string, using substitutions from mapping.
The substitutions are identified by braces ('{' and '}').
  * `index()`
    Return the lowest index in S where substring sub is found, such that sub is contained within S[start:end].

Optional arguments start and end are interpreted as in slice notation.
Raises ValueError when the substring is not found.
  * `isalnum(self, /)`
    Return True if the string is an alpha-numeric string, False otherwise.

A string is alpha-numeric if all characters in the string are alpha-numeric and
there is at least one character in the string.
  * `isalpha(self, /)`
    Return True if the string is an alphabetic string, False otherwise.

A string is alphabetic if all characters in the string are alphabetic and there
is at least one character in the string.
  * `isascii(self, /)`
    Return True if all characters in the string are ASCII, False otherwise.

ASCII characters have code points in the range U+0000-U+007F.
Empty string is ASCII too.
  * `isdecimal(self, /)`
    Return True if the string is a decimal string, False otherwise.

A string is a decimal string if all characters in the string are decimal and
there is at least one character in the string.
  * `isdigit(self, /)`
    Return True if the string is a digit string, False otherwise.

A string is a digit string if all characters in the string are digits and there
is at least one character in the string.
  * `isidentifier(self, /)`
    Return True if the string is a valid Python identifier, False otherwise.

Call keyword.iskeyword(s) to test whether string s is a reserved identifier,
such as "def" or "class".
  * `islower(self, /)`
    Return True if the string is a lowercase string, False otherwise.

A string is lowercase if all cased characters in the string are lowercase and
there is at least one cased character in the string.
  * `isnumeric(self, /)`
    Return True if the string is a numeric string, False otherwise.

A string is numeric if all characters in the string are numeric and there is at
least one character in the string.
  * `isprintable(self, /)`
    Return True if all characters in the string are printable, False otherwise.

A character is printable if repr() may use it in its output.
  * `isspace(self, /)`
    Return True if the string is a whitespace string, False otherwise.

A string is whitespace if all characters in the string are whitespace and there
is at least one character in the string.
  * `istitle(self, /)`
    Return True if the string is a title-cased string, False otherwise.

In a title-cased string, upper- and title-case characters may only
follow uncased characters and lowercase characters only cased ones.
  * `isupper(self, /)`
    Return True if the string is an uppercase string, False otherwise.

A string is uppercase if all cased characters in the string are uppercase and
there is at least one cased character in the string.
  * `join(self, iterable, /)`
    Concatenate any number of strings.

The string whose method is called is inserted in between each given string.
The result is returned as a new string.

Example: '.'.join(['ab', 'pq', 'rs']) -> 'ab.pq.rs'
  * `ljust(self, width, fillchar=' ', /)`
    Return a left-justified string of length width.

Padding is done using the specified fill character (default is a space).
  * `lower(self, /)`
    Return a copy of the string converted to lowercase.
  * `lstrip(self, chars=None, /)`
    Return a copy of the string with leading whitespace removed.

If chars is given and not None, remove characters in chars instead.
  * `maketrans()`
    Return a translation table usable for str.translate().

If there is only one argument, it must be a dictionary mapping Unicode
ordinals (integers) or characters to Unicode ordinals, strings or None.
Character keys will be then converted to ordinals.
If there are two arguments, they must be strings of equal length, and
in the resulting dictionary, each character in x will be mapped to the
character at the same position in y. If there is a third argument, it
must be a string, whose characters will be mapped to None in the result.
  * `partition(self, sep, /)`
    Partition the string into three parts using the given separator.

This will search for the separator in the string.  If the separator is found,
returns a 3-tuple containing the part before the separator, the separator
itself, and the part after it.

If the separator is not found, returns a 3-tuple containing the original string
and two empty strings.
  * `removeprefix(self, prefix, /)`
    Return a str with the given prefix string removed if present.

If the string starts with the prefix string, return string[len(prefix):].
Otherwise, return a copy of the original string.
  * `removesuffix(self, suffix, /)`
    Return a str with the given suffix string removed if present.

If the string ends with the suffix string and that suffix is not empty,
return string[:-len(suffix)]. Otherwise, return a copy of the original
string.
  * `replace(self, old, new, /, count=-1)`
    Return a copy with all occurrences of substring old replaced by new.

  count
    Maximum number of occurrences to replace.
    -1 (the default value) means replace all occurrences.

If the optional argument count is given, only the first count occurrences are
replaced.
  * `rfind()`
    Return the highest index in S where substring sub is found, such that sub is contained within S[start:end].

Optional arguments start and end are interpreted as in slice notation.
Return -1 on failure.
  * `rindex()`
    Return the highest index in S where substring sub is found, such that sub is contained within S[start:end].

Optional arguments start and end are interpreted as in slice notation.
Raises ValueError when the substring is not found.
  * `rjust(self, width, fillchar=' ', /)`
    Return a right-justified string of length width.

Padding is done using the specified fill character (default is a space).
  * `rpartition(self, sep, /)`
    Partition the string into three parts using the given separator.

This will search for the separator in the string, starting at the end. If
the separator is found, returns a 3-tuple containing the part before the
separator, the separator itself, and the part after it.

If the separator is not found, returns a 3-tuple containing two empty strings
and the original string.
  * `rsplit(self, /, sep=None, maxsplit=-1)`
    Return a list of the substrings in the string, using sep as the separator string.

  sep
    The separator used to split the string.

    When set to None (the default value), will split on any whitespace
    character (including \n \r \t \f and spaces) and will discard
    empty strings from the result.
  maxsplit
    Maximum number of splits.
    -1 (the default value) means no limit.

Splitting starts at the end of the string and works to the front.
  * `rstrip(self, chars=None, /)`
    Return a copy of the string with trailing whitespace removed.

If chars is given and not None, remove characters in chars instead.
  * `split(self, /, sep=None, maxsplit=-1)`
    Return a list of the substrings in the string, using sep as the separator string.

  sep
    The separator used to split the string.

    When set to None (the default value), will split on any whitespace
    character (including \n \r \t \f and spaces) and will discard
    empty strings from the result.
  maxsplit
    Maximum number of splits.
    -1 (the default value) means no limit.

Splitting starts at the front of the string and works to the end.

Note, str.split() is mainly useful for data that has been intentionally
delimited.  With natural text that includes punctuation, consider using
the regular expression module.
  * `splitlines(self, /, keepends=False)`
    Return a list of the lines in the string, breaking at line boundaries.

Line breaks are not included in the resulting list unless keepends is given and
true.
  * `startswith()`
    Return True if the string starts with the specified prefix, False otherwise.

  prefix
    A string or a tuple of strings to try.
  start
    Optional start position. Default: start of the string.
  end
    Optional stop position. Default: end of the string.
  * `strip(self, chars=None, /)`
    Return a copy of the string with leading and trailing whitespace removed.

If chars is given and not None, remove characters in chars instead.
  * `swapcase(self, /)`
    Convert uppercase characters to lowercase and lowercase characters to uppercase.
  * `title(self, /)`
    Return a version of the string where each word is titlecased.

More specifically, words start with uppercased characters and all remaining
cased characters have lower case.
  * `translate(self, table, /)`
    Replace each character in the string using the given translation table.

  table
    Translation table, which must be a mapping of Unicode ordinals to
    Unicode ordinals, strings, or None.

The table must implement lookup/indexing via __getitem__, for instance a
dictionary or list.  If this operation raises LookupError, the character is
left untouched.  Characters mapped to None are deleted.
  * `upper(self, /)`
    Return a copy of the string converted to uppercase.
  * `zfill(self, width, /)`
    Pad a numeric string with zeros on the left, to fill a field of the given width.

The string is never truncated.
#### Class: `CEDARScriptEditor`
Constructor: `CEDARScriptEditor(self, root_path)`
  * `apply_commands(self, commands: collections.abc.Sequence[cedarscript_ast_parser.cedarscript_ast_parser.Command])`
  * `find_identifier(self, source_info: tuple[str, str | collections.abc.Sequence[str]], marker: cedarscript_ast_parser.cedarscript_ast_parser.Marker) -> text_manipulation.range_spec.IdentifierBoundaries`
  * `find_index_range_for_region(self, region: cedarscript_ast_parser.cedarscript_ast_parser.BodyOrWhole | cedarscript_ast_parser.cedarscript_ast_parser.Marker | cedarscript_ast_parser.cedarscript_ast_parser.Segment | cedarscript_ast_parser.cedarscript_ast_parser.RelativeMarker, lines: collections.abc.Sequence[str], identifier_resolver: Callable[[cedarscript_ast_parser.cedarscript_ast_parser.Marker], text_manipulation.range_spec.IdentifierBoundaries], search_range: text_manipulation.range_spec.RangeSpec | text_manipulation.range_spec.IdentifierBoundaries | None = None) -> text_manipulation.range_spec.RangeSpec`
#### Class: `CEDARScriptEditorException`
Constructor: `CEDARScriptEditorException(self, command_ordinal: int, description: str)`
  * `add_note(self, object, /)`
    Exception.add_note(note) --
    add a note to the exception
  * `with_traceback(self, object, /)`
    Exception.with_traceback(tb) --
    set self.__traceback__ to tb and return self.
* `Callable(*args, **kwargs)`
  Deprecated alias to collections.abc.Callable.

    Callable[[int], str] signifies a function that takes a single
    parameter of type int and returns a str.

    The subscription syntax must always be used with exactly two
    values: the argument list and the return type.
    The argument list must be a list of types, a ParamSpec,
    Concatenate or ellipsis. The return type must be a single type.

    There is no syntax to indicate optional or keyword arguments;
    such function types are rarely used as callback types.
#### Class: `Command`
Constructor: `Command(self, type: str) -> None`
  Command(type: str)
#### Class: `DeleteClause`
Constructor: `DeleteClause(self, region: cedarscript_ast_parser.cedarscript_ast_parser.BodyOrWhole | cedarscript_ast_parser.cedarscript_ast_parser.Marker | cedarscript_ast_parser.cedarscript_ast_parser.Segment) -> None`
  DeleteClause(region: cedarscript_ast_parser.cedarscript_ast_parser.BodyOrWhole | cedarscript_ast_parser.cedarscript_ast_parser.Marker | cedarscript_ast_parser.cedarscript_ast_parser.Segment)
#### Class: `IdentifierBoundaries`
Constructor: `IdentifierBoundaries(self, /, *args, **kwargs)`
  IdentifierBoundaries(whole, body)
  * `count(self, value, /)`
    Return number of occurrences of value.
  * `index(self, value, start=0, stop=9223372036854775807, /)`
    Return first index of value.

Raises ValueError if the value is not present.
  * `location_to_search_range(self, location: cedarscript_ast_parser.cedarscript_ast_parser.BodyOrWhole | cedarscript_ast_parser.cedarscript_ast_parser.RelativePositionType) -> text_manipulation.range_spec.RangeSpec`
#### Class: `IdentifierFromFile`
Constructor: `IdentifierFromFile(self, file_path: str, identifier_type: cedarscript_ast_parser.cedarscript_ast_parser.MarkerType, name: str, where_clause: cedarscript_ast_parser.cedarscript_ast_parser.WhereClause, offset: int | None = None) -> None`
  IdentifierFromFile(file_path: str, identifier_type: cedarscript_ast_parser.cedarscript_ast_parser.MarkerType, name: str, where_clause: cedarscript_ast_parser.cedarscript_ast_parser.WhereClause, offset: int | None = None)
#### Class: `IndentationInfo`
Constructor: `IndentationInfo(self, /, *args, **kwargs)`
  A class to represent and manage indentation information.

This class analyzes and provides utilities for working with indentation.
It detects the indentation character (space or tab),
the number of characters used for each indentation level, and provides
methods to adjust and normalize indentation.

Attributes:
    char_count (int): The number of characters used for each indentation level.
    char (str): The character used for indentation (' ' for space, '        ' for tab).
    min_indent_level (int): The minimum indentation level found in the analyzed content.
    consistency (bool): Whether the indentation is consistent throughout the content.
    message (str | None): A message describing the indentation analysis results.

Class Methods:
    from_content: Analyzes the indentation in the given content and creates an IndentationInfo instance.

Methods:
    level_difference: Calculates the difference in indentation levels.
    char_count_to_level: Converts a character count to an indentation level.
    level_to_chars: Converts an indentation level to a string of indentation characters.
    shift_indentation: Adjusts the indentation of a sequence of lines.
    apply_relative_indents: Applies relative indentation based on annotations in the content.

Note:
    This class is particularly useful for processing Python code with varying
    or inconsistent indentation, and for adjusting indentation to meet specific
    formatting requirements.
  * `apply_relative_indents(self, content: str | collections.abc.Sequence[str], context_indent_count: int = 0) -> list[str]`
    Applies relative indentation based on annotations in the content.

This method processes the input content, interpreting special annotations
to apply relative indentation. It uses '@' followed by a number to indicate
relative indentation levels.

Args:
    content (str | Sequence[str]): The content to process. Can be a string
                                   or a sequence of strings.
    context_indent_count (int, optional): The base indentation count of the
                                          context. Defaults to 0.

Returns:
    list[str]: A new list of strings with normalized indentation (without the annotations)

Note:
    - Lines starting with '@n:' (where n is an integer) are interpreted as
      having a relative indentation of n levels from the context indent level.
    - Empty lines and lines with only whitespace are removed.
    - The method uses the IndentationInfo of the instance to determine
      the indentation character and count.
    - This method is particularly useful for content with varying
      indentation levels specified by annotations.

Raises:
    AssertionError: If the calculated indentation level for any line is negative.
  * `char_count_to_level(self, char_count: int) -> int`
  * `count(self, value, /)`
    Return number of occurrences of value.
  * `from_content(content: str | collections.abc.Sequence[str]) -> 'IndentationInfo'`
    Analyzes the indentation in the given content and creates an IndentationInfo instance.

This method examines the indentation patterns in the provided content,
determines the dominant indentation character and count, and assesses
the consistency of indentation throughout the content.

Args:
    content (str | Sequence[str]): The content to analyze. Can be a string
                                   or a sequence of strings.

Returns:
    IndentationInfo: An instance of IndentationInfo with the analysis results.

Note:
    - If no indentation is found, it assumes 4 spaces as per PEP 8.
    - For space indentation, it attempts to determine the most likely
      character count by analyzing patterns and using GCD.
  * `index(self, value, start=0, stop=9223372036854775807, /)`
    Return first index of value.

Raises ValueError if the value is not present.
  * `level_difference(self, base_indentation_count: int)`
  * `level_to_chars(self, level: int) -> str`
  * `shift_indentation(self, lines: collections.abc.Sequence[str], target_base_indentation_count: int) -> list[str]`
    Shifts the indentation of a sequence of lines based on a base indentation count.

This method adjusts the indentation of each non-empty line in the input sequence.
It calculates the difference between the base indentation and the minimum
indentation found in the content, then applies this shift to all lines.

Args:
    lines (Sequence[str]): A sequence of strings representing the lines to be adjusted.
    target_base_indentation_count (int): The base indentation count to adjust from.

Returns:
    list[str]: A new list of strings with adjusted indentation.

Note:
    - Empty lines and lines with only whitespace are preserved as-is.
    - The method uses the IndentationInfo of the instance to determine
      the indentation character and count.
    - This method is useful for uniformly adjusting indentation across all lines.
#### Class: `InsertClause`
Constructor: `InsertClause(self, insert_position: cedarscript_ast_parser.cedarscript_ast_parser.RelativeMarker) -> None`
  InsertClause(insert_position: cedarscript_ast_parser.cedarscript_ast_parser.RelativeMarker)
#### Class: `Marker`
Constructor: `Marker(self, type: cedarscript_ast_parser.cedarscript_ast_parser.MarkerType, value: str | int | None, offset: int | None = None, marker_subtype: str | None = None) -> None`
  A marker can be one of:
- LINE with string/number value
- LINE REGEX with regex pattern
- LINE PREFIX with prefix string
- LINE SUFFIX with suffix string
- VARIABLE with name
- FUNCTION with name
- CLASS with name
See also: Marker.to_search_range
  * `to_search_range(self, lines: collections.abc.Sequence[str], search_range: text_manipulation.range_spec.RangeSpec = RangeSpec(start=0, end=-1, indent=0)) -> text_manipulation.range_spec.RangeSpec | None`
  * `with_qualifier(self, qualifier: cedarscript_ast_parser.cedarscript_ast_parser.RelativePositionType)`
#### Class: `MarkerCompatible`
Constructor: `MarkerCompatible(self, /, *args, **kwargs)`
  * `as_marker(self) -> 'Marker'`
#### Class: `MarkerType`
Constructor: `MarkerType(self, *args, **kwds)`
  * `capitalize(self, /)`
    Return a capitalized version of the string.

More specifically, make the first character have upper case and the rest lower
case.
  * `casefold(self, /)`
    Return a version of the string suitable for caseless comparisons.
  * `center(self, width, fillchar=' ', /)`
    Return a centered string of length width.

Padding is done using the specified fill character (default is a space).
  * `count()`
    Return the number of non-overlapping occurrences of substring sub in string S[start:end].

Optional arguments start and end are interpreted as in slice notation.
  * `encode(self, /, encoding='utf-8', errors='strict')`
    Encode the string using the codec registered for encoding.

  encoding
    The encoding in which to encode the string.
  errors
    The error handling scheme to use for encoding errors.
    The default is 'strict' meaning that encoding errors raise a
    UnicodeEncodeError.  Other possible values are 'ignore', 'replace' and
    'xmlcharrefreplace' as well as any other name registered with
    codecs.register_error that can handle UnicodeEncodeErrors.
  * `endswith()`
    Return True if the string ends with the specified suffix, False otherwise.

  suffix
    A string or a tuple of strings to try.
  start
    Optional start position. Default: start of the string.
  end
    Optional stop position. Default: end of the string.
  * `expandtabs(self, /, tabsize=8)`
    Return a copy where all tab characters are expanded using spaces.

If tabsize is not given, a tab size of 8 characters is assumed.
  * `find()`
    Return the lowest index in S where substring sub is found, such that sub is contained within S[start:end].

Optional arguments start and end are interpreted as in slice notation.
Return -1 on failure.
  * `format(self, /, *args, **kwargs)`
    Return a formatted version of the string, using substitutions from args and kwargs.
The substitutions are identified by braces ('{' and '}').
  * `format_map(self, mapping, /)`
    Return a formatted version of the string, using substitutions from mapping.
The substitutions are identified by braces ('{' and '}').
  * `index()`
    Return the lowest index in S where substring sub is found, such that sub is contained within S[start:end].

Optional arguments start and end are interpreted as in slice notation.
Raises ValueError when the substring is not found.
  * `isalnum(self, /)`
    Return True if the string is an alpha-numeric string, False otherwise.

A string is alpha-numeric if all characters in the string are alpha-numeric and
there is at least one character in the string.
  * `isalpha(self, /)`
    Return True if the string is an alphabetic string, False otherwise.

A string is alphabetic if all characters in the string are alphabetic and there
is at least one character in the string.
  * `isascii(self, /)`
    Return True if all characters in the string are ASCII, False otherwise.

ASCII characters have code points in the range U+0000-U+007F.
Empty string is ASCII too.
  * `isdecimal(self, /)`
    Return True if the string is a decimal string, False otherwise.

A string is a decimal string if all characters in the string are decimal and
there is at least one character in the string.
  * `isdigit(self, /)`
    Return True if the string is a digit string, False otherwise.

A string is a digit string if all characters in the string are digits and there
is at least one character in the string.
  * `isidentifier(self, /)`
    Return True if the string is a valid Python identifier, False otherwise.

Call keyword.iskeyword(s) to test whether string s is a reserved identifier,
such as "def" or "class".
  * `islower(self, /)`
    Return True if the string is a lowercase string, False otherwise.

A string is lowercase if all cased characters in the string are lowercase and
there is at least one cased character in the string.
  * `isnumeric(self, /)`
    Return True if the string is a numeric string, False otherwise.

A string is numeric if all characters in the string are numeric and there is at
least one character in the string.
  * `isprintable(self, /)`
    Return True if all characters in the string are printable, False otherwise.

A character is printable if repr() may use it in its output.
  * `isspace(self, /)`
    Return True if the string is a whitespace string, False otherwise.

A string is whitespace if all characters in the string are whitespace and there
is at least one character in the string.
  * `istitle(self, /)`
    Return True if the string is a title-cased string, False otherwise.

In a title-cased string, upper- and title-case characters may only
follow uncased characters and lowercase characters only cased ones.
  * `isupper(self, /)`
    Return True if the string is an uppercase string, False otherwise.

A string is uppercase if all cased characters in the string are uppercase and
there is at least one cased character in the string.
  * `join(self, iterable, /)`
    Concatenate any number of strings.

The string whose method is called is inserted in between each given string.
The result is returned as a new string.

Example: '.'.join(['ab', 'pq', 'rs']) -> 'ab.pq.rs'
  * `ljust(self, width, fillchar=' ', /)`
    Return a left-justified string of length width.

Padding is done using the specified fill character (default is a space).
  * `lower(self, /)`
    Return a copy of the string converted to lowercase.
  * `lstrip(self, chars=None, /)`
    Return a copy of the string with leading whitespace removed.

If chars is given and not None, remove characters in chars instead.
  * `maketrans()`
    Return a translation table usable for str.translate().

If there is only one argument, it must be a dictionary mapping Unicode
ordinals (integers) or characters to Unicode ordinals, strings or None.
Character keys will be then converted to ordinals.
If there are two arguments, they must be strings of equal length, and
in the resulting dictionary, each character in x will be mapped to the
character at the same position in y. If there is a third argument, it
must be a string, whose characters will be mapped to None in the result.
  * `partition(self, sep, /)`
    Partition the string into three parts using the given separator.

This will search for the separator in the string.  If the separator is found,
returns a 3-tuple containing the part before the separator, the separator
itself, and the part after it.

If the separator is not found, returns a 3-tuple containing the original string
and two empty strings.
  * `removeprefix(self, prefix, /)`
    Return a str with the given prefix string removed if present.

If the string starts with the prefix string, return string[len(prefix):].
Otherwise, return a copy of the original string.
  * `removesuffix(self, suffix, /)`
    Return a str with the given suffix string removed if present.

If the string ends with the suffix string and that suffix is not empty,
return string[:-len(suffix)]. Otherwise, return a copy of the original
string.
  * `replace(self, old, new, /, count=-1)`
    Return a copy with all occurrences of substring old replaced by new.

  count
    Maximum number of occurrences to replace.
    -1 (the default value) means replace all occurrences.

If the optional argument count is given, only the first count occurrences are
replaced.
  * `rfind()`
    Return the highest index in S where substring sub is found, such that sub is contained within S[start:end].

Optional arguments start and end are interpreted as in slice notation.
Return -1 on failure.
  * `rindex()`
    Return the highest index in S where substring sub is found, such that sub is contained within S[start:end].

Optional arguments start and end are interpreted as in slice notation.
Raises ValueError when the substring is not found.
  * `rjust(self, width, fillchar=' ', /)`
    Return a right-justified string of length width.

Padding is done using the specified fill character (default is a space).
  * `rpartition(self, sep, /)`
    Partition the string into three parts using the given separator.

This will search for the separator in the string, starting at the end. If
the separator is found, returns a 3-tuple containing the part before the
separator, the separator itself, and the part after it.

If the separator is not found, returns a 3-tuple containing two empty strings
and the original string.
  * `rsplit(self, /, sep=None, maxsplit=-1)`
    Return a list of the substrings in the string, using sep as the separator string.

  sep
    The separator used to split the string.

    When set to None (the default value), will split on any whitespace
    character (including \n \r \t \f and spaces) and will discard
    empty strings from the result.
  maxsplit
    Maximum number of splits.
    -1 (the default value) means no limit.

Splitting starts at the end of the string and works to the front.
  * `rstrip(self, chars=None, /)`
    Return a copy of the string with trailing whitespace removed.

If chars is given and not None, remove characters in chars instead.
  * `split(self, /, sep=None, maxsplit=-1)`
    Return a list of the substrings in the string, using sep as the separator string.

  sep
    The separator used to split the string.

    When set to None (the default value), will split on any whitespace
    character (including \n \r \t \f and spaces) and will discard
    empty strings from the result.
  maxsplit
    Maximum number of splits.
    -1 (the default value) means no limit.

Splitting starts at the front of the string and works to the end.

Note, str.split() is mainly useful for data that has been intentionally
delimited.  With natural text that includes punctuation, consider using
the regular expression module.
  * `splitlines(self, /, keepends=False)`
    Return a list of the lines in the string, breaking at line boundaries.

Line breaks are not included in the resulting list unless keepends is given and
true.
  * `startswith()`
    Return True if the string starts with the specified prefix, False otherwise.

  prefix
    A string or a tuple of strings to try.
  start
    Optional start position. Default: start of the string.
  end
    Optional stop position. Default: end of the string.
  * `strip(self, chars=None, /)`
    Return a copy of the string with leading and trailing whitespace removed.

If chars is given and not None, remove characters in chars instead.
  * `swapcase(self, /)`
    Convert uppercase characters to lowercase and lowercase characters to uppercase.
  * `title(self, /)`
    Return a version of the string where each word is titlecased.

More specifically, words start with uppercased characters and all remaining
cased characters have lower case.
  * `translate(self, table, /)`
    Replace each character in the string using the given translation table.

  table
    Translation table, which must be a mapping of Unicode ordinals to
    Unicode ordinals, strings, or None.

The table must implement lookup/indexing via __getitem__, for instance a
dictionary or list.  If this operation raises LookupError, the character is
left untouched.  Characters mapped to None are deleted.
  * `upper(self, /)`
    Return a copy of the string converted to uppercase.
  * `zfill(self, width, /)`
    Pad a numeric string with zeros on the left, to fill a field of the given width.

The string is never truncated.
#### Class: `MoveClause`
Constructor: `MoveClause(self, insert_position: cedarscript_ast_parser.cedarscript_ast_parser.RelativeMarker, region: cedarscript_ast_parser.cedarscript_ast_parser.BodyOrWhole | cedarscript_ast_parser.cedarscript_ast_parser.Marker | cedarscript_ast_parser.cedarscript_ast_parser.Segment, to_other_file: cedarscript_ast_parser.cedarscript_ast_parser.SingleFileClause | None = None, relative_indentation: int | None = None) -> None`
  MoveClause(insert_position: cedarscript_ast_parser.cedarscript_ast_parser.RelativeMarker, region: cedarscript_ast_parser.cedarscript_ast_parser.BodyOrWhole | cedarscript_ast_parser.cedarscript_ast_parser.Marker | cedarscript_ast_parser.cedarscript_ast_parser.Segment, to_other_file: cedarscript_ast_parser.cedarscript_ast_parser.SingleFileClause | None = None, relative_indentation: int | None = None)
#### Class: `MvFileCommand`
Constructor: `MvFileCommand(self, type: str, file_path: str, target_path: str) -> None`
  MvFileCommand(type: str, file_path: str, target_path: str)
#### Class: `RangeSpec`
Constructor: `RangeSpec(self, /, *args, **kwargs)`
  RangeSpec(start, end, indent)
  * `count(self, value, /)`
    Return number of occurrences of value.
  * `dec(self, count: int = 1)`
  * `delete(self, src: collections.abc.Sequence[str]) -> collections.abc.Sequence[str]`
  * `from_line_marker(lines: collections.abc.Sequence[str], search_term: cedarscript_ast_parser.cedarscript_ast_parser.Marker, search_range: 'RangeSpec' = None)`
    Find the index of a specified line within a list of strings, considering different match types and an offset.

This function searches for a given line within a list, considering 4 types of matches in order of priority:
1. Exact match
2. Stripped match (ignoring leading and trailing whitespace)
3. Normalized match (ignoring non-alphanumeric characters)
4. Partial (Searching for a substring, using `casefold` to ignore upper- and lower-case differences).

The function applies the offset across all match types while maintaining the priority order.

:Args:
    :param lines: The list of strings to search through.
    :param search_term:
        search_marker.value: The line to search for.
        search_marker.offset: The number of matches to skip before returning a result.
                  0 skips no match and returns the first match, 1 returns the second match, and so on.
    :param search_range: The index to start the search from and to end the search at (exclusive).
                          Defaults to (0, -1), which means search to the end of the list.

:returns:
    RangeSpec: The index for the desired line in the 'lines' list.
         Returns None if no match is found or if the offset exceeds the number of matches within each category.

:Example:
    >> lines = ["Hello, world!", "  Hello, world!  ", "Héllo, wörld?", "Another line", "Hello, world!"]
    >> _find_line_index(lines, "Hello, world!", 1)
    4  # Returns the index of the second exact match

Note:
    - The function prioritizes match types in the order: exact, stripped, normalized, partial.
    - The offset is considered separately for each type.
  * `inc(self, count: int = 1)`
  * `index(self, value, start=0, stop=9223372036854775807, /)`
    Return first index of value.

Raises ValueError if the value is not present.
  * `normalize_line(line: str)`
  * `read(self, src: collections.abc.Sequence[str]) -> collections.abc.Sequence[str]`
  * `set_line_count(self, range_len: int)`
  * `write(self, src: collections.abc.Sequence[str], target: collections.abc.Sequence[str])`
#### Class: `RegionClause`
Constructor: `RegionClause(self, region: cedarscript_ast_parser.cedarscript_ast_parser.BodyOrWhole | cedarscript_ast_parser.cedarscript_ast_parser.Marker | cedarscript_ast_parser.cedarscript_ast_parser.Segment) -> None`
  RegionClause(region: cedarscript_ast_parser.cedarscript_ast_parser.BodyOrWhole | cedarscript_ast_parser.cedarscript_ast_parser.Marker | cedarscript_ast_parser.cedarscript_ast_parser.Segment)
#### Class: `RelativeMarker`
Constructor: `RelativeMarker(self, qualifier: cedarscript_ast_parser.cedarscript_ast_parser.RelativePositionType, *args, **kwargs)`
  * `to_search_range(self, lines: collections.abc.Sequence[str], search_range: text_manipulation.range_spec.RangeSpec = RangeSpec(start=0, end=-1, indent=0)) -> text_manipulation.range_spec.RangeSpec | None`
  * `with_qualifier(self, qualifier: cedarscript_ast_parser.cedarscript_ast_parser.RelativePositionType)`
#### Class: `RelativePositionType`
Constructor: `RelativePositionType(self, *args, **kwds)`
  * `capitalize(self, /)`
    Return a capitalized version of the string.

More specifically, make the first character have upper case and the rest lower
case.
  * `casefold(self, /)`
    Return a version of the string suitable for caseless comparisons.
  * `center(self, width, fillchar=' ', /)`
    Return a centered string of length width.

Padding is done using the specified fill character (default is a space).
  * `count()`
    Return the number of non-overlapping occurrences of substring sub in string S[start:end].

Optional arguments start and end are interpreted as in slice notation.
  * `encode(self, /, encoding='utf-8', errors='strict')`
    Encode the string using the codec registered for encoding.

  encoding
    The encoding in which to encode the string.
  errors
    The error handling scheme to use for encoding errors.
    The default is 'strict' meaning that encoding errors raise a
    UnicodeEncodeError.  Other possible values are 'ignore', 'replace' and
    'xmlcharrefreplace' as well as any other name registered with
    codecs.register_error that can handle UnicodeEncodeErrors.
  * `endswith()`
    Return True if the string ends with the specified suffix, False otherwise.

  suffix
    A string or a tuple of strings to try.
  start
    Optional start position. Default: start of the string.
  end
    Optional stop position. Default: end of the string.
  * `expandtabs(self, /, tabsize=8)`
    Return a copy where all tab characters are expanded using spaces.

If tabsize is not given, a tab size of 8 characters is assumed.
  * `find()`
    Return the lowest index in S where substring sub is found, such that sub is contained within S[start:end].

Optional arguments start and end are interpreted as in slice notation.
Return -1 on failure.
  * `format(self, /, *args, **kwargs)`
    Return a formatted version of the string, using substitutions from args and kwargs.
The substitutions are identified by braces ('{' and '}').
  * `format_map(self, mapping, /)`
    Return a formatted version of the string, using substitutions from mapping.
The substitutions are identified by braces ('{' and '}').
  * `index()`
    Return the lowest index in S where substring sub is found, such that sub is contained within S[start:end].

Optional arguments start and end are interpreted as in slice notation.
Raises ValueError when the substring is not found.
  * `isalnum(self, /)`
    Return True if the string is an alpha-numeric string, False otherwise.

A string is alpha-numeric if all characters in the string are alpha-numeric and
there is at least one character in the string.
  * `isalpha(self, /)`
    Return True if the string is an alphabetic string, False otherwise.

A string is alphabetic if all characters in the string are alphabetic and there
is at least one character in the string.
  * `isascii(self, /)`
    Return True if all characters in the string are ASCII, False otherwise.

ASCII characters have code points in the range U+0000-U+007F.
Empty string is ASCII too.
  * `isdecimal(self, /)`
    Return True if the string is a decimal string, False otherwise.

A string is a decimal string if all characters in the string are decimal and
there is at least one character in the string.
  * `isdigit(self, /)`
    Return True if the string is a digit string, False otherwise.

A string is a digit string if all characters in the string are digits and there
is at least one character in the string.
  * `isidentifier(self, /)`
    Return True if the string is a valid Python identifier, False otherwise.

Call keyword.iskeyword(s) to test whether string s is a reserved identifier,
such as "def" or "class".
  * `islower(self, /)`
    Return True if the string is a lowercase string, False otherwise.

A string is lowercase if all cased characters in the string are lowercase and
there is at least one cased character in the string.
  * `isnumeric(self, /)`
    Return True if the string is a numeric string, False otherwise.

A string is numeric if all characters in the string are numeric and there is at
least one character in the string.
  * `isprintable(self, /)`
    Return True if all characters in the string are printable, False otherwise.

A character is printable if repr() may use it in its output.
  * `isspace(self, /)`
    Return True if the string is a whitespace string, False otherwise.

A string is whitespace if all characters in the string are whitespace and there
is at least one character in the string.
  * `istitle(self, /)`
    Return True if the string is a title-cased string, False otherwise.

In a title-cased string, upper- and title-case characters may only
follow uncased characters and lowercase characters only cased ones.
  * `isupper(self, /)`
    Return True if the string is an uppercase string, False otherwise.

A string is uppercase if all cased characters in the string are uppercase and
there is at least one cased character in the string.
  * `join(self, iterable, /)`
    Concatenate any number of strings.

The string whose method is called is inserted in between each given string.
The result is returned as a new string.

Example: '.'.join(['ab', 'pq', 'rs']) -> 'ab.pq.rs'
  * `ljust(self, width, fillchar=' ', /)`
    Return a left-justified string of length width.

Padding is done using the specified fill character (default is a space).
  * `lower(self, /)`
    Return a copy of the string converted to lowercase.
  * `lstrip(self, chars=None, /)`
    Return a copy of the string with leading whitespace removed.

If chars is given and not None, remove characters in chars instead.
  * `maketrans()`
    Return a translation table usable for str.translate().

If there is only one argument, it must be a dictionary mapping Unicode
ordinals (integers) or characters to Unicode ordinals, strings or None.
Character keys will be then converted to ordinals.
If there are two arguments, they must be strings of equal length, and
in the resulting dictionary, each character in x will be mapped to the
character at the same position in y. If there is a third argument, it
must be a string, whose characters will be mapped to None in the result.
  * `partition(self, sep, /)`
    Partition the string into three parts using the given separator.

This will search for the separator in the string.  If the separator is found,
returns a 3-tuple containing the part before the separator, the separator
itself, and the part after it.

If the separator is not found, returns a 3-tuple containing the original string
and two empty strings.
  * `removeprefix(self, prefix, /)`
    Return a str with the given prefix string removed if present.

If the string starts with the prefix string, return string[len(prefix):].
Otherwise, return a copy of the original string.
  * `removesuffix(self, suffix, /)`
    Return a str with the given suffix string removed if present.

If the string ends with the suffix string and that suffix is not empty,
return string[:-len(suffix)]. Otherwise, return a copy of the original
string.
  * `replace(self, old, new, /, count=-1)`
    Return a copy with all occurrences of substring old replaced by new.

  count
    Maximum number of occurrences to replace.
    -1 (the default value) means replace all occurrences.

If the optional argument count is given, only the first count occurrences are
replaced.
  * `rfind()`
    Return the highest index in S where substring sub is found, such that sub is contained within S[start:end].

Optional arguments start and end are interpreted as in slice notation.
Return -1 on failure.
  * `rindex()`
    Return the highest index in S where substring sub is found, such that sub is contained within S[start:end].

Optional arguments start and end are interpreted as in slice notation.
Raises ValueError when the substring is not found.
  * `rjust(self, width, fillchar=' ', /)`
    Return a right-justified string of length width.

Padding is done using the specified fill character (default is a space).
  * `rpartition(self, sep, /)`
    Partition the string into three parts using the given separator.

This will search for the separator in the string, starting at the end. If
the separator is found, returns a 3-tuple containing the part before the
separator, the separator itself, and the part after it.

If the separator is not found, returns a 3-tuple containing two empty strings
and the original string.
  * `rsplit(self, /, sep=None, maxsplit=-1)`
    Return a list of the substrings in the string, using sep as the separator string.

  sep
    The separator used to split the string.

    When set to None (the default value), will split on any whitespace
    character (including \n \r \t \f and spaces) and will discard
    empty strings from the result.
  maxsplit
    Maximum number of splits.
    -1 (the default value) means no limit.

Splitting starts at the end of the string and works to the front.
  * `rstrip(self, chars=None, /)`
    Return a copy of the string with trailing whitespace removed.

If chars is given and not None, remove characters in chars instead.
  * `split(self, /, sep=None, maxsplit=-1)`
    Return a list of the substrings in the string, using sep as the separator string.

  sep
    The separator used to split the string.

    When set to None (the default value), will split on any whitespace
    character (including \n \r \t \f and spaces) and will discard
    empty strings from the result.
  maxsplit
    Maximum number of splits.
    -1 (the default value) means no limit.

Splitting starts at the front of the string and works to the end.

Note, str.split() is mainly useful for data that has been intentionally
delimited.  With natural text that includes punctuation, consider using
the regular expression module.
  * `splitlines(self, /, keepends=False)`
    Return a list of the lines in the string, breaking at line boundaries.

Line breaks are not included in the resulting list unless keepends is given and
true.
  * `startswith()`
    Return True if the string starts with the specified prefix, False otherwise.

  prefix
    A string or a tuple of strings to try.
  start
    Optional start position. Default: start of the string.
  end
    Optional stop position. Default: end of the string.
  * `strip(self, chars=None, /)`
    Return a copy of the string with leading and trailing whitespace removed.

If chars is given and not None, remove characters in chars instead.
  * `swapcase(self, /)`
    Convert uppercase characters to lowercase and lowercase characters to uppercase.
  * `title(self, /)`
    Return a version of the string where each word is titlecased.

More specifically, words start with uppercased characters and all remaining
cased characters have lower case.
  * `translate(self, table, /)`
    Replace each character in the string using the given translation table.

  table
    Translation table, which must be a mapping of Unicode ordinals to
    Unicode ordinals, strings, or None.

The table must implement lookup/indexing via __getitem__, for instance a
dictionary or list.  If this operation raises LookupError, the character is
left untouched.  Characters mapped to None are deleted.
  * `upper(self, /)`
    Return a copy of the string converted to uppercase.
  * `zfill(self, width, /)`
    Pad a numeric string with zeros on the left, to fill a field of the given width.

The string is never truncated.
#### Class: `ReplaceClause`
Constructor: `ReplaceClause(self, region: cedarscript_ast_parser.cedarscript_ast_parser.BodyOrWhole | cedarscript_ast_parser.cedarscript_ast_parser.Marker | cedarscript_ast_parser.cedarscript_ast_parser.Segment) -> None`
  ReplaceClause(region: cedarscript_ast_parser.cedarscript_ast_parser.BodyOrWhole | cedarscript_ast_parser.cedarscript_ast_parser.Marker | cedarscript_ast_parser.cedarscript_ast_parser.Segment)
#### Class: `RmFileCommand`
Constructor: `RmFileCommand(self, type: str, file_path: str) -> None`
  RmFileCommand(type: str, file_path: str)
#### Class: `Segment`
Constructor: `Segment(self, start: cedarscript_ast_parser.cedarscript_ast_parser.RelativeMarker, end: cedarscript_ast_parser.cedarscript_ast_parser.RelativeMarker) -> None`
  Segment(start: cedarscript_ast_parser.cedarscript_ast_parser.RelativeMarker, end: cedarscript_ast_parser.cedarscript_ast_parser.RelativeMarker)
  * `to_search_range(self, lines: collections.abc.Sequence[str], search_range: text_manipulation.range_spec.RangeSpec = RangeSpec(start=0, end=-1, indent=0)) -> text_manipulation.range_spec.RangeSpec | None`
#### Class: `SelectCommand`
Constructor: `SelectCommand(self, type: str, target: Union[ForwardRef('FileNamesPathsTarget'), ForwardRef('OtherTarget')], source: Union[ForwardRef('SingleFileClause'), ForwardRef('MultiFileClause')], where_clause: cedarscript_ast_parser.cedarscript_ast_parser.WhereClause | None = None, limit: int | None = None) -> None`
  SelectCommand(type: str, target: Union[ForwardRef('FileNamesPathsTarget'), ForwardRef('OtherTarget')], source: Union[ForwardRef('SingleFileClause'), ForwardRef('MultiFileClause')], where_clause: cedarscript_ast_parser.cedarscript_ast_parser.WhereClause | None = None, limit: int | None = None)
#### Class: `Sequence`
Constructor: `Sequence(self, /, *args, **kwargs)`
  All the operations on a read-only sequence.

Concrete subclasses must override __new__ or __init__,
__getitem__, and __len__.
  * `count(self, value)`
    S.count(value) -> integer -- return number of occurrences of value
  * `index(self, value, start=0, stop=None)`
    S.index(value, [start, [stop]]) -> integer -- return first index of value.
Raises ValueError if the value is not present.

Supporting start and stop arguments is optional, but
recommended.
#### Class: `UpdateCommand`
Constructor: `UpdateCommand(self, type: str, target: cedarscript_ast_parser.cedarscript_ast_parser.SingleFileClause | cedarscript_ast_parser.cedarscript_ast_parser.IdentifierFromFile, action: cedarscript_ast_parser.cedarscript_ast_parser.ReplaceClause | cedarscript_ast_parser.cedarscript_ast_parser.DeleteClause | cedarscript_ast_parser.cedarscript_ast_parser.InsertClause | cedarscript_ast_parser.cedarscript_ast_parser.MoveClause, content: str | tuple[cedarscript_ast_parser.cedarscript_ast_parser.BodyOrWhole | cedarscript_ast_parser.cedarscript_ast_parser.Marker | cedarscript_ast_parser.cedarscript_ast_parser.Segment, int | None] | cedarscript_ast_parser.cedarscript_ast_parser.EdScript | cedarscript_ast_parser.cedarscript_ast_parser.CaseStatement | None = None) -> None`
  UpdateCommand(type: str, target: cedarscript_ast_parser.cedarscript_ast_parser.SingleFileClause | cedarscript_ast_parser.cedarscript_ast_parser.IdentifierFromFile, action: cedarscript_ast_parser.cedarscript_ast_parser.ReplaceClause | cedarscript_ast_parser.cedarscript_ast_parser.DeleteClause | cedarscript_ast_parser.cedarscript_ast_parser.InsertClause | cedarscript_ast_parser.cedarscript_ast_parser.MoveClause, content: str | tuple[cedarscript_ast_parser.cedarscript_ast_parser.BodyOrWhole | cedarscript_ast_parser.cedarscript_ast_parser.Marker | cedarscript_ast_parser.cedarscript_ast_parser.Segment, int | None] | cedarscript_ast_parser.cedarscript_ast_parser.EdScript | cedarscript_ast_parser.cedarscript_ast_parser.CaseStatement | None = None)
* `bow_to_search_range(bow: cedarscript_ast_parser.cedarscript_ast_parser.BodyOrWhole, searh_range: text_manipulation.range_spec.IdentifierBoundaries | text_manipulation.range_spec.RangeSpec | None = None) -> text_manipulation.range_spec.RangeSpec`
* `find_marker_or_segment(action: cedarscript_ast_parser.cedarscript_ast_parser.ReplaceClause | cedarscript_ast_parser.cedarscript_ast_parser.DeleteClause | cedarscript_ast_parser.cedarscript_ast_parser.InsertClause | cedarscript_ast_parser.cedarscript_ast_parser.MoveClause, lines: collections.abc.Sequence[str], search_range: text_manipulation.range_spec.RangeSpec) -> tuple[cedarscript_ast_parser.cedarscript_ast_parser.Marker, text_manipulation.range_spec.RangeSpec]`
* `read_file(file_path: str | os.PathLike) -> str`
* `restrict_search_range(action, target, identifier_resolver: Callable[[cedarscript_ast_parser.cedarscript_ast_parser.Marker], text_manipulation.range_spec.IdentifierBoundaries]) -> text_manipulation.range_spec.RangeSpec`
* `restrict_search_range_for_marker(marker: cedarscript_ast_parser.cedarscript_ast_parser.Marker, action: cedarscript_ast_parser.cedarscript_ast_parser.ReplaceClause | cedarscript_ast_parser.cedarscript_ast_parser.DeleteClause | cedarscript_ast_parser.cedarscript_ast_parser.InsertClause | cedarscript_ast_parser.cedarscript_ast_parser.MoveClause, lines: collections.abc.Sequence[str], search_range: text_manipulation.range_spec.RangeSpec, identifier_resolver: Callable[[cedarscript_ast_parser.cedarscript_ast_parser.Marker], text_manipulation.range_spec.IdentifierBoundaries]) -> text_manipulation.range_spec.RangeSpec`
* `select_finder(root_path: str, file_name: str, source: str) -> Callable[[str, str, str, cedarscript_ast_parser.cedarscript_ast_parser.Marker], text_manipulation.range_spec.IdentifierBoundaries | None]`
* `write_file(file_path: str | os.PathLike, lines: collections.abc.Sequence[str])`
### Function: `find_commands(content: str)`
### Module: `identifier_selector`
* `Callable(*args, **kwargs)`
  Deprecated alias to collections.abc.Callable.

    Callable[[int], str] signifies a function that takes a single
    parameter of type int and returns a str.

    The subscription syntax must always be used with exactly two
    values: the argument list and the return type.
    The argument list must be a list of types, a ParamSpec,
    Concatenate or ellipsis. The return type must be a single type.

    There is no syntax to indicate optional or keyword arguments;
    such function types are rarely used as callback types.
#### Class: `IdentifierBoundaries`
Constructor: `IdentifierBoundaries(self, /, *args, **kwargs)`
  IdentifierBoundaries(whole, body)
  * `count(self, value, /)`
    Return number of occurrences of value.
  * `index(self, value, start=0, stop=9223372036854775807, /)`
    Return first index of value.

Raises ValueError if the value is not present.
  * `location_to_search_range(self, location: cedarscript_ast_parser.cedarscript_ast_parser.BodyOrWhole | cedarscript_ast_parser.cedarscript_ast_parser.RelativePositionType) -> text_manipulation.range_spec.RangeSpec`
#### Class: `Marker`
Constructor: `Marker(self, type: cedarscript_ast_parser.cedarscript_ast_parser.MarkerType, value: str | int | None, offset: int | None = None, marker_subtype: str | None = None) -> None`
  A marker can be one of:
- LINE with string/number value
- LINE REGEX with regex pattern
- LINE PREFIX with prefix string
- LINE SUFFIX with suffix string
- VARIABLE with name
- FUNCTION with name
- CLASS with name
See also: Marker.to_search_range
  * `to_search_range(self, lines: collections.abc.Sequence[str], search_range: text_manipulation.range_spec.RangeSpec = RangeSpec(start=0, end=-1, indent=0)) -> text_manipulation.range_spec.RangeSpec | None`
  * `with_qualifier(self, qualifier: cedarscript_ast_parser.cedarscript_ast_parser.RelativePositionType)`
* `find_python_identifier(root_path: str, file_name: str, source: str, marker: cedarscript_ast_parser.cedarscript_ast_parser.Marker) -> text_manipulation.range_spec.IdentifierBoundaries | None`
  Find the starting line index of a specified function in the given lines.

:param root_path:
:param file_name:
:param source: Source code.
:param marker: Type, name and offset of the identifier to find.
TODO: If `None` when there are 2 or more identifiers with the same name, raise exception.
:return: IdentifierBoundaries with identifier start, body start, and end lines of the identifier
or None if not found.
* `select_finder(root_path: str, file_name: str, source: str) -> Callable[[str, str, str, cedarscript_ast_parser.cedarscript_ast_parser.Marker], text_manipulation.range_spec.IdentifierBoundaries | None]`
### Module: `python_identifier_finder`
#### Class: `IdentifierBoundaries`
Constructor: `IdentifierBoundaries(self, /, *args, **kwargs)`
  IdentifierBoundaries(whole, body)
  * `count(self, value, /)`
    Return number of occurrences of value.
  * `index(self, value, start=0, stop=9223372036854775807, /)`
    Return first index of value.

Raises ValueError if the value is not present.
  * `location_to_search_range(self, location: cedarscript_ast_parser.cedarscript_ast_parser.BodyOrWhole | cedarscript_ast_parser.cedarscript_ast_parser.RelativePositionType) -> text_manipulation.range_spec.RangeSpec`
#### Class: `Marker`
Constructor: `Marker(self, type: cedarscript_ast_parser.cedarscript_ast_parser.MarkerType, value: str | int | None, offset: int | None = None, marker_subtype: str | None = None) -> None`
  A marker can be one of:
- LINE with string/number value
- LINE REGEX with regex pattern
- LINE PREFIX with prefix string
- LINE SUFFIX with suffix string
- VARIABLE with name
- FUNCTION with name
- CLASS with name
See also: Marker.to_search_range
  * `to_search_range(self, lines: collections.abc.Sequence[str], search_range: text_manipulation.range_spec.RangeSpec = RangeSpec(start=0, end=-1, indent=0)) -> text_manipulation.range_spec.RangeSpec | None`
  * `with_qualifier(self, qualifier: cedarscript_ast_parser.cedarscript_ast_parser.RelativePositionType)`
#### Class: `MarkerType`
Constructor: `MarkerType(self, *args, **kwds)`
  * `capitalize(self, /)`
    Return a capitalized version of the string.

More specifically, make the first character have upper case and the rest lower
case.
  * `casefold(self, /)`
    Return a version of the string suitable for caseless comparisons.
  * `center(self, width, fillchar=' ', /)`
    Return a centered string of length width.

Padding is done using the specified fill character (default is a space).
  * `count()`
    Return the number of non-overlapping occurrences of substring sub in string S[start:end].

Optional arguments start and end are interpreted as in slice notation.
  * `encode(self, /, encoding='utf-8', errors='strict')`
    Encode the string using the codec registered for encoding.

  encoding
    The encoding in which to encode the string.
  errors
    The error handling scheme to use for encoding errors.
    The default is 'strict' meaning that encoding errors raise a
    UnicodeEncodeError.  Other possible values are 'ignore', 'replace' and
    'xmlcharrefreplace' as well as any other name registered with
    codecs.register_error that can handle UnicodeEncodeErrors.
  * `endswith()`
    Return True if the string ends with the specified suffix, False otherwise.

  suffix
    A string or a tuple of strings to try.
  start
    Optional start position. Default: start of the string.
  end
    Optional stop position. Default: end of the string.
  * `expandtabs(self, /, tabsize=8)`
    Return a copy where all tab characters are expanded using spaces.

If tabsize is not given, a tab size of 8 characters is assumed.
  * `find()`
    Return the lowest index in S where substring sub is found, such that sub is contained within S[start:end].

Optional arguments start and end are interpreted as in slice notation.
Return -1 on failure.
  * `format(self, /, *args, **kwargs)`
    Return a formatted version of the string, using substitutions from args and kwargs.
The substitutions are identified by braces ('{' and '}').
  * `format_map(self, mapping, /)`
    Return a formatted version of the string, using substitutions from mapping.
The substitutions are identified by braces ('{' and '}').
  * `index()`
    Return the lowest index in S where substring sub is found, such that sub is contained within S[start:end].

Optional arguments start and end are interpreted as in slice notation.
Raises ValueError when the substring is not found.
  * `isalnum(self, /)`
    Return True if the string is an alpha-numeric string, False otherwise.

A string is alpha-numeric if all characters in the string are alpha-numeric and
there is at least one character in the string.
  * `isalpha(self, /)`
    Return True if the string is an alphabetic string, False otherwise.

A string is alphabetic if all characters in the string are alphabetic and there
is at least one character in the string.
  * `isascii(self, /)`
    Return True if all characters in the string are ASCII, False otherwise.

ASCII characters have code points in the range U+0000-U+007F.
Empty string is ASCII too.
  * `isdecimal(self, /)`
    Return True if the string is a decimal string, False otherwise.

A string is a decimal string if all characters in the string are decimal and
there is at least one character in the string.
  * `isdigit(self, /)`
    Return True if the string is a digit string, False otherwise.

A string is a digit string if all characters in the string are digits and there
is at least one character in the string.
  * `isidentifier(self, /)`
    Return True if the string is a valid Python identifier, False otherwise.

Call keyword.iskeyword(s) to test whether string s is a reserved identifier,
such as "def" or "class".
  * `islower(self, /)`
    Return True if the string is a lowercase string, False otherwise.

A string is lowercase if all cased characters in the string are lowercase and
there is at least one cased character in the string.
  * `isnumeric(self, /)`
    Return True if the string is a numeric string, False otherwise.

A string is numeric if all characters in the string are numeric and there is at
least one character in the string.
  * `isprintable(self, /)`
    Return True if all characters in the string are printable, False otherwise.

A character is printable if repr() may use it in its output.
  * `isspace(self, /)`
    Return True if the string is a whitespace string, False otherwise.

A string is whitespace if all characters in the string are whitespace and there
is at least one character in the string.
  * `istitle(self, /)`
    Return True if the string is a title-cased string, False otherwise.

In a title-cased string, upper- and title-case characters may only
follow uncased characters and lowercase characters only cased ones.
  * `isupper(self, /)`
    Return True if the string is an uppercase string, False otherwise.

A string is uppercase if all cased characters in the string are uppercase and
there is at least one cased character in the string.
  * `join(self, iterable, /)`
    Concatenate any number of strings.

The string whose method is called is inserted in between each given string.
The result is returned as a new string.

Example: '.'.join(['ab', 'pq', 'rs']) -> 'ab.pq.rs'
  * `ljust(self, width, fillchar=' ', /)`
    Return a left-justified string of length width.

Padding is done using the specified fill character (default is a space).
  * `lower(self, /)`
    Return a copy of the string converted to lowercase.
  * `lstrip(self, chars=None, /)`
    Return a copy of the string with leading whitespace removed.

If chars is given and not None, remove characters in chars instead.
  * `maketrans()`
    Return a translation table usable for str.translate().

If there is only one argument, it must be a dictionary mapping Unicode
ordinals (integers) or characters to Unicode ordinals, strings or None.
Character keys will be then converted to ordinals.
If there are two arguments, they must be strings of equal length, and
in the resulting dictionary, each character in x will be mapped to the
character at the same position in y. If there is a third argument, it
must be a string, whose characters will be mapped to None in the result.
  * `partition(self, sep, /)`
    Partition the string into three parts using the given separator.

This will search for the separator in the string.  If the separator is found,
returns a 3-tuple containing the part before the separator, the separator
itself, and the part after it.

If the separator is not found, returns a 3-tuple containing the original string
and two empty strings.
  * `removeprefix(self, prefix, /)`
    Return a str with the given prefix string removed if present.

If the string starts with the prefix string, return string[len(prefix):].
Otherwise, return a copy of the original string.
  * `removesuffix(self, suffix, /)`
    Return a str with the given suffix string removed if present.

If the string ends with the suffix string and that suffix is not empty,
return string[:-len(suffix)]. Otherwise, return a copy of the original
string.
  * `replace(self, old, new, /, count=-1)`
    Return a copy with all occurrences of substring old replaced by new.

  count
    Maximum number of occurrences to replace.
    -1 (the default value) means replace all occurrences.

If the optional argument count is given, only the first count occurrences are
replaced.
  * `rfind()`
    Return the highest index in S where substring sub is found, such that sub is contained within S[start:end].

Optional arguments start and end are interpreted as in slice notation.
Return -1 on failure.
  * `rindex()`
    Return the highest index in S where substring sub is found, such that sub is contained within S[start:end].

Optional arguments start and end are interpreted as in slice notation.
Raises ValueError when the substring is not found.
  * `rjust(self, width, fillchar=' ', /)`
    Return a right-justified string of length width.

Padding is done using the specified fill character (default is a space).
  * `rpartition(self, sep, /)`
    Partition the string into three parts using the given separator.

This will search for the separator in the string, starting at the end. If
the separator is found, returns a 3-tuple containing the part before the
separator, the separator itself, and the part after it.

If the separator is not found, returns a 3-tuple containing two empty strings
and the original string.
  * `rsplit(self, /, sep=None, maxsplit=-1)`
    Return a list of the substrings in the string, using sep as the separator string.

  sep
    The separator used to split the string.

    When set to None (the default value), will split on any whitespace
    character (including \n \r \t \f and spaces) and will discard
    empty strings from the result.
  maxsplit
    Maximum number of splits.
    -1 (the default value) means no limit.

Splitting starts at the end of the string and works to the front.
  * `rstrip(self, chars=None, /)`
    Return a copy of the string with trailing whitespace removed.

If chars is given and not None, remove characters in chars instead.
  * `split(self, /, sep=None, maxsplit=-1)`
    Return a list of the substrings in the string, using sep as the separator string.

  sep
    The separator used to split the string.

    When set to None (the default value), will split on any whitespace
    character (including \n \r \t \f and spaces) and will discard
    empty strings from the result.
  maxsplit
    Maximum number of splits.
    -1 (the default value) means no limit.

Splitting starts at the front of the string and works to the end.

Note, str.split() is mainly useful for data that has been intentionally
delimited.  With natural text that includes punctuation, consider using
the regular expression module.
  * `splitlines(self, /, keepends=False)`
    Return a list of the lines in the string, breaking at line boundaries.

Line breaks are not included in the resulting list unless keepends is given and
true.
  * `startswith()`
    Return True if the string starts with the specified prefix, False otherwise.

  prefix
    A string or a tuple of strings to try.
  start
    Optional start position. Default: start of the string.
  end
    Optional stop position. Default: end of the string.
  * `strip(self, chars=None, /)`
    Return a copy of the string with leading and trailing whitespace removed.

If chars is given and not None, remove characters in chars instead.
  * `swapcase(self, /)`
    Convert uppercase characters to lowercase and lowercase characters to uppercase.
  * `title(self, /)`
    Return a version of the string where each word is titlecased.

More specifically, words start with uppercased characters and all remaining
cased characters have lower case.
  * `translate(self, table, /)`
    Replace each character in the string using the given translation table.

  table
    Translation table, which must be a mapping of Unicode ordinals to
    Unicode ordinals, strings, or None.

The table must implement lookup/indexing via __getitem__, for instance a
dictionary or list.  If this operation raises LookupError, the character is
left untouched.  Characters mapped to None are deleted.
  * `upper(self, /)`
    Return a copy of the string converted to uppercase.
  * `zfill(self, width, /)`
    Pad a numeric string with zeros on the left, to fill a field of the given width.

The string is never truncated.
#### Class: `RangeSpec`
Constructor: `RangeSpec(self, /, *args, **kwargs)`
  RangeSpec(start, end, indent)
  * `count(self, value, /)`
    Return number of occurrences of value.
  * `dec(self, count: int = 1)`
  * `delete(self, src: collections.abc.Sequence[str]) -> collections.abc.Sequence[str]`
  * `from_line_marker(lines: collections.abc.Sequence[str], search_term: cedarscript_ast_parser.cedarscript_ast_parser.Marker, search_range: 'RangeSpec' = None)`
    Find the index of a specified line within a list of strings, considering different match types and an offset.

This function searches for a given line within a list, considering 4 types of matches in order of priority:
1. Exact match
2. Stripped match (ignoring leading and trailing whitespace)
3. Normalized match (ignoring non-alphanumeric characters)
4. Partial (Searching for a substring, using `casefold` to ignore upper- and lower-case differences).

The function applies the offset across all match types while maintaining the priority order.

:Args:
    :param lines: The list of strings to search through.
    :param search_term:
        search_marker.value: The line to search for.
        search_marker.offset: The number of matches to skip before returning a result.
                  0 skips no match and returns the first match, 1 returns the second match, and so on.
    :param search_range: The index to start the search from and to end the search at (exclusive).
                          Defaults to (0, -1), which means search to the end of the list.

:returns:
    RangeSpec: The index for the desired line in the 'lines' list.
         Returns None if no match is found or if the offset exceeds the number of matches within each category.

:Example:
    >> lines = ["Hello, world!", "  Hello, world!  ", "Héllo, wörld?", "Another line", "Hello, world!"]
    >> _find_line_index(lines, "Hello, world!", 1)
    4  # Returns the index of the second exact match

Note:
    - The function prioritizes match types in the order: exact, stripped, normalized, partial.
    - The offset is considered separately for each type.
  * `inc(self, count: int = 1)`
  * `index(self, value, start=0, stop=9223372036854775807, /)`
    Return first index of value.

Raises ValueError if the value is not present.
  * `normalize_line(line: str)`
  * `read(self, src: collections.abc.Sequence[str]) -> collections.abc.Sequence[str]`
  * `set_line_count(self, range_len: int)`
  * `write(self, src: collections.abc.Sequence[str], target: collections.abc.Sequence[str])`
#### Class: `Sequence`
Constructor: `Sequence(self, /, *args, **kwargs)`
  All the operations on a read-only sequence.

Concrete subclasses must override __new__ or __init__,
__getitem__, and __len__.
  * `count(self, value)`
    S.count(value) -> integer -- return number of occurrences of value
  * `index(self, value, start=0, stop=None)`
    S.index(value, [start, [stop]]) -> integer -- return first index of value.
Raises ValueError if the value is not present.

Supporting start and stop arguments is optional, but
recommended.
* `find_python_identifier(root_path: str, file_name: str, source: str, marker: cedarscript_ast_parser.cedarscript_ast_parser.Marker) -> text_manipulation.range_spec.IdentifierBoundaries | None`
  Find the starting line index of a specified function in the given lines.

:param root_path:
:param file_name:
:param source: Source code.
:param marker: Type, name and offset of the identifier to find.
TODO: If `None` when there are 2 or more identifiers with the same name, raise exception.
:return: IdentifierBoundaries with identifier start, body start, and end lines of the identifier
or None if not found.
* `get_by_offset(obj: collections.abc.Sequence, offset: int)`
* `get_line_indent_count(line: str)`
### Module: `re`
#### Class: `Match`
Constructor: `Match(self, /, *args, **kwargs)`
  The result of re.match() and re.search().
Match objects always have a boolean value of True.
  * `end(self, group=0, /)`
    Return index of the end of the substring matched by group.
  * `expand(self, /, template)`
    Return the string obtained by doing backslash substitution on the string template, as done by the sub() method.
  * `group()`
    group([group1, ...]) -> str or tuple.
    Return subgroup(s) of the match by indices or names.
    For 0 returns the entire match.
  * `groupdict(self, /, default=None)`
    Return a dictionary containing all the named subgroups of the match, keyed by the subgroup name.

  default
    Is used for groups that did not participate in the match.
  * `groups(self, /, default=None)`
    Return a tuple containing all the subgroups of the match, from 1.

  default
    Is used for groups that did not participate in the match.
  * `span(self, group=0, /)`
    For match object m, return the 2-tuple (m.start(group), m.end(group)).
  * `start(self, group=0, /)`
    Return index of the start of the substring matched by group.
#### Class: `Pattern`
Constructor: `Pattern(self, /, *args, **kwargs)`
  Compiled regular expression object.
  * `findall(self, /, string, pos=0, endpos=9223372036854775807)`
    Return a list of all non-overlapping matches of pattern in string.
  * `finditer(self, /, string, pos=0, endpos=9223372036854775807)`
    Return an iterator over all non-overlapping matches for the RE pattern in string.

For each match, the iterator returns a match object.
  * `fullmatch(self, /, string, pos=0, endpos=9223372036854775807)`
    Matches against all of the string.
  * `match(self, /, string, pos=0, endpos=9223372036854775807)`
    Matches zero or more characters at the beginning of the string.
  * `scanner(self, /, string, pos=0, endpos=9223372036854775807)`
  * `search(self, /, string, pos=0, endpos=9223372036854775807)`
    Scan through string looking for a match, and return a corresponding match object instance.

Return None if no position in the string matches.
  * `split(self, /, string, maxsplit=0)`
    Split string by the occurrences of pattern.
  * `sub(self, /, repl, string, count=0)`
    Return the string obtained by replacing the leftmost non-overlapping occurrences of pattern in string by the replacement repl.
  * `subn(self, /, repl, string, count=0)`
    Return the tuple (new_string, number_of_subs_made) found by replacing the leftmost non-overlapping occurrences of pattern with the replacement repl.
#### Class: `PatternError`
Constructor: `PatternError(self, msg, pattern=None, pos=None)`
  Exception raised for invalid regular expressions.

Attributes:

    msg: The unformatted error message
    pattern: The regular expression pattern
    pos: The index in the pattern where compilation failed (may be None)
    lineno: The line corresponding to pos (may be None)
    colno: The column corresponding to pos (may be None)
  * `add_note(self, object, /)`
    Exception.add_note(note) --
    add a note to the exception
  * `with_traceback(self, object, /)`
    Exception.with_traceback(tb) --
    set self.__traceback__ to tb and return self.
#### Class: `RegexFlag`
Constructor: `RegexFlag(self, *args, **kwds)`
  An enumeration.
  * `as_integer_ratio(self, /)`
    Return a pair of integers, whose ratio is equal to the original int.

The ratio is in lowest terms and has a positive denominator.

>>> (10).as_integer_ratio()
(10, 1)
>>> (-10).as_integer_ratio()
(-10, 1)
>>> (0).as_integer_ratio()
(0, 1)
  * `bit_count(self, /)`
    Number of ones in the binary representation of the absolute value of self.

Also known as the population count.

>>> bin(13)
'0b1101'
>>> (13).bit_count()
3
  * `bit_length(self, /)`
    Number of bits necessary to represent self in binary.

>>> bin(37)
'0b100101'
>>> (37).bit_length()
6
  * `conjugate(self, /)`
    Returns self, the complex conjugate of any int.
  * `from_bytes(bytes, byteorder='big', *, signed=False)`
    Return the integer represented by the given array of bytes.

  bytes
    Holds the array of bytes to convert.  The argument must either
    support the buffer protocol or be an iterable object producing bytes.
    Bytes and bytearray are examples of built-in objects that support the
    buffer protocol.
  byteorder
    The byte order used to represent the integer.  If byteorder is 'big',
    the most significant byte is at the beginning of the byte array.  If
    byteorder is 'little', the most significant byte is at the end of the
    byte array.  To request the native byte order of the host system, use
    sys.byteorder as the byte order value.  Default is to use 'big'.
  signed
    Indicates whether two's complement is used to represent the integer.
  * `is_integer(self, /)`
    Returns True. Exists for duck type compatibility with float.is_integer.
  * `to_bytes(self, /, length=1, byteorder='big', *, signed=False)`
    Return an array of bytes representing an integer.

  length
    Length of bytes object to use.  An OverflowError is raised if the
    integer is not representable with the given number of bytes.  Default
    is length 1.
  byteorder
    The byte order used to represent the integer.  If byteorder is 'big',
    the most significant byte is at the beginning of the byte array.  If
    byteorder is 'little', the most significant byte is at the end of the
    byte array.  To request the native byte order of the host system, use
    sys.byteorder as the byte order value.  Default is to use 'big'.
  signed
    Determines whether two's complement is used to represent the integer.
    If signed is False and a negative integer is given, an OverflowError
    is raised.
#### Class: `Scanner`
Constructor: `Scanner(self, lexicon, flags=0)`
  * `scan(self, string)`
* `compile(pattern, flags=0)`
  Compile a regular expression pattern, returning a Pattern object.
#### Class: `error`
Constructor: `error(self, msg, pattern=None, pos=None)`
  Exception raised for invalid regular expressions.

Attributes:

    msg: The unformatted error message
    pattern: The regular expression pattern
    pos: The index in the pattern where compilation failed (may be None)
    lineno: The line corresponding to pos (may be None)
    colno: The column corresponding to pos (may be None)
  * `add_note(self, object, /)`
    Exception.add_note(note) --
    add a note to the exception
  * `with_traceback(self, object, /)`
    Exception.with_traceback(tb) --
    set self.__traceback__ to tb and return self.
* `escape(pattern)`
  Escape special characters in a string.
* `findall(pattern, string, flags=0)`
  Return a list of all non-overlapping matches in the string.

If one or more capturing groups are present in the pattern, return
a list of groups; this will be a list of tuples if the pattern
has more than one group.

Empty matches are included in the result.
* `finditer(pattern, string, flags=0)`
  Return an iterator over all non-overlapping matches in the
string.  For each match, the iterator returns a Match object.

Empty matches are included in the result.
* `fullmatch(pattern, string, flags=0)`
  Try to apply the pattern to all of the string, returning
a Match object, or None if no match was found.
* `match(pattern, string, flags=0)`
  Try to apply the pattern at the start of the string, returning
a Match object, or None if no match was found.
* `purge()`
  Clear the regular expression caches
* `search(pattern, string, flags=0)`
  Scan through string looking for a match to the pattern, returning
a Match object, or None if no match was found.
* `split(pattern, string, maxsplit=0, flags=0)`
  Split the source string by the occurrences of the pattern,
returning a list containing the resulting substrings.  If
capturing parentheses are used in pattern, then the text of all
groups in the pattern are also returned as part of the resulting
list.  If maxsplit is nonzero, at most maxsplit splits occur,
and the remainder of the string is returned as the final element
of the list.
* `sub(pattern, repl, string, count=0, flags=0)`
  Return the string obtained by replacing the leftmost
non-overlapping occurrences of the pattern in string by the
replacement repl.  repl can be either a string or a callable;
if a string, backslash escapes in it are processed.  If it is
a callable, it's passed the Match object and must return
a replacement string to be used.
* `subn(pattern, repl, string, count=0, flags=0)`
  Return a 2-tuple containing (new_string, number).
new_string is the string obtained by replacing the leftmost
non-overlapping occurrences of the pattern in the source
string by the replacement repl.  number is the number of
substitutions that were made. repl can be either a string or a
callable; if a string, backslash escapes in it are processed.
If it is a callable, it's passed the Match object and must
return a replacement string to be used.