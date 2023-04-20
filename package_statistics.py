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
Displays deb package statistics for various architectures.
"""
import heapq
import gzip
import os
import requests
import sys

# Defines the supported architectures.
ARCHITECTURES = dict.fromkeys([
    "all",
    "amd64",
    "arm64",
    "armel",
    "armhf",
    "i386",
    "mips64el",
    "mipsel",
    "ppc64el",
    "s390x",
    "source",
    "udeb-all",
    "udeb-amd64",
    "udeb-arm64",
    "udeb-armel",
    "udeb-armhf",
    "udeb-i386",
    "udeb-mips64el",
    "udeb-mipsel",
    "udeb-ppc64el",
    "udeb-s390x",
])

# Defines the debian mirror to use.
DEBIAN_MIRROR = "http://ftp.uk.debian.org/debian/dists/stable/main/"

# Defines the folder to store the downloaded files.
DOWNLOADS_FOLDER = "./downloads/"


# Produces a generic usage message.
def usage_message() -> str:
  return (
      f"Usage: {sys.argv[0]} ARCHITECTURE\n\n"
      f"Supported architectures: {' '.join(ARCHITECTURES)}"
  )


# Produces an error message in case the architecture argument is missing.
def missing_architecture_error() -> str:
  return "Missing architecture argument.\n" + usage_message()


# Produces an error message in case of an invalid or unsupported architecture.
def invalid_architecture_error(architecture: str) -> str:
  return (
      f"Invalid or unsupported architecture: {architecture}\n" + usage_message()
  )


# Downloads the contents file for the given architecture, unless it has been
# already downloaded, and returns the filepath of the downloaded file.
def maybe_download_contents(architecture: str) -> str:
  # Create the downloads folder if it doesn't exist.
  if not os.path.isdir(DOWNLOADS_FOLDER):
    os.makedirs(DOWNLOADS_FOLDER)

  filename = f"Contents-{architecture}.gz"
  filepath = f"{DOWNLOADS_FOLDER}/{filename}"

  # Skip downloading the file if it already exists.
  if os.path.isfile(filepath):
    return filepath

  # Download as a stream and save it to persistent storage.
  url = f"{DEBIAN_MIRROR}/{filename}"
  response = requests.get(url, stream=True, timeout=60)
  with open(filepath, "wb") as f:
    f.write(response.raw.read())

  return filepath


# Decompresses a .gz file and returns its contents as a string
def decompress_gz(filepath: str) -> str:
  with gzip.open(filepath, "rt") as f:
    return f.read()


# Gets the package from a contents line
def get_package(line: str) -> str:
  # Find the last space in the line and return the suffix. We use this
  # approach because file names may contain spaces, thus breaking the
  # standard split() method.
  last_space_index = line.rfind(" ")
  return line[last_space_index + 1 :]


# Returns a dictionary where the key represents a package and the value
# represents the number of files associated with this package.
# Input: the decompressed contents file.
def count_files_per_package(contents: str) -> dict[str, int]:
  file_count = {}

  # Split the file into lines, where each line represents a package.
  lines = contents.splitlines()

  # Process each package.
  for line in lines:
    package = get_package(line)

    # Increment the file counter of this package.
    if package in file_count:
      file_count[package] = file_count[package] + 1
    else:
      file_count[package] = 1

  return file_count


# Prints the top K packages from the `stats` dictionary, based on how many files
# each package is associated with. Each dictionary represents a {k, v} value,
# where k = package name, v = number of files the package is associated with.
#
# Time Complexity: O(N + K*log(N)) where N = number of packages.
# Space Complexity: O(N) for auxilliary memory.
#
# Note: if K is constant and K << N, e.g., K = 10, then this essentially runs
# in O(N) time.
def print_top_packages(stats: dict[str, int]) -> None:
  # Create a tuple list from the given dictionary, in order to create a heap.
  # Since `heapify` creates a min heap, use the negative values of file counts
  # so that we end up with an equivalent max heap.
  tuplist = [(-v, k) for k, v in stats.items()]

  # Make a max heap out of the tuples based on the number of files associated
  # with each package. This takes O(N) time, where N = number of packages.
  heapq.heapify(tuplist)

  # Print the top K packages in O(K*log(N)) time.
  for i in range(1, 10):
    if len(tuplist) == 0:
      break

    # Remove the top element in O(log(N)) time and print it.
    top = heapq.heappop(tuplist)
    package = top[1]
    count = abs(top[0])
    print(f"{package} : {count}")


def main() -> None:
  # Require that we have at least one ARCHITECTURE argument.
  # Note: excessive arguments are allowed, but ignored.
  if len(sys.argv) < 2:
    raise ValueError(missing_architecture_error())

  # Check whether the argument represents a valid architecture.
  architecture = sys.argv[1]
  if architecture not in ARCHITECTURES:
    raise ValueError(invalid_architecture_error(architecture))

  filepath = maybe_download_contents(architecture)
  contents = decompress_gz(filepath)

  file_count = count_files_per_package(contents)

  print_top_packages(file_count)


if __name__ == "__main__":
  main()
