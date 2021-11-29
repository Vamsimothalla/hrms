from django.urls import path, reverse
from . import views
app_name = 'hrms'
urlpatterns = [

# Authentication Routes
    path('', views.Index.as_view(), name='index'),
    path('register/', views.Register.as_view(), name='reg'),
    path('login/', views.Login_View.as_view(), name='login'),
    path('login_emp/', views.Login_View_Emp.as_view(), name='login_emp'),
    path('logout/', views.Logout_View.as_view(), name='logout'),
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    path('dashboard_emp/', views.Dashboard_Emp.as_view(), name='dashboard_emp'),

    path('holidays', views.holidays_page, name="holidays_page"),
    path('delete_holiday/<int:holiday_id>/', views.delete_holiday, name="delete_holiday"),
    path('edit_holiday/<int:holiday_id>/', views.edit_holiday_page, name="edit_holiday_page"),

# Employee Routes
    path('dashboard/employee/', views.Employee_All.as_view(), name='employee_all'),
    path('dashboard/employee/new/', views.Employee_New.as_view(), name='employee_new'),
    path('dashboard/employee/<int:pk>/view/', views.Employee_View.as_view(), name='employee_view'),
    path('dashboard/employee/<int:pk>/update/', views.Employee_Update.as_view(), name='employee_update'),
    path('dashboard/employee/<int:pk>/delete/', views.Employee_Delete.as_view(), name='employee_delete'),

#Department Routes
    path('dashboard/department/<int:pk>/', views.Department_Detail.as_view(), name='dept_detail'),
    path('dashboard/department/add/', views.Department_New.as_view(), name='dept_new'),
    path('dashboard/department/<int:pk>/update/', views.Department_Update.as_view(), name='dept_update'),

#Attendance Routes
    path('dashboard/attendance/in/', views.Attendance_New.as_view(), name='attendance_new'),
    path('dashboard/attendance/<int:pk>/out/', views.Attendance_Out.as_view(), name='attendance_out'),

#Leave Routes
path('leave_application_details/<int:id>/', views.leave_application_details,
         name="leave_application_details"),
    path('apply_leave/', views.apply_leave, name="apply_leave"),
    path("dashboard/leave/new/", views.leave_dashboard_page, name="leave_new"),
    path('approve_leave/', views.approve_leave, name="approve_leave"),
    path('reject_leave/', views.reject_leave, name="reject_leave"),

#Recruitment

    path('manage_job_advertisement_page', views.manage_job_advertisement_page, name="manage_job_advertisement_page"),
    path('edit_job_advertisement_page/<int:job_advertisement_id>/', views.edit_job_advertisement_page,
         name="edit_job_advertisement_page"),
    path('delete_job_advertisement/<int:job_advertisement_id>/', views.delete_job_advertisement,
         name="delete_job_advertisement"),
    path('recruitment', views.job_advertisements_page, name="job_advertisements_page"),
    path('view_job_applications_page', views.view_job_applications_page, name="view_job_applications_page"),
    path('job_advertisement/<int:job_advertisement_id>/', views.job_advertisement, name="job_advertisement"),
    path('job_applications/<int:job_advertisement_id>/', views.job_applications_page, name="job_applications"),
    path("recruitment1/",views.RecruitmentNew.as_view(), name="recruitment"),
    path("recruitment/all/",views.RecruitmentAll.as_view(), name="recruitmentall"),
    path("recruitment/<int:pk>/delete/", views.RecruitmentDelete.as_view(), name="recruitmentdelete"),

#Payroll
    path("employee/pay/",views.Pay.as_view(), name="payroll")

]
def javascript_settings():
    js_conf = {
        'get_end_date': reverse('get_end_date'),
        'get_number_of_days_between_two_dates': reverse('get_number_of_days_between_two_dates'),
        'get_no_of_days': reverse('get_no_of_days'),
        'approve_leave': reverse('approve_leave'),
        'reject_leave': reverse('reject_leave'),
        'edit_leave_application': reverse('edit_leave_application'),
        'delete_leave_application': reverse('delete_leave_application'),
        'apply_leave_page': reverse('apply_leave_page'),
        'leave_dashboard_page': reverse('leave_dashboard_page'),
    }

    return js_conf