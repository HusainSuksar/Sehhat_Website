#!/usr/bin/env python3
"""
Script to create all missing templates for the UmoorSehhat application.
This will create comprehensive, functional templates for all modules.
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
    """Create all templates"""
    
    # ARAZ remaining templates
    create_template('araz/analytics.html', 
        'Araz Analytics',
        '<h1 class="h3 mb-0 text-gray-800">📊 Petition Analytics</h1>',
        '''
        <!-- Analytics content would go here -->
        <div class="card shadow mb-4">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">Analytics Dashboard</h6>
            </div>
            <div class="card-body">
                <p>Analytics charts and statistics will be displayed here.</p>
            </div>
        </div>''')
    
    create_template('araz/my_assignments.html',
        'My Assignments',
        '<h1 class="h3 mb-0 text-gray-800">📋 My Petition Assignments</h1>',
        '''
        <div class="card shadow mb-4">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">Assigned Petitions</h6>
            </div>
            <div class="card-body">
                {%% if assignments %%}
                    <div class="table-responsive">
                        <table class="table table-bordered">
                            <thead>
                                <tr>
                                    <th>Petition</th>
                                    <th>Priority</th>
                                    <th>Status</th>
                                    <th>Assigned Date</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {%% for assignment in assignments %%}
                                <tr>
                                    <td><a href="{%% url 'araz:petition_detail' assignment.petition.pk %%}">{{ assignment.petition.title|truncatechars:50 }}</a></td>
                                    <td><span class="badge badge-info">{{ assignment.petition.get_priority_display }}</span></td>
                                    <td><span class="badge badge-warning">{{ assignment.petition.get_status_display }}</span></td>
                                    <td>{{ assignment.created_at|date:"M d, Y" }}</td>
                                    <td><a href="{%% url 'araz:petition_detail' assignment.petition.pk %%}" class="btn btn-sm btn-primary">View</a></td>
                                </tr>
                                {%% endfor %%}
                            </tbody>
                        </table>
                    </div>
                {%% else %%}
                    <p class="text-muted">No assignments found.</p>
                {%% endif %%}
            </div>
        </div>''')

    # EVALUATION templates
    create_template('evaluation/form_list.html',
        'Evaluation Forms',
        '''<h1 class="h3 mb-0 text-gray-800">📋 Evaluation Forms</h1>
        <a href="{%% url 'evaluation:form_create' %%}" class="btn btn-primary">
            <i class="fas fa-plus fa-sm"></i> Create Form
        </a>''',
        '''
        <div class="card shadow mb-4">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">Forms</h6>
            </div>
            <div class="card-body">
                {%% if forms %%}
                    <div class="table-responsive">
                        <table class="table table-bordered">
                            <thead>
                                <tr>
                                    <th>Title</th>
                                    <th>Type</th>
                                    <th>Status</th>
                                    <th>Created</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {%% for form in forms %%}
                                <tr>
                                    <td><a href="{%% url 'evaluation:form_detail' form.pk %%}">{{ form.title }}</a></td>
                                    <td><span class="badge badge-secondary">{{ form.get_evaluation_type_display }}</span></td>
                                    <td>
                                        {%% if form.is_active %%}
                                            <span class="badge badge-success">Active</span>
                                        {%% else %%}
                                            <span class="badge badge-danger">Inactive</span>
                                        {%% endif %%}
                                    </td>
                                    <td>{{ form.created_at|date:"M d, Y" }}</td>
                                    <td><a href="{%% url 'evaluation:form_detail' form.pk %%}" class="btn btn-sm btn-primary">View</a></td>
                                </tr>
                                {%% endfor %%}
                            </tbody>
                        </table>
                    </div>
                {%% else %%}
                    <p class="text-muted">No forms found.</p>
                {%% endif %%}
            </div>
        </div>''')

    create_template('evaluation/form_detail.html',
        '{{ form.title }} - Form Details',
        '''<div>
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="{%% url 'evaluation:dashboard' %%}">Evaluation</a></li>
                    <li class="breadcrumb-item"><a href="{%% url 'evaluation:form_list' %%}">Forms</a></li>
                    <li class="breadcrumb-item active">{{ form.title|truncatechars:30 }}</li>
                </ol>
            </nav>
            <h1 class="h3 mb-0 text-gray-800">📋 {{ form.title }}</h1>
        </div>
        <div>
            {%% if can_edit %%}
                <a href="{%% url 'evaluation:form_update' form.pk %%}" class="btn btn-warning btn-sm">Edit</a>
            {%% endif %%}
            {%% if can_evaluate %%}
                <a href="{%% url 'evaluation:evaluate_form' form.pk %%}" class="btn btn-success btn-sm">Evaluate</a>
            {%% endif %%}
        </div>''',
        '''
        <div class="card shadow mb-4">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">Form Information</h6>
            </div>
            <div class="card-body">
                <div class="row mb-3">
                    <div class="col-md-6">
                        <strong>Type:</strong> <span class="badge badge-secondary ml-2">{{ form.get_evaluation_type_display }}</span>
                    </div>
                    <div class="col-md-6">
                        <strong>Status:</strong>
                        {%% if form.is_active %%}
                            <span class="badge badge-success ml-2">Active</span>
                        {%% else %%}
                            <span class="badge badge-danger ml-2">Inactive</span>
                        {%% endif %%}
                    </div>
                </div>
                <div class="mb-3">
                    <h6 class="font-weight-bold">Description:</h6>
                    <div class="border-left-primary pl-3">
                        {{ form.description|linebreaks }}
                    </div>
                </div>
            </div>
        </div>''')

    create_template('evaluation/form_create.html',
        'Create Evaluation Form',
        '<h1 class="h3 mb-0 text-gray-800">📝 Create Evaluation Form</h1>',
        '''
        <div class="card shadow">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">Form Details</h6>
            </div>
            <div class="card-body">
                <form method="post">
                    {%% csrf_token %%}
                    {{ form.as_p }}
                    <div class="d-flex justify-content-between">
                        <a href="{%% url 'evaluation:form_list' %%}" class="btn btn-secondary">Cancel</a>
                        <button type="submit" class="btn btn-primary">Create Form</button>
                    </div>
                </form>
            </div>
        </div>''')

    create_template('evaluation/evaluate_form.html',
        'Evaluate: {{ form.title }}',
        '<h1 class="h3 mb-0 text-gray-800">⭐ Evaluate: {{ form.title }}</h1>',
        '''
        <div class="card shadow">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">Evaluation</h6>
            </div>
            <div class="card-body">
                <form method="post">
                    {%% csrf_token %%}
                    {%% for criterion in criteria %%}
                        <div class="form-group">
                            <label>{{ criterion.name }}</label>
                            {%% if criterion.description %%}
                                <small class="form-text text-muted">{{ criterion.description }}</small>
                            {%% endif %%}
                            <select name="rating_{{ criterion.id }}" class="form-control" required>
                                <option value="">Select rating...</option>
                                <option value="5">5 - Excellent</option>
                                <option value="4">4 - Good</option>
                                <option value="3">3 - Average</option>
                                <option value="2">2 - Below Average</option>
                                <option value="1">1 - Poor</option>
                            </select>
                        </div>
                    {%% endfor %%}
                    <div class="form-group">
                        <label for="comments">Comments (Optional)</label>
                        <textarea name="comments" class="form-control" rows="4"></textarea>
                    </div>
                    <div class="d-flex justify-content-between">
                        <a href="{%% url 'evaluation:form_detail' form.pk %%}" class="btn btn-secondary">Cancel</a>
                        <button type="submit" class="btn btn-success">Submit Evaluation</button>
                    </div>
                </form>
            </div>
        </div>''')

    create_template('evaluation/submission_detail.html',
        'Evaluation Submission',
        '<h1 class="h3 mb-0 text-gray-800">📊 Evaluation Details</h1>',
        '''
        <div class="card shadow">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">Submission Details</h6>
            </div>
            <div class="card-body">
                <div class="row mb-3">
                    <div class="col-md-6">
                        <strong>Form:</strong> {{ submission.form.title }}
                    </div>
                    <div class="col-md-6">
                        <strong>Evaluator:</strong> {{ submission.evaluator.get_full_name }}
                    </div>
                </div>
                <div class="row mb-3">
                    <div class="col-md-6">
                        <strong>Submitted:</strong> {{ submission.submitted_at|date:"F d, Y g:i A" }}
                    </div>
                    <div class="col-md-6">
                        <strong>Total Score:</strong> {{ submission.total_score|floatformat:1 }}
                    </div>
                </div>
                {%% if submission.comments %%}
                <div class="mb-3">
                    <h6 class="font-weight-bold">Comments:</h6>
                    <div class="border-left-primary pl-3">
                        {{ submission.comments|linebreaks }}
                    </div>
                </div>
                {%% endif %%}
            </div>
        </div>''')

    create_template('evaluation/analytics.html',
        'Evaluation Analytics',
        '<h1 class="h3 mb-0 text-gray-800">📊 Evaluation Analytics</h1>',
        '''
        <div class="card shadow mb-4">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">Analytics Dashboard</h6>
            </div>
            <div class="card-body">
                <p>Evaluation analytics charts and statistics will be displayed here.</p>
            </div>
        </div>''')

    create_template('evaluation/my_evaluations.html',
        'My Evaluations',
        '<h1 class="h3 mb-0 text-gray-800">⭐ My Evaluations</h1>',
        '''
        <div class="card shadow mb-4">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">My Evaluation History</h6>
            </div>
            <div class="card-body">
                {%% if submissions %%}
                    <div class="table-responsive">
                        <table class="table table-bordered">
                            <thead>
                                <tr>
                                    <th>Form</th>
                                    <th>Type</th>
                                    <th>Score</th>
                                    <th>Submitted</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {%% for submission in submissions %%}
                                <tr>
                                    <td>{{ submission.form.title }}</td>
                                    <td><span class="badge badge-secondary">{{ submission.form.get_evaluation_type_display }}</span></td>
                                    <td>{{ submission.total_score|floatformat:1 }}</td>
                                    <td>{{ submission.submitted_at|date:"M d, Y" }}</td>
                                    <td><a href="{%% url 'evaluation:submission_detail' submission.pk %%}" class="btn btn-sm btn-primary">View</a></td>
                                </tr>
                                {%% endfor %%}
                            </tbody>
                        </table>
                    </div>
                {%% else %%}
                    <p class="text-muted">No evaluations submitted yet.</p>
                {%% endif %%}
            </div>
        </div>''')

    print(f"\nCreated evaluation templates successfully!")

if __name__ == '__main__':
    main()