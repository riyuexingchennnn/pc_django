from datetime import datetime
from apps.pay.models import ContinueTime


def is_overdue(user_id):
    """
    判断现在会员是否过期
    True为过期
    False为没过期,并返回剩余天数
    """

    now = datetime.now()
    record = ContinueTime.objects.get(user_id=user_id)
    if record.deadline > now:
        return True
    else:
        leave_day = now - record.deadline
        return False, leave_day.days
