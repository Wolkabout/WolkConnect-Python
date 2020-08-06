Documentation
=============

Project documentation is built using [Sphinx docs](http://sphinx-doc.org/), which uses [ReST](http://docutils.sourceforge.net/rst.html) for markup.  This allows the docs to cover a vast amount of topics without using a thousand-line README file.

Sphinx docs is pip-installable via `pip install sphinx`.  Once installed, open a command line in the docs folder and run the following commands:

```console
pip install -r requirements.txt
```

This will install the requirements needed for the generating the docs. Afterwards you can run:

- Linux:
```console
make html
```
- Windows:
```console
sphinx-build -b html .\source\ .\build\
```


The docs will be generated, the output files will be placed in the `build/` directory, and can be browsed (locally) with any browser.
