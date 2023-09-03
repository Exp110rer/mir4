from django.core.mail import send_mail, send_mass_mail
from mirusers.models import MirUser
from hub_api.models import Order

email_sender = 'informer@ihubzone.ru'


def ihubzone_send_mail(instance, status):
    email_list_cs = [user.email for user in MirUser.objects.filter(groups__name='Orders_CS')]
    emails = list()
    base_subject = f"{instance.order} # {instance.hub.erpname} {instance.productCategory} {instance.buyoutDate}"
    message = f"Order #                    {instance.order}\nHUB                          {instance.hub.erpname}\nProduct Category   {instance.productCategory}\nDelivery date          {instance.buyoutDate}\nOwner                      {instance.saleType}\nCreated                    {instance.created}"
    for item in email_list_cs:
        if status == 'validated':
            subject = f" {base_subject} VALIDATED"
        elif status == 'deleted':
            subject = f" {base_subject} DELETED"
        elif status == 'received':
            subject = f" {base_subject} RECEIVED"
        elif status == 'validated_warning':
            subject == f"{base_subject} WARNING VALIDATED"
        else:
            subject = 'Subject'
            message = 'Message'
        emails.append((subject, message, email_sender, (item,)))
    try:
        send_mass_mail(tuple(emails))
    except Exception as Exp:
        pass

# def field_required_response(field_name):
#     response = {
#         field_name: [
#             "This field is required."
#         ]
#     }
#     return response
