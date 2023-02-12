from django import forms
from mirusers.models import MirUser
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, ReadOnlyPasswordHashField, UsernameField
from django.utils.translation import gettext_lazy as _


class MirUserCreationForm(UserCreationForm):
    class Meta:
        model = MirUser
        fields = ('hub',)


# class MirUserChangeForm(UserChangeForm):
#     class Meta:
#         model = MirUser
#         fields = ('hub',)


class MirUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            "Raw passwords are not stored, so there is no way to see this "
            "user’s password, but you can change the password using "
            '<a href="{}">this form</a>.'
        ),
    )

    class Meta:
        model = MirUser
        fields = "__all__"
        # field_classes = {"username": UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        password = self.fields.get("password")
        if password:
            password.help_text = password.help_text.format("../password/")
        user_permissions = self.fields.get("user_permissions")
        if user_permissions:
            user_permissions.queryset = user_permissions.queryset.select_related(
                "content_type"
            )
