import foosbot.database as database
from django.contrib.auth.models import User


class ClientAuth:
    def authenticate(self, request, account_id=None, token=None):
        db = database.builder('foosbot')
        client = db.table('clients').where('account_id', account_id).where('token', 'token').first()
        if client:
            try:
                user = User.objects.get(pk=account_id)
            except User.DoesNotExist:
                # Create a new user. There's no need to set a password
                # because only the password from settings.py is checked.
                user = User(pk=account_id, username=str(account_id))
                user.is_staff = False
                user.is_superuser = False
                user.save()
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
