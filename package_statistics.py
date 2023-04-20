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


if __name__ == "__main__":
  main()