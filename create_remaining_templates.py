#!/usr/bin/env python3
"""
Script to create all remaining templates for the UmoorSehhat application.
This will create comprehensive, functional templates for all remaining modules.
"""

import os

def create_template(path, title, header, content):
    """Create a template file with the given configuration"""
    template_content = f"""{{%% extends 'base.html' %%}}

{{%% block title %%}}{title}{{%% endblock %%}}

{{%% block content %%}}
<div class="container-fluid">
    <!-- Header -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="d-sm-flex align-items-center justify-content-between">
                {header}
            </div>
        </div>
    </div>

    {content}
</div>
{{%% endblock %%}}"""
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(f'templates/{path}'), exist_ok=True)
    
    with open(f'templates/{path}', 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"Created: templates/{path}")

def main():
    """Create all remaining templates"""
    
    # MAHALSHIFA Module Templates
    create_template('mahalshifa/hospital_list.html',
        'Hospitals',
        '''<h1 class="h3 mb-0 text-gray-800">🏥 Hospitals</h1>
        <a href="{%% url 'mahalshifa:hospital_create' %%}" class="btn btn-primary">
            <i class="fas fa-plus fa-sm"></i> Add Hospital
        </a>''',
        '''
        <div class="card shadow mb-4">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">Hospitals Directory</h6>
            </div>
            <div class="card-body">
                {%% if hospitals %%}
                    <div class="row">
                        {%% for hospital in hospitals %%}
                        <div class="col-md-6 col-lg-4 mb-4">
                            <div class="card h-100">
                                <div class="card-body">
                                    <h5 class="card-title">
                                        <a href="{%% url 'mahalshifa:hospital_detail' hospital.pk %%}">{{ hospital.name }}</a>
                                    </h5>
                                    <p class="card-text">
                                        <i class="fas fa-map-marker-alt text-muted"></i> {{ hospital.location }}<br>
                                        <i class="fas fa-tag text-muted"></i> {{ hospital.get_hospital_type_display }}<br>
                                        <i class="fas fa-bed text-muted"></i> {{ hospital.total_beds }} beds
                                    </p>
                                    <div class="text-muted small">
                                        <i class="fas fa-phone"></i> {{ hospital.contact_phone }}
                                    </div>
                                </div>
                            </div>
                        </div>
                        {%% endfor %%}
                    </div>
                {%% else %%}
                    <p class="text-muted">No hospitals registered yet.</p>
                {%% endif %%}
            </div>
        </div>''')

    create_template('mahalshifa/hospital_detail.html',
        '{{ hospital.name }} - Hospital Details',
        '''<div>
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="{%% url 'mahalshifa:dashboard' %%}">Mahal Shifa</a></li>
                    <li class="breadcrumb-item"><a href="{%% url 'mahalshifa:hospital_list' %%}">Hospitals</a></li>
                    <li class="breadcrumb-item active">{{ hospital.name|truncatechars:30 }}</li>
                </ol>
            </nav>
            <h1 class="h3 mb-0 text-gray-800">🏥 {{ hospital.name }}</h1>
        </div>
        <div>
            {%% if can_edit %%}
                <a href="{%% url 'mahalshifa:hospital_update' hospital.pk %%}" class="btn btn-warning btn-sm">Edit</a>
            {%% endif %%}
        </div>''',
        '''
        <div class="row">
            <div class="col-lg-8">
                <div class="card shadow mb-4">
                    <div class="card-header py-3">
                        <h6 class="m-0 font-weight-bold text-primary">Hospital Information</h6>
                    </div>
                    <div class="card-body">
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <strong>Type:</strong> <span class="badge badge-info ml-2">{{ hospital.get_hospital_type_display }}</span>
                            </div>
                            <div class="col-md-6">
                                <strong>Total Beds:</strong> {{ hospital.total_beds }}
                            </div>
                        </div>
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <strong>Location:</strong> {{ hospital.location }}
                            </div>
                            <div class="col-md-6">
                                <strong>Contact:</strong> {{ hospital.contact_phone }}
                            </div>
                        </div>
                        {%% if hospital.description %%}
                        <div class="mb-3">
                            <h6 class="font-weight-bold">Description:</h6>
                            <div class="border-left-primary pl-3">
                                {{ hospital.description|linebreaks }}
                            </div>
                        </div>
                        {%% endif %%}
                    </div>
                </div>
            </div>
            <div class="col-lg-4">
                <div class="card shadow mb-4">
                    <div class="card-header py-3">
                        <h6 class="m-0 font-weight-bold text-primary">Statistics</h6>
                    </div>
                    <div class="card-body">
                        <div class="text-center mb-3">
                            <div class="h4 text-primary">{{ total_patients }}</div>
                            <div class="text-muted">Total Patients</div>
                        </div>
                        <div class="text-center mb-3">
                            <div class="h4 text-success">{{ total_appointments }}</div>
                            <div class="text-muted">Appointments</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>''')

    create_template('mahalshifa/patient_list.html',
        'Patients',
        '''<h1 class="h3 mb-0 text-gray-800">👥 Patients</h1>
        <a href="{%% url 'mahalshifa:patient_create' %%}" class="btn btn-primary">
            <i class="fas fa-plus fa-sm"></i> Add Patient
        </a>''',
        '''
        <div class="card shadow mb-4">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">Patients Directory</h6>
            </div>
            <div class="card-body">
                {%% if patients %%}
                    <div class="table-responsive">
                        <table class="table table-bordered">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>ITS ID</th>
                                    <th>Age</th>
                                    <th>Gender</th>
                                    <th>Contact</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {%% for patient in patients %%}
                                <tr>
                                    <td>
                                        <a href="{%% url 'mahalshifa:patient_detail' patient.pk %%}">
                                            {{ patient.user.get_full_name }}
                                        </a>
                                    </td>
                                    <td>{{ patient.user.its_id }}</td>
                                    <td>{{ patient.age }}</td>
                                    <td>{{ patient.get_gender_display }}</td>
                                    <td>{{ patient.user.phone_number }}</td>
                                    <td>
                                        <a href="{%% url 'mahalshifa:patient_detail' patient.pk %%}" class="btn btn-sm btn-primary">View</a>
                                    </td>
                                </tr>
                                {%% endfor %%}
                            </tbody>
                        </table>
                    </div>
                {%% else %%}
                    <p class="text-muted">No patients registered yet.</p>
                {%% endif %%}
            </div>
        </div>''')

    create_template('mahalshifa/appointment_list.html',
        'Appointments',
        '''<h1 class="h3 mb-0 text-gray-800">📅 Appointments</h1>
        <a href="{%% url 'mahalshifa:create_appointment' %%}" class="btn btn-primary">
            <i class="fas fa-plus fa-sm"></i> Schedule Appointment
        </a>''',
        '''
        <div class="card shadow mb-4">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">Appointments Schedule</h6>
            </div>
            <div class="card-body">
                {%% if appointments %%}
                    <div class="table-responsive">
                        <table class="table table-bordered">
                            <thead>
                                <tr>
                                    <th>Patient</th>
                                    <th>Doctor</th>
                                    <th>Date & Time</th>
                                    <th>Type</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {%% for appointment in appointments %%}
                                <tr>
                                    <td>
                                        <a href="{%% url 'mahalshifa:patient_detail' appointment.patient.pk %%}">
                                            {{ appointment.patient.user.get_full_name }}
                                        </a>
                                    </td>
                                    <td>{{ appointment.doctor.user.get_full_name }}</td>
                                    <td>
                                        {{ appointment.appointment_date|date:"M d, Y" }}<br>
                                        <small class="text-muted">{{ appointment.appointment_time }}</small>
                                    </td>
                                    <td>
                                        {%% if appointment.appointment_type == 'emergency' %%}
                                            <span class="badge badge-danger">Emergency</span>
                                        {%% elif appointment.appointment_type == 'urgent' %%}
                                            <span class="badge badge-warning">Urgent</span>
                                        {%% else %%}
                                            <span class="badge badge-info">Regular</span>
                                        {%% endif %%}
                                    </td>
                                    <td>
                                        {%% if appointment.status == 'scheduled' %%}
                                            <span class="badge badge-warning">Scheduled</span>
                                        {%% elif appointment.status == 'completed' %%}
                                            <span class="badge badge-success">Completed</span>
                                        {%% elif appointment.status == 'cancelled' %%}
                                            <span class="badge badge-danger">Cancelled</span>
                                        {%% else %%}
                                            <span class="badge badge-info">{{ appointment.get_status_display }}</span>
                                        {%% endif %%}
                                    </td>
                                    <td>
                                        <a href="{%% url 'mahalshifa:appointment_detail' appointment.pk %%}" class="btn btn-sm btn-primary">View</a>
                                    </td>
                                </tr>
                                {%% endfor %%}
                            </tbody>
                        </table>
                    </div>
                {%% else %%}
                    <p class="text-muted">No appointments scheduled.</p>
                {%% endif %%}
            </div>
        </div>''')

    create_template('mahalshifa/appointment_detail.html',
        'Appointment Details',
        '''<div>
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="{%% url 'mahalshifa:dashboard' %%}">Mahal Shifa</a></li>
                    <li class="breadcrumb-item"><a href="{%% url 'mahalshifa:appointment_list' %%}">Appointments</a></li>
                    <li class="breadcrumb-item active">Appointment Details</li>
                </ol>
            </nav>
            <h1 class="h3 mb-0 text-gray-800">📅 Appointment Details</h1>
        </div>''',
        '''
        <div class="card shadow mb-4">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">Appointment Information</h6>
            </div>
            <div class="card-body">
                <div class="row mb-3">
                    <div class="col-md-6">
                        <strong>Patient:</strong> {{ appointment.patient.user.get_full_name }}
                    </div>
                    <div class="col-md-6">
                        <strong>Doctor:</strong> {{ appointment.doctor.user.get_full_name }}
                    </div>
                </div>
                <div class="row mb-3">
                    <div class="col-md-6">
                        <strong>Date:</strong> {{ appointment.appointment_date|date:"F d, Y" }}
                    </div>
                    <div class="col-md-6">
                        <strong>Time:</strong> {{ appointment.appointment_time }}
                    </div>
                </div>
                <div class="row mb-3">
                    <div class="col-md-6">
                        <strong>Type:</strong>
                        {%% if appointment.appointment_type == 'emergency' %%}
                            <span class="badge badge-danger ml-2">Emergency</span>
                        {%% elif appointment.appointment_type == 'urgent' %%}
                            <span class="badge badge-warning ml-2">Urgent</span>
                        {%% else %%}
                            <span class="badge badge-info ml-2">Regular</span>
                        {%% endif %%}
                    </div>
                    <div class="col-md-6">
                        <strong>Status:</strong>
                        {%% if appointment.status == 'scheduled' %%}
                            <span class="badge badge-warning ml-2">Scheduled</span>
                        {%% elif appointment.status == 'completed' %%}
                            <span class="badge badge-success ml-2">Completed</span>
                        {%% elif appointment.status == 'cancelled' %%}
                            <span class="badge badge-danger ml-2">Cancelled</span>
                        {%% endif %%}
                    </div>
                </div>
                {%% if appointment.notes %%}
                <div class="mb-3">
                    <h6 class="font-weight-bold">Notes:</h6>
                    <div class="border-left-primary pl-3">
                        {{ appointment.notes|linebreaks }}
                    </div>
                </div>
                {%% endif %%}
            </div>
        </div>''')

    create_template('mahalshifa/patient_detail.html',
        '{{ patient.user.get_full_name }} - Patient Details',
        '''<div>
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="{%% url 'mahalshifa:dashboard' %%}">Mahal Shifa</a></li>
                    <li class="breadcrumb-item"><a href="{%% url 'mahalshifa:patient_list' %%}">Patients</a></li>
                    <li class="breadcrumb-item active">{{ patient.user.get_full_name|truncatechars:30 }}</li>
                </ol>
            </nav>
            <h1 class="h3 mb-0 text-gray-800">👤 {{ patient.user.get_full_name }}</h1>
        </div>''',
        '''
        <div class="card shadow mb-4">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">Patient Information</h6>
            </div>
            <div class="card-body">
                <div class="row mb-3">
                    <div class="col-md-6">
                        <strong>ITS ID:</strong> {{ patient.user.its_id }}
                    </div>
                    <div class="col-md-6">
                        <strong>Age:</strong> {{ patient.age }}
                    </div>
                </div>
                <div class="row mb-3">
                    <div class="col-md-6">
                        <strong>Gender:</strong> {{ patient.get_gender_display }}
                    </div>
                    <div class="col-md-6">
                        <strong>Contact:</strong> {{ patient.user.phone_number }}
                    </div>
                </div>
                {%% if patient.medical_history %%}
                <div class="mb-3">
                    <h6 class="font-weight-bold">Medical History:</h6>
                    <div class="border-left-primary pl-3">
                        {{ patient.medical_history|linebreaks }}
                    </div>
                </div>
                {%% endif %%}
            </div>
        </div>''')

    create_template('mahalshifa/create_appointment.html',
        'Schedule Appointment',
        '<h1 class="h3 mb-0 text-gray-800">📅 Schedule New Appointment</h1>',
        '''
        <div class="card shadow">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">Appointment Details</h6>
            </div>
            <div class="card-body">
                <form method="post">
                    {%% csrf_token %%}
                    {{ form.as_p }}
                    <div class="d-flex justify-content-between">
                        <a href="{%% url 'mahalshifa:appointment_list' %%}" class="btn btn-secondary">Cancel</a>
                        <button type="submit" class="btn btn-primary">Schedule Appointment</button>
                    </div>
                </form>
            </div>
        </div>''')

    create_template('mahalshifa/analytics.html',
        'Medical Analytics',
        '<h1 class="h3 mb-0 text-gray-800">📊 Medical Analytics</h1>',
        '''
        <div class="card shadow mb-4">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">Medical Analytics Dashboard</h6>
            </div>
            <div class="card-body">
                <p>Medical analytics charts and statistics will be displayed here.</p>
            </div>
        </div>''')

    create_template('mahalshifa/inventory.html',
        'Inventory Management',
        '<h1 class="h3 mb-0 text-gray-800">📦 Inventory Management</h1>',
        '''
        <div class="card shadow mb-4">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">Medical Inventory</h6>
            </div>
            <div class="card-body">
                <p>Inventory management features will be displayed here.</p>
            </div>
        </div>''')

    # PHOTOS Module Templates
    create_template('photos/album_list.html',
        'Photo Albums',
        '''<h1 class="h3 mb-0 text-gray-800">📸 Photo Albums</h1>
        <a href="{%% url 'photos:album_create' %%}" class="btn btn-primary">
            <i class="fas fa-plus fa-sm"></i> Create Album
        </a>''',
        '''
        <div class="card shadow mb-4">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">Albums Gallery</h6>
            </div>
            <div class="card-body">
                {%% if albums %%}
                    <div class="row">
                        {%% for album in albums %%}
                        <div class="col-md-6 col-lg-4 mb-4">
                            <div class="card h-100">
                                <div class="card-img-top bg-light d-flex align-items-center justify-content-center" style="height: 200px;">
                                    {%% if album.photos.first %%}
                                        <img src="{{ album.photos.first.image.url }}" class="img-fluid" style="max-height: 190px; object-fit: cover;">
                                    {%% else %%}
                                        <i class="fas fa-images fa-4x text-gray-300"></i>
                                    {%% endif %%}
                                </div>
                                <div class="card-body">
                                    <h5 class="card-title">
                                        <a href="{%% url 'photos:album_detail' album.pk %%}">{{ album.name }}</a>
                                    </h5>
                                    <p class="card-text">{{ album.description|truncatechars:100 }}</p>
                                    <div class="d-flex justify-content-between align-items-center">
                                        <small class="text-muted">{{ album.photo_count }} photos</small>
                                        <small class="text-muted">{{ album.created_at|date:"M d" }}</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                        {%% endfor %%}
                    </div>
                {%% else %%}
                    <div class="text-center py-5">
                        <i class="fas fa-images fa-4x text-gray-300 mb-3"></i>
                        <h4 class="text-gray-400">No albums yet</h4>
                        <p class="text-muted">Create your first photo album to get started.</p>
                        <a href="{%% url 'photos:album_create' %%}" class="btn btn-primary">Create Album</a>
                    </div>
                {%% endif %%}
            </div>
        </div>''')

    print(f"\nCreated mahalshifa and photos templates successfully!")

if __name__ == '__main__':
    main()