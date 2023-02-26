import json


def field_required_response(field_name):
    response = {
        field_name: [
            "This field is required."
        ]
    }
    return response
