import json

from django.template import Context, Template


class PermTracerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        user = request.user
        user._perm_trace = []

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        omit_paths = ['files', 'captcha', 'themes']
        modify_content = not any([request.path.startswith('/' + path) for path in omit_paths])
        if modify_content and hasattr(user, '_perm_trace') and len(user._perm_trace):
            response.content = response.content.replace(b'</body>', self.render_trace(user._perm_trace) + b'</body>')

        return response

    def render_trace(self, perm_trace):
        template = Template('<script type="text/javascript">console.info("%cPermissions Inspected", "color:Orchid; font-weight:bold; font-size:24px;"); console.table({{ perm_trace | safe }});</script>')
        context = Context(dict(perm_trace=json.dumps(perm_trace)))
        return bytes(template.render(context), 'utf8')
