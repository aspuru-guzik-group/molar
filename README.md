![test](https://gitlab.com/tgaudin/goldmine/badges/master/pipeline.svg) ![coverage](https://gitlab.com/tgaudin/goldmine/badges/master/coverage.svg)

# Madness DB

Install the doc:

```bash
$ pip install -e .[doc] # Install the extra deps
$ cd docs
$ make html
$ open _build/html/index.html
```

or alternatively, the doc is also hosted on the workstation:

```
ssh -L 5000:localhost:80 -2 -N  aagdbvis@thedb
```

then go to http://localhost:5000/
