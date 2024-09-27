# STAPI FastAPI - Sensor Tasking API with FastAPI: TLE Provider Example

NOTE: This repository uses [scripts to rule them all](https://github.com/github/scripts-to-rule-them-all)

## Usage

### Dev Setup

Setup is managed with `poetry` and `pre-commit`, all of which can be initialised
by `./scripts/bootstrap`.

### Test Suite

A `pytest` based test suite is provided. Run it as `./scripts/test`. Any additional
pytest flags are passed along

### Dev Server

For dev purposes, [stapi_fastapi_tle.\_\_main\_\_.py](./stapi_fastapi_tle/__mains__.py)
shows a minimal demo with `uvicorn` to run the full app. Start it with
`./scripts/server`.

A mock TLE is provided as default, but can be overriden using the `TLE_SRC` env var.

Try getting opportunities over null island for the next week with [httpie][httpie]:

```bash
http -v POST localhost:8000/opportunities \
  product_id=basic_tle \
  datetime=$(TZ=Zulu date -Iseconds)/$(TZ=Zulu date -Iseconds -v+1w) \
  "geometry[type]"=Point \
  "geometry[coordinates]":='[0,0]'
```

[httpie]: https://httpie.io
