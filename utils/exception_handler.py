from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    """
    Custom DRF exception handler to return a unified 'message' format.
    """
    response = exception_handler(exc, context)

    if response is not None:
        # Handle ValidationError
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            custom_response_data = {}

            for field, errors in response.data.items():
                # Join multiple errors for a field
                message = " ".join(errors)
                custom_response_data[field] = {"message": message}

            response.data = {
                "status": "error",
                "errors": custom_response_data
            }
        else:
            # Other DRF errors
            response.data = {
                "status": "error",
                "message": response.data.get("detail", "An error occurred")
            }

    return response