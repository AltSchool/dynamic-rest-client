We encourage bug reports, suggestions for improvements, and direct contributions through Github Issues/Pull Requests.

When making contributions, try to follow these guidelines:

# Development

## Style

Use `make lint` to check your code for style violations.

We use the `flake8` linter to enforce PEP8 code style. 
For additional details, see our [Python style guide](https://github.com/AltSchool/Python).

## Tests

Use `make test` to lint and run all unit tests (runs in a few seconds).
Run `tox` to run tests against Python 2.7 and Python 3.6

We recommend linting regularly, testing with every commit, and running tests against all combinations before submitting a pull request.

# Submission

Please submit your pull request with a clear title and description.
Any visual changes (e.g. to the Browsable API) should include screenshots in the description.
Any related issues in Dynamic REST, Django REST Framework, or Django should include a URL reference to the issue.

# Publishing

(PyPi and repository write access required)
Make sure you have a `~/.pypirc` file that contains the following:
```
[distutils]
index-servers =
  pypi
  pypitest

[pypi]
repository=https://upload.pypi.org/legacy/

[pypitest]
repository=https://test.pypi.org/legacy/
```

Before releasing:

- Check/update the version in `dynamic_rest/constants.py`
- Commit changes and tag the commit with the version, prefixed by "v"
- Run `make pypi_upload_test` to upload a new version to PyPiTest. Check the contents at https://test.pypi.org/project/dynamic-rest-client
- Run `make pypi_upload` to upload a new version to PyPi. Check the contents at https://pypi.python.org/pypi/dynamic-rest-client
