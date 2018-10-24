import logging
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from requests.forms import ScanCardValidationForm
from requests.models import Student, NFCCard

# Get an instance of a logger
logger = logging.getLogger(__name__)

def homePageView(request):
    return HttpResponse('Hello World!')

@csrf_exempt
def cardScanView(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    # Create a form to validate incoming data.
    # This will check key names, key types, value types.
    post_data_form = ScanCardValidationForm(request.POST)
    if post_data_form.is_valid():
        student = Student.objects.filter(nfccard__card_id=request.POST['card_id']).first()
        if student is None:
            return HttpResponse('No student found!')

        # We only expect one result due to DB one to one relationship.
        return HttpResponse(f'Student found! The name is {student.first_name} {student.second_name}')
    else:
        # 400 indicates incorrect syntax
        logger.error(f"POST data incorrect: {post_data_form.errors}")
        return HttpResponse(status=400)