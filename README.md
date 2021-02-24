# Star resty
Object-oriented rest framework based on starlette, marshmallow and apispec.

## Requirements

* [Python] 3.7+
* [Starlette] 0.12.0+
* [Marshmallow] 3.0.0rc8+
* [APISpec] 2.0.2+

## Installation

```console
$ pip install star_resty
```

## Example

```python
from dataclasses import dataclass
from typing import Optional

from marshmallow import Schema, fields, post_load, ValidationError
from starlette.applications import Starlette
from starlette.responses import JSONResponse

from star_resty import Method, Operation, endpoint, json_schema, query, setup_spec


class EchoInput(Schema):
    a = fields.Int()


@dataclass
class Payload:
    a: int
    s: Optional[str] = None


class PayloadSchema(Schema):
    a = fields.Int(required=True)
    s = fields.String()

    @post_load
    def create_payload(self, data, **kwargs):
        return Payload(**data)


app = Starlette(debug=True)

@app.exception_handler(ValidationError)
def register_error(request, e: ValidationError):
    return JSONResponse(e.normalized_messages(), status_code=400)


@app.route('/echo')
@endpoint
class Echo(Method):
    meta = Operation(tag='default',
                     description='echo')
    response_schema = EchoInput
    async def execute(self, query_params: query(EchoInput)):
        self.status_code = 201  # Configurable Respone Http Status Code
        return query_params


@app.route('/post', methods=['POST'])
@endpoint
class Post(Method):
    meta = Operation(tag='default', description='post')

    async def execute(self, item: json_schema(PayloadSchema, Payload)):
        return {'a': item.a * 2, 's': item.s}


if __name__ == '__main__':
    import uvicorn

    setup_spec(app, title='Example')
    uvicorn.run(app, port=8080)
```

Open [http://localhost:8080/apidocs.json](http://localhost:8080/apidocs.json) to view generated openapi schema.
