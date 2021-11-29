from hrms.models import JobAdvertisement, JobApplication,Department


def get_all_job_ads():
    return JobAdvertisement.objects.all()


def get_job_advertisement(job_advertisement_id):
    return JobAdvertisement.objects.get(pk=job_advertisement_id)


def get_job_applications(job_advertisement):
    job_applications = JobApplication.objects.filter(job_ad=job_advertisement)
    return job_applications

def get_all_positions():
    return Department.objects.all()


def get_position(position_id):
    return Department.objects.get(pk=position_id)