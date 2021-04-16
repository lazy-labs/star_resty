# Star resty
Object-oriented rest framework based on starlette, marshmallow and apispec.

## Requirements

* [Python] 3.7+
* [Starlette] 0.12.0+
* [Marshmallow] 3.0.0rc8+
* [APISpec] 2.0.2+
* [python-multipart] 0.0.5+

## Installation

```console
$ pip install star_resty
```

## Example

```python
from marshmallow import Schema, fields, ValidationError, post_load
from starlette.applications import Starlette
from starlette.datastructures import UploadFile
from starlette.responses import JSONResponse
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec import APISpec

from dataclasses import dataclass
from datetime import datetime

from star_resty import Method, Operation, endpoint, json_schema, json_payload, upload, query, setup_spec, form_payload
from typing import Optional

class EchoInput(Schema):
    a = fields.Int()


# Json Payload (by schema)
class JsonPayloadSchema(Schema):
    a = fields.Int(required=True)
    s = fields.String()

ma_plugin = MarshmallowPlugin()

# Json Payload (by dataclass)
@dataclass
class Payload:
    a: int
    s: Optional[str] = None

class JsonPayloadDataclass(Schema):
    a=fields.Int(required=True)
    s=fields.Str()

    @post_load
    def create_payload(self, data, **kwargs):
        return Payload(**data)


# Form Payload
class FormPayload(Schema):
    id = fields.Int(required=True)
    file_dt = fields.DateTime()


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


@app.route('/post/schema', methods=['POST'])
@endpoint
class PostSchema(Method):
    meta = Operation(tag='default', description='post json (by schema)')

    async def execute(self, item: json_payload(JsonPayloadSchema)):
        return {'a': item.get('a') * 2, 's': item.get('s')}


@app.route('/post/dataclass', methods=['POST'])
@endpoint
class PostDataclass(Method):
    meta = Operation(tag='default', description='post json (by dataclass)')

    async def execute(self, item: json_schema(JsonPayloadDataclass, Payload)):
        return {'a': item.a * 3, 's': item.s}

@app.route('/form', methods=['POST'])
@endpoint
class PostForm(Method):
    meta = Operation(tag='default', description='post form')

    async def execute(self, form_data: form_payload(FormPayload),
                            files_reqired: upload('selfie', 'doc', required=True),
                            files_optional: upload('file1', 'file2', 'file3')):
        files = {}
        for file in files_reqired + files_optional:
            body = await file.read()
            files[file.filename] = f"{body.hex()[:10]}..."
        id = form_data.get('id')
        return {'message': f"files received (id: {id})", "files": files}


if __name__ == '__main__':
    import uvicorn

    setup_spec(app, title='Example')
    uvicorn.run(app, port=8080)
```

Open [http://localhost:8080/apidocs](http://localhost:8080/apidocs) to view generated openapi schema.