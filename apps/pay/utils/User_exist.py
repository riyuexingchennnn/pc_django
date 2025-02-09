from apps.accounts.models import User


def user_is_exist(user_id):
    users = User.objects.filter(id=user_id)
    if len(users) == 0:
        return False
    else:
        return True
