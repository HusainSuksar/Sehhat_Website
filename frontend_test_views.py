# Frontend Test Views
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def frontend_test(request):
    """Frontend functionality test page"""
    return render(request, 'frontend_test.html')

@csrf_exempt
def test_ajax_endpoint(request):
    """Test AJAX endpoint for error handling testing"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Simulate different responses based on test type
            test_type = data.get('type', 'success')
            
            if test_type == 'success':
                return JsonResponse({
                    'status': 'success',
                    'message': 'AJAX request successful!',
                    'data': data
                })
            elif test_type == 'error':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Simulated error occurred',
                    'errors': {
                        'field1': ['This field has an error'],
                        'field2': ['Another field error']
                    }
                }, status=400)
            elif test_type == 'validation':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Validation failed',
                    'errors': {
                        'name': ['Name is required'],
                        'email': ['Invalid email format']
                    }
                }, status=422)
            else:
                return JsonResponse({
                    'status': 'info',
                    'message': 'Test completed successfully',
                    'description': 'This is a test response'
                })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405)