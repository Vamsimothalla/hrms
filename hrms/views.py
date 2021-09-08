import datetime

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, resolve_url, render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import CreateView, View, DetailView, TemplateView, ListView, UpdateView, DeleteView

from .forms import RegistrationForm, LoginForm, EmployeeForm, DepartmentForm, AttendanceForm, LeaveForm, \
    RecruitmentForm, JobApplicationForm
from .models import Employee, Department, Attendance, Leave, Recruitment, create_holiday, get_all_holidays, get_holiday, \
    Holiday, JobAdvertisement, LeaveApplication
from .selector import get_job_advertisement
from .selector import get_job_applications
from .selector import get_all_job_ads, get_all_positions, get_position
from .selector import get_all_job_ads, get_all_positions, get_position


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
    redirect_authenticated_user = False

    def get_success_url(self):
        url = resolve_url('hrms:dashboard')
        return url


class Login_View_Emp(LoginView):
    model = get_user_model()
    form_class = LoginForm
    template_name = 'hrms/registrations/emp_login.html'
    redirect_authenticated_user = False

    def get_success_url(self):
        url = resolve_url('hrms:dashboard_emp')
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


class Dashboard_Emp(LoginRequiredMixin, ListView):
    template_name = 'hrms/dashboard/emp_index.html'
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


def get_current_year():
    return datetime.datetime.now().year


def get_leave_record(email, year):
    try:
        leave_record = LeaveApplication.objects.get(email=email, leave_year=year)
        return leave_record
    except Exception:
        return None


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


def manage_job_advertisement_page(request):
    if request.POST:
        position_id = request.POST.get('position_id')
        position = get_position(position_id)
        education = request.POST.get('education')
        vacancy = request.POST.get('vacancy')
        experience = request.POST.get('experience')
        description = request.POST.get('description')
        deadline = request.POST.get('deadline')

        JobAdvertisement.objects.create(
            position=position,
            education=education,
            vacancy=vacancy,
            experience=experience,
            description=description,
            deadline=deadline
        )

        messages.success(request, "Successfully created a job advertisement")

        return HttpResponseRedirect(reverse('hrms:manage_job_advertisement_page'))

    all_positions = get_all_positions()
    all_job_ads = get_all_job_ads()
    context = {
        "recruitment_page": "active",
        "positions": all_positions,
        "job_ads": all_job_ads,

    }
    return render(request, 'hrms/recruitment/manage_job_advertisement.html', context)


def edit_job_advertisement_page(request, job_advertisement_id):
    if request.POST:
        position_id = request.POST.get('position_id')
        position = get_position(position_id)
        education = request.POST.get('education')
        vacancy = request.POST.get('vacancy')
        experience = request.POST.get('experience')
        description = request.POST.get('description')
        deadline = request.POST.get('deadline')

        JobAdvertisement.objects.filter(id=job_advertisement_id).update(
            position=position,
            education=education,
            vacancy=vacancy,
            experience=experience,
            description=description,
            deadline=deadline
        )

        messages.success(request, "Successfully updated a job advertisement")
        return HttpResponseRedirect(reverse('hrms:manage_job_advertisement_page'))

    job_advertisement = get_job_advertisement(job_advertisement_id)
    all_positions = get_all_positions()
    all_job_ads = get_all_job_ads()
    context = {
        "recruitment_page": "active",
        "positions": all_positions,
        "job_ads": all_job_ads,
        "job_ad": job_advertisement,
    }
    return render(request, 'hrms/recruitment/edit_job_advertisement.html', context)


def delete_job_advertisement(request, job_advertisement_id):
    job_advertisement = get_job_advertisement(job_advertisement_id)
    job_advertisement.delete()
    messages.success(request, "Deleted the job advertisement")
    return HttpResponseRedirect(reverse('hrms:manage_job_advertisement_page'))


def job_advertisements_page(request):
    all_positions = get_all_positions()
    all_job_ads = get_all_job_ads()

    context = {
        "recruitment_page": "active",
        "positions": all_positions,
        "job_ads": all_job_ads,

    }

    return render(request, 'hrms/recruitment/advertised_jobs.html', context)


def view_job_applications_page(request):
    all_positions = get_all_positions()
    all_job_ads = get_all_job_ads()

    context = {
        "recruitment_page": "active",
        "positions": all_positions,
        "job_ads": all_job_ads,

    }

    return render(request, 'hrms/recruitment/view_job_applications.html', context)


def job_advertisement(request, job_advertisement_id):
    if request.POST:
        job_application_form = JobApplicationForm(request.POST, request.FILES)
        job_application = job_application_form.save(commit=False)
        job_application.job_ad = get_job_advertisement(job_advertisement_id)
        job_application.save()

        messages.success(request, "Successfully uploaded CV")
        return HttpResponseRedirect(reverse('hrms:job_advertisement', args=[job_advertisement_id]))

    job_advertisement = get_job_advertisement(job_advertisement_id)

    job_application_form = JobApplicationForm()
    context = {
        "recruitment_page": "active",
        "job_advertisement": job_advertisement,
        "job_application_form": job_application_form,

    }

    return render(request, 'hrms/recruitment/job_description.html', context)


def job_applications_page(request, job_advertisement_id):
    job_advertisement = get_job_advertisement(job_advertisement_id)
    job_applications = get_job_applications(job_advertisement)

    context = {
        "recruitment_page": "active",
        "job_applications": job_applications,
        "job_advertisement": job_advertisement
    }
    return render(request, 'hrms/recruitment/job_applications.html', context)


def leave_dashboard_page(request):
    is_applications_available = False

    if True:
        hr_applications = LeaveApplication.objects \
            .filter(hr_status="Pending").order_by('apply_date')
        role = "is_hr"
        if hr_applications:
            is_applications_available = True

    context = {
        "leave_dashboard_page": "active",
        "hr_applications": hr_applications,
        "is_applications_available": is_applications_available,
        "role": role
    }
    return render(request, 'hrms/leave/leave_dashboard.html', context)


def apply_leave(request):
    if request.method == "POST":
        user = request.user
        start_date = request.POST["s_date"]
        end_date = request.POST["e_date"]
        days_applied = int(request.POST["no_days"])
        leave_application = LeaveApplication(
            name=user.first_name,
            email=user.email,
            start_date=start_date,
            end_date=end_date,
            no_of_days=days_applied,
        )
        leave_application.save()

    return render(request, "hrms/leave/leave.html")


def leave_application_details(request, id):
    leave_application = LeaveApplication.objects.get(id=id)

    context = {
        "leave_application": leave_application,
        "role": "is_hr"
    }

    return render(request, "hrms/leave/leave_applications.html", context)


def approve_leave(request):
    if request.method == "POST":
        user = request.user
        application_id = request.POST.get("application_id")
        leave_application = LeaveApplication.objects.get(pk=application_id)
        leave_application.hr_status = "Approved"
        leave_application.hr_comment = request.POST.get("comment")

        leave_application.save()
        messages.success(request, 'Leave Approved Successfully')
        return JsonResponse({'success': True, 'redirect': "leave_dashboard_page"})


def reject_leave(request):
    if request.method == "POST":
        application_id = request.POST.get("application_id")
        comment = request.POST.get("comment")
        leave_application = LeaveApplication.objects.get(pk=application_id)
        leave_application.hr_status = "Rejected"
        leave_application.hr_comment = comment
        leave_application.save()
        messages.success(request, 'Leave request rejected Successfully')
        return JsonResponse({'success': True, 'redirect': "leave_dashboard_page"})
