from .models import Department, LeaveApplication


def get_departments(request):
    depts = Department.objects.all().order_by('name')
    return {'depts': depts}
def get_leaves(request):
    try:
        leaves=LeaveApplication.objects.filter(email=request.user.email)
        return {"apps":leaves}
    except Exception:
        return {}