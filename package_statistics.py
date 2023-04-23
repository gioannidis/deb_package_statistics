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
Displays the debian packages with the most associated files for an architecture.

Downloads the Contents file for a given architecture or the "source"
pseudo-architecture, computes the packages that have the most files associated
with them, and returns the top 10 packages. Users can optionally change the
number of the top packages to print.

Example usages:
    ./package_statistics.py amd64
        Prints the top 10 packages for the amd64 architecture.

    ./package_statistics.py i386 42
        Prints the top 42 packages for the i386 architecture.
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

DEFAULT_TOP_K_PACKAGES = 10
"""Defines the top K packages to be retrieved when executing the main()"""

# Defines the folder to store the downloaded files.
DOWNLOADS_FOLDER = "./downloads/"


def usage_message() -> str:
    """Produces a generic usage message for this executable."""
    return (
        f"Usage: {sys.argv[0]} <architecture> [top_k]\n\n"
        f"Supported architectures: {' '.join(ARCHITECTURES)}\n"
        "top_k: number of top K packages to print "
        f"(default: {DEFAULT_TOP_K_PACKAGES}); if zero (0), prints all packages"
    )


def missing_architecture_error() -> str:
    """Produces an error message for a missing architecture argument."""
    return "Missing architecture argument.\n" + usage_message()


def invalid_architecture_error(architecture: str) -> str:
    """Produces an error message for an invalid or unsupported architecture."""
    return (
        f"Invalid or unsupported architecture: {architecture}\n"
        + usage_message()
    )


class PackageStatistics:
    """Computes debian package statistics for various architectures.

    Provides an API to download the contents index of debian packages for a
    given architecture, compute the number of files associated with each
    package, and print the packages that have the most files associated with
    them.

    Attributes:
        _mirror: A string of the debian mirror URL to download the contents.
        _path: A string representing the path where the contents files are
            saved at.
    """

    def __init__(self, mirror: str, path: str):
        """Initializes the instance based on the debian mirror.

        Args:
            mirror: the URL of the debian mirror to download the contents from.
            _path: A string representing the path where the contents files are
                saved at.
        """
        self._mirror = mirror
        self._path = path

    def get_top_packages(
        self, architecture: str, top_k: int | None = None
    ) -> list[tuple[str, int]]:
        """Finds the packages that have the most files associated with them.

        Retrieves the debian Contents file for a given architecture and returns
        the top K packages based on the number of files associated with them.

        Time Complexity: O(N + K*log(N)), where:
            N = number of packages, i.e., the size of the `stats` dictionary
            K = the `top_k` argument. If K is None or K > N, then K = N.
        Space Complexity: O(N) for auxiliary memory.

        Note: if K is constant and K << N, e.g., K = 10, then this method runs
        essentially in O(N) time.

        Args:
            architecture: A string representing the target architecture.

            top_k: An integer or None. If set, it limits the number of the top
                K packages to be retrieved. If None, all packages are returned.

        Returns:
            A list of (str, int) tuples, where the first element is a string
            representing a package and the second element is an integer
            representing the number of files associated with the package. The
            tuples are sorted in descending order by the number of associated
            files, i.e., their second element.
        """
        filepath = self._maybe_download_contents(architecture)
        contents = self._decompress_gz(filepath)

        file_count = self._count_files_per_package(contents)
        return self._find_top_packages(file_count, top_k)

    def _decompress_gz(self, filepath: str) -> str:
        """Decompresses a .gz file and returns its contents as a string."""
        with gzip.open(filepath, "rt") as f:
            return f.read()

    def _maybe_download_contents(self, architecture: str) -> str:
        """Downloads the contents file a debian architecture.

        Connects to the `_mirror` and downloads the compressed contents file
        for the given architecture. already downloaded, and returns the filepath
        of the downloaded file. Saves the downloaded to the `_path` and creates
        the folder if it doesn't exist.

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
        if not os.path.isdir(self._path):
            os.makedirs(self._path)

        filename = f"Contents-{architecture}.gz"
        filepath = f"{self._path}/{filename}"

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
        comma separated packages, and returns the packages as a list.

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

        Processes a decompressed Contents file stored in memory and computes
        the number of files that each package is associated with. Each line in
        the file represents a single file that can be associated with multiple
        packages. The contents are tokenized by lines and each line is processed
        separately.

        This also ignores a potential header line, where the first line can
        optionally contain the columns "FILE" and "LOCATION".

        Args:
            contents: A string representing the decompressed contents file.

        Returns:
            A (key, value) dictionary where:
                key: A string representing a package.
                value: An integer representing the number of files associated
                    with the package.
        """
        file_count = {}
        lines = contents.splitlines()

        # Retrieve the package list that each file (line) is associated with and
        # increment the counter of each associated package.
        for i, line in enumerate(lines):
            packages = self._get_packages(line)

            # Ignore the first line if it is a header line.
            if (
                i == 0
                and len(packages) == 1
                and packages[0] == "LOCATION"
                and line.find("FILE") >= 0
            ):
                continue

            for package in packages:
                if package in file_count:
                    file_count[package] = file_count[package] + 1
                else:
                    file_count[package] = 1

        return file_count

    def _find_top_packages(
        self, stats: dict[str, int], top_k: int | None
    ) -> list[tuple[str, int]]:
        """Finds the packages that have the most files associated with them.

        Processes a dictionary mapping each package to the number of files
        associated with it, performs a partial sort of this dictionary based on
        how many file each package is associated with, and returns the top K
        packages based on the number of files associated with them.

        The partial sort is implemented by creating a heap from the dictionary
        in linear time and then extracting the top K elements.

        Refer to the documentation of `get_top_packages` for the time and space
        complexity.

        Args:
            stats: A dictionary mapping a string to an integer.
                key: A string representing a package.
                value: An integer representing the number of files associated
                    with the package.

            top_k: An integer or None, representing the top packages to
                retrieve. Refer to the documentation of `get_top_packages` for
                more details.

        Returns:
            A list of (str, int) tuples, representing packages and number of
            files associated with them. Refer to the documentation of
            `get_top_packages` for more details.
        """
        # Create a tuple list that will be used as the max heap elements. Place
        # the dictionary value as the first element so that the heap uses this
        # value as the sorting criterion.
        # NOTE: since `heapify` creates a min heap, we use the negative values
        # of file counts so that we end up with an equivalent max heap.
        tuplist = [(-v, k) for k, v in stats.items()]

        heapq.heapify(tuplist)

        # Handle the case when `top_k` has not been set. This results in
        # returning all packages.
        if top_k is None:
            top_k = len(tuplist)

        # Extract the top K packages in O(K*log(N)) time.
        packages = []
        for _ in range(0, top_k):
            if len(tuplist) == 0:
                break

            top = heapq.heappop(tuplist)
            package = top[1]
            count = abs(top[0])
            packages.append((package, count))

        return packages


