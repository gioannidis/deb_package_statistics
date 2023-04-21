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
import gzip
import heapq
import os
import requests
import sys

from strings import find_last_of

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


def usage_message() -> str:
    """Produces a generic usage message for this script."""
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
        f"Invalid or unsupported architecture: {architecture}\n"
        + usage_message()
    )


# Decompresses a .gz file and returns its contents as a string
def decompress_gz(filepath: str) -> str:
    with gzip.open(filepath, "rt") as f:
        return f.read()


class PackageStatistics:
    """Computes debian package statistics for various architectures.

    Provides an API to download the contents index of debian packages for a
    given architecture, compute the number of files associated with each
    package, and print the packages that have the most files associated with
    them.

    Attributes:
        _mirror: A string of the debian mirror URL to download the contents.

    """

    def __init__(self, mirror: str):
        """Initializes the instance based on the debian mirror.

        Args:
            mirror: the URL of the debian mirror to download the contents from.
        """
        self._mirror = mirror

    def get_top_packages(
        self, architecture: str, top_k: int | None = None
    ) -> None:
        filepath = self._maybe_download_contents(architecture)
        contents = decompress_gz(filepath)

        file_count = self._count_files_per_package(contents)
        self._print_top_packages(file_count)

    def _maybe_download_contents(self, architecture: str) -> str:
        """Downloads the contents file a debian architecture.

        Connects to the `_mirror` and downloads the compressed contents file
        for the given architecture. already downloaded, and returns the filepath
        of the downloaded file. Saves the downloaded to the `DOWNLOADS_FOLDER`
        and creates the folder if it doesn't exist.

        The method skips downloading the contents file if it already exists.

        Args:
            architecture: A string indicating the architecture.

        Returns:
            A string pointing to the pathname of the downloaded compressed
            contents file. Example:

            /path/to/Contents-amd64.gz

        Raises:
            ConnectionError: the connection to the mirror was not possible.
        """
        if not os.path.isdir(DOWNLOADS_FOLDER):
            os.makedirs(DOWNLOADS_FOLDER)

        filename = f"Contents-{architecture}.gz"
        filepath = f"{DOWNLOADS_FOLDER}/{filename}"

        # Skip downloading the file if it already exists.
        if os.path.isfile(filepath):
            return filepath

        url = f"{DEBIAN_MIRROR}/{filename}"
        response = requests.get(url, stream=True, timeout=60)
        with open(filepath, "wb") as f:
            f.write(response.raw.read())

        return filepath

    def _get_packages(self, line: str) -> list[str]:
        """Parses a row from a Contents file and retrieves a list of packages.

        Each line in the contents file has the following format:
            file_name     package_1,package_2,package_3,...,package_N

        File names may contain spaces. The package list, which is a comma
        separated list of packages, is guaranteed to contain no spaces.

        This method finds the last space or tab in the line, tokenizes the
        comma separted packages, and returns the packages as a list.

        Args:
            line: A string representing a line row from a Contents file of a
                Debian architecture. Example:

                /path/to/a/file         package_1,package_2,package_3

        Returns:
            A list of strings representing debian packages. Example:
                ["package_1", "package_2", "package_3"]
        """
        last_space_index = find_last_of(line, " \t")

        # Handle malformed lines, where there is no 2nd column.
        if last_space_index < 0:
            raise ValueError(f"Malformed line in Contents file: {line}")

        packages = line[last_space_index + 1 :]
        return packages.split(",")

    def _count_files_per_package(self, contents: str) -> dict[str, int]:
        """Counts the files associated with each package in a Contents file.

        Returns a dictionary where the key represents a package and the value
        represents the number of files associated with this package.
        Input: the decompressed contents file.
        """
        file_count = {}

        # Split the file into lines, where each line represents a package.
        lines = contents.splitlines()

        # Process each line, updating the file counts for each package associated with
        # each file.
        for line in lines:
            packages = self._get_packages(line)

            # Increment the file counter of this package.
            for package in packages:
                if package in file_count:
                    file_count[package] = file_count[package] + 1
                else:
                    file_count[package] = 1

        return file_count

    def _print_top_packages(
        self, stats: dict[str, int], top_k: int | None = 10
    ) -> None:
        """
        Prints the top K packages from the `stats` dictionary, based on how many files
        each package is associated with. Each dictionary represents a {k, v} value,
        where k = package name, v = number of files the package is associated with.

        If `K` is `None`, then all packages are printed, sorted by descending order
        based on their associated file counts.

        Time Complexity: O(N + K*log(N)) where N = number of packages.
        Space Complexity: O(N) for auxilliary memory.

        Note: if K is constant and K << N, e.g., K = 10, then this essentially runs
        in O(N) time.
        """
        # Create a tuple list from the given dictionary, in order to create a heap.
        # Since `heapify` creates a min heap, use the negative values of file counts
        # so that we end up with an equivalent max heap.
        tuplist = [(-v, k) for k, v in stats.items()]

        # Make a max heap out of the tuples based on the number of files associated
        # with each package. This takes O(N) time, where N = number of packages.
        heapq.heapify(tuplist)

        # Print all packages if no K has been specified.
        if top_k is None:
            top_k = len(tuplist)

        # Print the top K packages in O(K*log(N)) time.
        for i in range(1, top_k):
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

    stats = PackageStatistics(DEBIAN_MIRROR)
    stats.get_top_packages(architecture, 10)


if __name__ == "__main__":
    main()
