from django.conf import settings
from django.contrib.auth.models import User
import crypt

class HtPasswdBackend:
    def authenticate(self, username=None, password=None):
        f = open(settings.HTPASSWD)
        for line in f:
            name,pw = line.split(':')

            if name != username:
                continue

            pw = pw.rstrip('\n')
            if crypt.crypt(password, pw) != pw:
                return None
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = User(username=username, password='specified in htpasswd')
                user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
