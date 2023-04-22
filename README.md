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

## Development Tools

Development tools that were used for this project include:

- The [Pyink][pyink] auto-formatter.
- The [Pylint][pylint] static code analyzer.

## Allocated Time

About 12 hours were allocated to this project in its entirety. This allocated
time was used to:

- Gather requirements, reach out to the company for clarifications, and make
  assumptions.
- Conduct research on the style guide to follow and decide on the most suitable
  auto-formatter and the static code analyzer.
- Read and understand the [contents file format][contents] and design the
  core functionality of the tool.
- Implement the core functionality of the code.
- Refactor the code for readability across different classes and/or modules.
- Optimize the time complexity to find the top `K` packages.
- Provide documentation as module, function, or class docstrings.
- Write explanatory inline comments to illustrate the rationale be hind the
  implementation decisions.

[contents]: https://wiki.debian.org/RepositoryFormat#A.22Contents.22_indices
[pyink]: https://github.com/google/pyink
[pylint]: https://pypi.org/project/pylint