def main() -> None:
    """Retrieves and prints the top K package for a given architecture.

    Parses the arguments and validates that the target architecture is given
    and represents a valid architecture. Instantiates a PackageStatistics class,
    retrieves the `DEFAULT_TOP_K_PACKAGES` and prints them in a human-friendly
    format.
    """
    # Require that we have at least one ARCHITECTURE argument.
    # Note: excessive arguments are allowed, but ignored.
    if len(sys.argv) < 2:
        raise ValueError(missing_architecture_error())

    # Check whether the argument represents a valid architecture.
    architecture = sys.argv[1]
    if architecture not in ARCHITECTURES:
        raise ValueError(invalid_architecture_error(architecture))

    # Check whether an optional second argument has been given, indicating the
    # number of top K packages to print.
    top_k = DEFAULT_TOP_K_PACKAGES
    if len(sys.argv) >= 3:
        top_k = int(sys.argv[2])
        if top_k < 0:
            raise ValueError(f"top_k argument must be non-negative: {top_k}")
        elif top_k == 0:
            # Set it to None, indicating that all packages should be printed.
            top_k = None

    stats = PackageStatistics(DEBIAN_MIRROR, DOWNLOADS_FOLDER)
    packages = stats.get_top_packages(architecture, top_k)

    # Print the packages in a human readable format.
    hline = "-" * 50
    print(hline)
    print(f"{'#': ^3} {'Package': <41}{'Files': <5}")
    print(hline)
    for i, tup in enumerate(packages):
        package, count = tup
        print(f"{i+1: >2}. {package: <41}{count: >5}")

    print(hline)


if __name__ == "__main__":
    main()
