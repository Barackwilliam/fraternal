"""
noindex kwa kurasa ambazo Google inaruhusiwa kuzisoma lakini zisiorodheshwe.

Njia sahihi ya kuondoa ukurasa kwenye Google ni kuuruhusu kwenye robots.txt
na kutuma noindex — si kuuzuia (Google haioni noindex ya ukurasa uliozuiwa).
"""

NOINDEX_PREFIXES = ('/portal/',)


class NoIndexMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith(NOINDEX_PREFIXES) and 'X-Robots-Tag' not in response:
            response['X-Robots-Tag'] = 'noindex, follow'
        return response
