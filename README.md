# STAPI FastAPI - Sensor Tasking API with FastAPI: TLE Provider Example

NOTE: This repository uses [scripts to rule them all](https://github.com/github/scripts-to-rule-them-all)

This repository shows a different approach to provide a STAPI provider
implementation: router subclassing instead of backend protocol. This provides
two advantages over the hitherto solution:

1. standard FastAPI style dependency injection in the router endpoints parameter
   declaration. Use this to add your implementation specific dependencies like
   JWT authentication, database client or like in this example actual TLE
   defined satellite model. Then use FastAPI dependency overrides in testing as
   well for example.
2. ability to provide fully OpenAPI type documented endpoints. It's a little bit
   on the expressive side (see
   [product.py](./stapi_fastapi_tle/service/product.py)), but remember
   [PEP20][https://peps.python.org/pep-0020/]! Plus it's opt-in (but maybe
   shouldn't?).

If this approach finds support, some refactoring in the stapi_fastapi project
should be done:

1. Remove backend protocol stuff.
2. Move model mixins from here to stapi_fastapi.
3. Add documentation around how to add a provider implementation (proposal:
   mkdocs contained in the repo, hosted on github?).

## Usage

### Dev Setup

Setup is managed with `poetry` and `pre-commit`, all of which can be initialised
by `./scripts/bootstrap`.

### Test Suite

A `pytest` based test suite is provided. Run it as `./scripts/test`. Any
additional pytest flags are passed along

### Dev Server

For dev purposes,
[stapi_fastapi_tle.\_\_main\_\_.py](./stapi_fastapi_tle/__mains__.py) shows a
minimal demo with `uvicorn` to run the full app. Start it with
`./scripts/server`.

A mock TLE is provided as default, but can be overriden using the `TLE_SRC` env
var.

Try getting opportunities over null island for the next week with
[httpie][httpie]:

```bash
http -v POST localhost:8000/opportunities \
  product_id=basic_tle \
  datetime=$(TZ=Zulu date -Iseconds)/$(TZ=Zulu date -Iseconds -v+1w) \
  "geometry[type]"=Point \
  "geometry[coordinates]":='[0,0]'
```

[httpie]: https://httpie.io
