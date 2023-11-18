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
PackageStatistics test on local decompressed data.
"""
import unittest
from unittest.mock import patch

from package_statistics import PackageStatistics

_TEST_DATA_PATH = "./test_data/"
_TEST_DATA_DECOMPRESSED_FILE = f"{_TEST_DATA_PATH}/test_contents"


class PackageStatisticsTest(unittest.TestCase):

    def setUp(self):
        self.package_statistics = PackageStatistics(
            mirror="test_mirror", path=_TEST_DATA_PATH
        )
        self.expected = [
            ("packageA", 5),
            ("packageB", 4),
            ("packageC", 3),
            ("packageD", 2),
            ("packageE", 1),
        ]

    @patch.object(PackageStatistics, "_decompress_gz")
    @patch.object(PackageStatistics, "_maybe_download_contents")
    def test_get_all_packages_from_local_data(
        self, mock_download, mock_decompress
    ):
        # Given: the mock _decompress_gz returns the local cleartext file.
        with open(_TEST_DATA_DECOMPRESSED_FILE, "rt", encoding="utf-8") as f:
            contents = f.read()
            mock_decompress.return_value = contents

        # When: the packages for a test architecture are requested.
        packages = self.package_statistics.get_top_packages(architecture="test")

        # Then: each package is mapped to the number of associated files, and
        # packages are sorted by the number of files, in descending order.
        self.assertListEqual(packages, self.expected)

        mock_download.assert_called_once()
        mock_decompress.assert_called_once()


if __name__ == "__main__":
    unittest.main()
