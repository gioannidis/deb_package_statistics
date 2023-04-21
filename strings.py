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


# Finds the last occurrence of any one of the characters in `chars` within
# `text` and returns its index. Returns -1 if no matches are found.
def find_last_of(text: str, chars: str) -> int:
    # Create a dictionary from the characters that we are looking to match.
    char_dict = dict.fromkeys(chars)

    # Define the predicate to filter for matching characters.
    def predicate(char: str) -> bool:
        return char in char_dict

    # Reverse the string, so that we find the last occurrence.
    text = text[::-1]

    # Find the first occurrence in the reversed text and return -1 if not found.
    index = next((i for i, ch in enumerate(text) if predicate(ch)), None)

    # Handle case where no match is found.
    if index is None:
        return -1

    # Return the index corresponding to the original string, i.e., the last
    # matching index.
    return len(text) - index - 1
