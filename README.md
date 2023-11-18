# deb_package_statistics

Python command line tool that prints the debian packages with the most
associated filenames.

This tool downloads the Contents Indices file for a given architecture or the
"source" pseudo-architecture, computes the packages that have the most filenames
associated with them, and returns the top 10 packages. Users can optionally
tune the number of the top packages to print. The packages are printed in
descending order based on the number of associated filenames.

## Preface

This repository implements a technical assessment that had been requested by a
renowned company in the IT and embedded sector, for the purposes of their
recruitment process. We share this repository to illustrate various aspects of
our work as a Software Engineer, e.g., requirements elicitation, design
implementation, testing, and documentation. The assessment was neither
proprietary or [compensated][compensation], nor any NDA had been concluded, thus
may be shared publicly.

The [instructions](#original-instructions) section describes the original
instructions that were shared by the company for the purposes of this
assessment.

## Requirements

- `python3.7` or higher. This was tested under version `3.11.2`.
- [`gzip`][gzip]
- [`heapq`][heapq]
- [`requests`][requests] version [`v2.28.0`][requests-version] or higher.

## Usage

```
./package_statistics.py <architecture> [top_k]
```

The `architecture` argument can be any one of the following supported (as of
2023-04-25) architectures:

```
all amd64 arm64 armel armhf i386 mips64el mipsel ppc64el s390x source udeb-all udeb-amd64 udeb-arm64 udeb-armel udeb-armhf udeb-i386 udeb-mips64el udeb-mipsel udeb-ppc64el udeb-s390x
```

The `top_k` _optional_ argument can either be:

- A positive integer `K`, indicating the number of top packages that should be
  printed, based on the number of associated filenames from the respective
  Contents Indices file.
- `all`, indicating that all packages should be printed

Example usages:

```
./package_statistics.py amd64
    Prints the top 10 packages for the amd64 architecture.

./package_statistics.py i386 42
    Prints the top 42 packages for the i386 architecture.

./package_statistics.py source all
    Prints all packages for the "source" pseudo-architecture.
```

## Original Instructions

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

## Requirements Elicitation

Prior to designing and implementing this assessment, we researched the
requirements of the system, the stakeholders, and any potential users. Please
refer to the [requirements][requirements] section for more details.

## Performance

### Time Complexity

The time complexity of this tool, excluding any network or decompression
operations, is `O(M*L + K*log(N))`, where:

- `M` is the number of filenames in the decompressed Contents indices file,
    i.e., the number of individual lines.
- `L` is the length of the longest line in the in the Contents indices file.
- `K` is the number of the top packages that we would like to display, based on
    the number of associated filenames.
- `N` is the number of individual packages in the Contents indices file.

In particular:

- `O(M * L)` time is required to process the entire `Contents` file.
- `log(N)` time is required to pop the top package from the heap; we repeat this
  operation `K` times.

Note that `O(N)` time is also required to build a max heap of packages based on
their associated filename counts. However, we can easily illustrate that
`N <= M*L`, since every package is mentioned at least once in the entire
Contents indices file. Therefore, `O(M*L + N) = O(M*L)`.

We achieve this time complexity by refraining from sorting all packages based
on their respective associated filename counts. Instead, we apply a partial sort
via a heap by choosing only the top `K` packages.

If `K` is expected to be constant and `K << N`, e.g., `K = 10`, then the time
complexity of this tool is essentially `O(M * L)`.

### Space Complexity

`O(M * L)` space is required to store the compressed file in persistent storage
and the decompressed file in volatile memory. See the
[Time Complexity](#time-complexity) section for an explanation of the notation.

Note that `O(N)` space is also required to create and maintain a max-heap of
packages, as well as to produce the final output. However, as we illustrated in
the [Time Complexity](#time-complexity) section, `N <= M*L`, therefore the
`M*L` factor is the dominant one.

## Documentation

All APIs have been documented with docstrings. Please run
`pydoc3 package_statistics` to view the public API documentation for this tool.

## Development Tools

Development tools that were used for this assessment include:

- The [Pyink][pyink] auto-formatter.
- The [Pylint][pylint] static code analyzer.
- [Grip][grip] for instant view of markdown files on the local machine.

The external [Google Style Guide for Python][google-python] has been followed
in this assessment, so all tools have been tuned to enforce this style guide.

## Allocated Time

About 19.5 hours were allocated to this assessment in its entirety. This
allocated time was used to:

- Gather [requirements][requirements], reach out to the company for
  clarifications, and make assumptions.
- Conduct research on the style guide to follow and decide on the most suitable
  auto-formatter and the static code analyzer.
- Read and understand the [contents file format][contents] and design the
  core functionality of the tool.
- Implement the core functionality of the code.
- Refactor the code for readability across different classes and/or modules.
- Optimize the time complexity to find the top `K` packages.
- Set up the `unittest` framework, construct test data, and provide unit
  test(s).
- Provide documentation as module, function, or class docstrings.
- Write explanatory inline comments to illustrate the rationale behind the
  implementation decisions.
- Implement small features outside of the scope of the
  [original instructions](#original-instructions), e.g., allow users tune the
  `K` parameter.

[compensation]: docs/requirements.md#compensation
[contents]: https://wiki.debian.org/RepositoryFormat#A.22Contents.22_indices
[google-python]: https://google.github.io/styleguide/pyguide.html
[grip]: https://github.com/joeyespo/grip
[gzip]: https://docs.python.org/3/library/gzip.html
[heapq]: https://docs.python.org/3/library/heapq.html
[pyink]: https://github.com/google/pyink
[pylint]: https://pypi.org/project/pylint
[requests]: https://pypi.org/project/requests/
[requests-version]: https://github.com/psf/requests/releases/tag/v2.28.0
[requirements]: docs/requirements.md
