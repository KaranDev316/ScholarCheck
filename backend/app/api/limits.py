"""Bound report request bytes before JSON parsing, including chunked requests."""
from starlette.responses import JSONResponse


class ReportBodyLimit:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http' or scope.get('method') != 'POST' or not scope.get('path','').endswith('/reports'):
            return await self.app(scope, receive, send)
        messages = []
        size = 0
        while True:
            message = await receive()
            if message['type'] == 'http.disconnect':
                return
            size += len(message.get('body', b''))
            if size > 8192:
                response = JSONResponse({'code':'invalid_request','message':'Report is too large.'},status_code=413)
                return await response(scope, receive, send)
            messages.append(message)
            if not message.get('more_body',False):
                break
        async def replay():
            if messages:
                return messages.pop(0)
            return await receive()
        await self.app(scope,replay,send)
