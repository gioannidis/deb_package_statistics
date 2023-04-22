#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2023 George Ioannidis
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Provides string-related algorithms.
"""


def find_last_of(text: str, pattern: str) -> int:
    """Finds the last occurrence of a character from a pattern in a given text.

    Finds and returns the last position in `text` that represents any one
    character from the given `patter`.

    This is implemented by reversing the original string, as finding the last
    occurrence in the original string is equivalent to finding the first
    occurrence in the reversed string.

    Args:
        text: A string where the last matching character is being searched for.
        pattern: A series of characters used as search patterns.

    Returns:
        An integer representing the index in `text` where the last match from
        `pattern` is found. Returns -1 if no match is found.
    """
    char_dict = dict.fromkeys(pattern)

    def predicate(char: str) -> bool:
        """Filters matching characters in the given pattern."""
        return char in char_dict

    text = text[::-1]

    # NOTE: we specify to return `None` in case of no match, so that no
    # exception is raised.
    index = next((i for i, ch in enumerate(text) if predicate(ch)), None)

    if index is None:
        return -1

    # Return the index corresponding to the original string, i.e., the last
    # matching index.
    return len(text) - index - 1
