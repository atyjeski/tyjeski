from django.http import JsonResponse, HttpResponse


def landing_page(request):
    html = "<html><body>You have reached the tyjeski.com landing page</body></html>"
    return HttpResponse(html)

def api_landing_page(request):
    html = "<html><body>This is the tyjeski.com API</body></html>"
    return HttpResponse(html)

def login(request):
    data = {'ping': 'pong!'}
    return JsonResponse(data)