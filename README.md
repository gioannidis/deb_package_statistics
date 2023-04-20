# deb_package_statistics
Python command line tool that displays deb package statistics for various
architectures.

## Preface

This repository implements a technical assessment for the purposes of a
recruitment process.

## Instructions

Debian uses `*deb` packages to deploy and upgrade software. The packages are
stored in repositories and each repository contains the so called "Contents
index". The format of that file is well described here:
https://wiki.debian.org/RepositoryFormat#A.22Contents.22_indices

Your task is to develop a python command line tool that takes the architecture
(amd64, arm64, mips etc.) as an argument and downloads the compressed Contents
file associated with it from a Debian mirror. The program should parse the file
and output the statistics of the top 10 packages that have the most files
associated with them. An example output could be:

```bash
./package_statistics.py amd64
    <package name 1>         <number of files>
    <package name 2>         <number of files>
......
    <package name 10>         <number of files>
```

You can use the following Debian mirror:
http://ftp.uk.debian.org/debian/dists/stable/main/. Please try to follow
Python's best practices in your solution. Hint: there are tools that can help
you verify your code is compliant. In-line comments are appreciated.
