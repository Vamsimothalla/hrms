from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, resolve_url, render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import CreateView, View, DetailView, TemplateView, ListView, UpdateView, DeleteView

from .forms import RegistrationForm, LoginForm, EmployeeForm, DepartmentForm, AttendanceForm, LeaveForm, \
    RecruitmentForm
from .models import Employee, Department, Attendance, Leave, Recruitment, create_holiday, get_all_holidays, get_holiday, \
    Holiday


# Create your views here.
class Index(TemplateView):
    template_name = 'hrms/home/home.html'


#   Authentication
class Register(CreateView):
    model = get_user_model()
    form_class = RegistrationForm
    template_name = 'hrms/registrations/register.html'
    success_url = reverse_lazy('hrms:login')


class Login_View(LoginView):
    model = get_user_model()
    form_class = LoginForm
    template_name = 'hrms/registrations/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        url = resolve_url('hrms:dashboard')
        return url


class Logout_View(View):

    def get(self, request):
        logout(self.request)
        return redirect('hrms:login', permanent=True)


# Main Board
class Dashboard(LoginRequiredMixin, ListView):
    template_name = 'hrms/dashboard/index.html'
    login_url = 'hrms:login'
    model = get_user_model()
    context_object_name = 'qset'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['emp_total'] = Employee.objects.all().count()
        context['dept_total'] = Department.objects.all().count()
        context['admin_count'] = get_user_model().objects.all().count()
        context['workers'] = Employee.objects.order_by('-id')
        return context


# Employee's Controller
class Employee_New(LoginRequiredMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'hrms/employee/create.html'
    login_url = 'hrms:login'
    redirect_field_name = 'redirect:'


class Employee_All(LoginRequiredMixin, ListView):
    template_name = 'hrms/employee/index.html'
    model = Employee
    login_url = 'hrms:login'
    context_object_name = 'employees'
    paginate_by = 5


class Employee_View(LoginRequiredMixin, DetailView):
    queryset = Employee.objects.select_related('department')
    template_name = 'hrms/employee/single.html'
    context_object_name = 'employee'
    login_url = 'hrms:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            return context
        except ObjectDoesNotExist:
            return context


class Employee_Update(LoginRequiredMixin, UpdateView):
    model = Employee
    template_name = 'hrms/employee/edit.html'
    form_class = EmployeeForm
    login_url = 'hrms:login'


class Employee_Delete(LoginRequiredMixin, DeleteView):
    pass


# Department views

class Department_Detail(LoginRequiredMixin, ListView):
    context_object_name = 'employees'
    template_name = 'hrms/department/single.html'
    login_url = 'hrms:login'

    def get_queryset(self):
        queryset = Employee.objects.filter(department=self.kwargs['pk'])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dept"] = Department.objects.get(pk=self.kwargs['pk'])
        return context


class Department_New(LoginRequiredMixin, CreateView):
    model = Department
    template_name = 'hrms/department/create.html'
    form_class = DepartmentForm
    login_url = 'hrms:login'


class Department_Update(LoginRequiredMixin, UpdateView):
    model = Department
    template_name = 'hrms/department/edit.html'
    form_class = DepartmentForm
    login_url = 'hrms:login'
    success_url = reverse_lazy('hrms:dashboard')


# Attendance View

class Attendance_New(LoginRequiredMixin, CreateView):
    model = Attendance
    form_class = AttendanceForm
    login_url = 'hrms:login'
    template_name = 'hrms/attendance/create.html'
    success_url = reverse_lazy('hrms:attendance_new')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["today"] = timezone.localdate()
        pstaff = Attendance.objects.filter(Q(status='PRESENT') & Q(date=timezone.localdate()))
        context['present_staffers'] = pstaff
        return context


class Attendance_Out(LoginRequiredMixin, View):
    login_url = 'hrms:login'

    def get(self, request, *args, **kwargs):
        user = Attendance.objects.get(
            Q(staff__id=self.kwargs['pk']) & Q(status='PRESENT') & Q(date=timezone.localdate()))
        user.last_out = timezone.localtime()
        user.save()
        return redirect('hrms:attendance_new')


class LeaveNew(LoginRequiredMixin, CreateView, ListView):
    model = Leave
    template_name = 'hrms/leave/create.html'
    form_class = LeaveForm
    login_url = 'hrms:login'
    success_url = reverse_lazy('hrms:leave_new')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["leaves"] = Leave.objects.all()
        return context


class Payroll(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'hrms/payroll/index.html'
    login_url = 'hrms:login'
    context_object_name = 'stfpay'


class RecruitmentNew(CreateView):
    model = Recruitment
    template_name = 'hrms/recruitment/index.html'
    form_class = RecruitmentForm
    success_url = reverse_lazy('hrms:recruitment')


class RecruitmentAll(LoginRequiredMixin, ListView):
    model = Recruitment
    login_url = 'hrms:login'
    template_name = 'hrms/recruitment/all.html'
    context_object_name = 'recruit'


class RecruitmentDelete(LoginRequiredMixin, View):
    login_url = 'hrms:login'

    def get(self, request, pk):
        form_app = Recruitment.objects.get(pk=pk)
        form_app.delete()
        return redirect('hrms:recruitmentall', permanent=True)


class Pay(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'hrms/payroll/index.html'
    context_object_name = 'emps'
    login_url = 'hrms:login'


def holidays_page(request):
    if request.POST:
        date = request.POST.get('date')
        name = request.POST.get('name')
        holiday = create_holiday(date, name)
        messages.success(request, "Successfully created the holiday")
        return HttpResponseRedirect(reverse('hrms:holidays_page'))

    holidays = get_all_holidays()
    context = {
        "holidays_page": "active",
        "holidays": holidays
    }

    return render(request, 'hrms/holiday/holidays_page.html', context)


def delete_holiday(request, holiday_id):
    holiday = get_holiday(holiday_id)
    holiday.delete()
    messages.success(request, "Deleted a holiday entry")
    return HttpResponseRedirect(reverse('hrms:holidays_page'))


def edit_holiday_page(request, holiday_id):
    holiday = get_holiday(holiday_id)
    if request.POST:
        date = request.POST.get('date')
        name = request.POST.get('name')
        Holiday.objects.filter(id=holiday.id).update(
            name=name,
            date=date
        )
        messages.success(request, "Updated the holiday entry")
        return HttpResponseRedirect(reverse('hrms:holidays_page'))
    context = {
        "holidays_page": "active",
        "holiday": holiday
    }
    return render(request, 'hrms/holiday/edit_holiday.html', context)
