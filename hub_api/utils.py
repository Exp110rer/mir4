from django.core.mail import send_mail
from mirusers.models import MirUser


email_list_cs = [user.email for user in MirUser.objects.filter(groups__name='Orders_CS')]


def ihubzone_send_mail(instance, status):
    if status == 'validated':
        subject = f"Order # {instance.order} VALIDATED"
        message = f"Order # {instance.order} has been validated.\nStatus: {instance.status}"
    elif status == 'deleted':
        subject = f"Order # {instance.order} DELETED"
        message = f"Order # {instance.order} has been deleted."
    elif status == 'received':
        subject = f"Order # {instance['order']} RECEIVED"
        message = f"Order # {instance['order']} has been received."
    else:
        subject = 'Subject'
        message = 'Message'
    try:
        send_mail(subject, message, email_sender, email_list_cs)
    except Exception:
        pass

# def field_required_response(field_name):
#     response = {
#         field_name: [
#             "This field is required."
#         ]
#     }
#     return response
