import foosbot.database as database
from django.contrib.auth.models import User


class ClientAuth:
    def authenticate(self, request, client_id=None, token=None):
        db = database.builder('foosbot')
        client = db.table('clients').where('client_id', client_id).where('token', 'token').first()
        if client:
            try:
                user = User.objects.get(pk=client_id)
            except User.DoesNotExist:
                # Create a new user. There's no need to set a password
                # because only the password from settings.py is checked.
                user = User(pk=client_id, username=str(client_id))
                user.is_staff = False
                user.is_superuser = False
                user.save()
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
