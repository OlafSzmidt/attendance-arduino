from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

def homePageView(request):
    return HttpResponse('Hello World!')

@csrf_exempt
def cardScanView(request):
    if request.method != 'POST':
        return HttpResponse(status=405)
    return HttpResponse('Card has been scanned!')