Contributing
============

When contributing to this repository, please first discuss the change you wish
to make via issue, email, or any other method with the owners of this repository
before making a change.

Code Style
----------
For manual formatting, please adhere to the following guidelines.
1. Use a style conformant to PEP8 with the following exceptions.
2. Add 3 lines of whitespace between classes and free functions.
3. Prefer 2 lines of whitespace between methods within classes.
4. Prefer all methods in classes should have an explicit `return` statement.
5. All `pytest` tests shoud `return 0` if the test is successful.
6. Conform to Google-style docstrings except for where it might break Sphinx
   formatting.
7. PEP8 line length limitations are a bit too tight and can cause code to be
   harder to read than it should be due to unnecessary breaks. Given the prevalance
   of wide-format displays it's reasonable to extend this lenghth. Lines should not 
   exceed 120 columns except in cases where it really is needed for readability.

### Automatic formatting
We also use the [YAPF][2] tool to perform auto-formatting.
The [.style.yapf](.style.yapf) file provides the rules for the formatting scheme we use.
This formatter will override some of the settings listed above and is preferred.

Versioning
----------
This project uses [Semantic Versioning][1].

Merge Request Process
---------------------
1. Ensure any unapproved install or build dependencies are removed before submitting
   a merge request.
2. Update the CHANGELOG.md file with details of the changes you are making.
3. Update relevant documentation in the `doc/` folder and any appropriate _docstrings_.
4. Update unit tests to fully test your additions. We aim for 100% coverage on this project.
5. Ensure unit tests and documentation build cleanly by running `exec-tests.sh`, `exec-makedoc.sh`
   and the _example_ applications in the repository.

Code of Conduct
===============
In the interest of fostering an open and welcoming environment, we as contributors
and maintainers pledge to making participation in our project and our community a
harassment-free experience for everyone, regardless of age, body size, disability,
ethnicity, gender identity and expression, level of experience, nationality,
personal appearance, race, religion, or sexual identity and orientation.

Standards
---------
Examples of behavior that contributes to creating a positive environment include:
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

Examples of unacceptable behavior by participants include:
- The use of sexualized language or imagery and unwelcome sexual attention
  or advances
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information, such as a physical or electronic
  address, without explicit permission
- Other conduct which could reasonably be considered inappropriate in a
  professional setting

[1]: http://semver.org/
[2]: https://github.com/google/yapf
