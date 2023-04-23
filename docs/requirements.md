# Requirements Elicitation

Prior to designing and implementing this assessment, we researched the
requirements of the system, the stakeholders, and any potential users. After
conducting an initial requirements gathering round, we sent an e-mail to the
point of contact (POC) of the company, on the same day when we received the
instructions for this assessment.

Nevertheless, we received no response within 14 days of sending the initial
e-mail. Therefore, we took reasonable assumptions for each requirement in order
to implement this assessment.

Below are the different areas where we gathered requirements.

## Target Audience

Question: _What is the target audience of this tool, if any? Examples include: a
single external user; a software developer; a team of developers; an entire
company._

Assumption: a single internal user who is already acquainted with the assessment
instructions and requirements.

## Environment

Question: _Will the produced python script be executed from a Linux
environment?_

Assumption: yes, the script will be executed from a Linux environment.

## Permissions

Question: _Will there be adequate permissions to download remote files from URLs
and store them on the local and/or `/tmp` directory, as dictated by the exercise
requirements?_

Assumption: yes, any requirement permissions are assumed to have been granted.

## Imports

Question: _Will any required python packages such as `gzip` or `requests` be
available?_

Assumption: any packages from the standard python library are assumed to be
available.

## Error Handling

Question: _What level of error handling is expected? Examples include: network
partitioning, corrupt files, invalid command line arguments, missing
dependencies._

Assumption: the respective packages will raise the respective exceptions, but we
will not explicitly handle them. For example, [`requests.get`][requests] will
raise a `ConnectionError` exception in case of network partition.

We explicitly handle two use cases:

- No architecture positional argument is given when executing the script.
- An architecture argument is given, but represents an invalid architecture.

## Unit Testing

Question: _What level of unit testing is expected?_

Assumption: we will provide one simple unit test to validate the
proof-of-concept. Due to the simplicity of this assessment, we will not provide
more elaborate test cases.

## Constraints

Question: _What are the performance objectives and constraints, if any? Is it
sufficient to produce a single-threaded script? Is the use of Map-Reduce
frameworks, e.g., `PySpark`, outside of the scope of this assessment? Likewise,
can we assume that a single, decompressed `Contents` file, which is typically
less than `1 MB`, can fit into the memory?_

Assumption: no special performance or memory objectives or constraints are
assumed. The decompressed files are expected to fit into memory due to their
small size. Furthermore, we consider a single-threaded application to be
sufficient for the purposes of this assessment.

## Scaling Considerations

Question: _Are there any specific scaling requirements?_

Assumption: there are no special scaling considerations.

## Data Cleanup

Question: _After the tool has been executed, should the downloaded files be
deleted from persistent storage?_

Assumption: it is not required to delete the downloaded files from persistent
storage.

## Caching

Question: _In case of multiple or repeated executions of this tool: is caching
of previous executions within the scope of this assessment? Are repeated
executions of the same command & architecture being evaluated? Example: a user
runs twice `./package_statistics amd64` within 20 seconds._

Assumption: we provide a very simple caching optimization. Since the compressed
downloaded files are kept into persistent storage, we first verify if the
required `Contents-{architecture}.gz` file has already been downloaded, before
attempting to download it from the remote mirror.

## Security Considerations

Question: _Are there any security considerations, e.g., rate limiting when the
tool is executed multiple times?_

Assumption: there are no special security or privacy considerations.

## Documentation

Question: _What level of documentation is expected?_

Assumption: we provide:

- A [`README`][readme] file with the assessment instructions.
- Docstrings for every public and protected/private API.
- Inline comments explaining the rationale behind non-trivial implementation
  decisions.

## Allocated Time

Question: _How many hours are expected to be invested on this assessment and
when is the deadline for submitting it?_

Assumption: since no response was received within 14 days of sending the initial
e-mail, we do not assume any strict requirements, but make a reasonable time
investment so that the assessment is completed in a relatively short time, but
also illustrate our work around various concepts, such as design,
implementation, testing, and documentation.

We document the allocated time in the [`README`][readme] file.

## Compensation

Question: _How will this assessment be compensated?_

Assumption: since no response was received within 14 days of sending the initial
e-mail, this assessment is assumed to be unpaid and, therefore, implemented on a
voluntary basis. Since no Non-disclosure agreement (NDA) had been signed prior
to commencing this assessment, there are not any legal requirements or
constraints for neither the interviewer nor the interviewee.

[readme]: ../README.md
[requests]: https://pypi.org/project/requests/
