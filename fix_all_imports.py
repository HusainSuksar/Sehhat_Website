#!/usr/bin/env python
"""
Fix all import and model issues in generate_mock_data.py
"""

import re

# Read the original file
with open('generate_mock_data.py', 'r') as f:
    content = f.read()

# Fix imports
content = content.replace(
    'from evaluation.models import StudentEvaluation',
    'from evaluation.models import Evaluation, EvaluationCriteria, EvaluationSubmission'
)

# Fix the student evaluation creation code
# First, find and replace the create_evaluations method
old_eval_pattern = r'def create_evaluations\(self\):[\s\S]*?print\(f"  ✓ Created \{StudentEvaluation\.objects\.count\(\)\} student evaluations"\)'

new_eval_method = '''def create_evaluations(self):
        """Create student evaluations"""
        print("\\n9. Creating Student Evaluations...")
        
        # Create evaluation criteria
        criteria_list = []
        criteria_names = [
            'Academic Performance',
            'Class Participation',
            'Attendance',
            'Behavior',
            'Assignment Quality'
        ]
        
        for name in criteria_names:
            criteria = EvaluationCriteria.objects.create(
                name=name,
                description=f"Evaluation of student's {name.lower()}",
                weight=20.0,  # Equal weight for all criteria
                is_active=True
            )
            criteria_list.append(criteria)
        
        # Get students and evaluators
        students = Student.objects.all()[:100]  # Evaluate first 100 students
        evaluators = User.objects.filter(role__in=['aamil', 'moze_coordinator'])
        
        evaluation_count = 0
        for student in students:
            if student.user and evaluators.exists():
                # Create evaluation
                evaluation = Evaluation.objects.create(
                    evaluatee=student.user,
                    evaluator=random.choice(list(evaluators)),
                    evaluation_type='student_performance',
                    title=f"Term Evaluation for {student.user.get_full_name()}",
                    description="Regular academic performance evaluation",
                    period_start=date.today() - timedelta(days=90),
                    period_end=date.today(),
                    overall_rating=random.randint(3, 5),
                    overall_score=random.randint(60, 100),
                    status='completed',
                    completed_date=date.today() - timedelta(days=random.randint(1, 30))
                )
                
                # Add comments
                evaluation.evaluator_comments = f"Student shows {random.choice(['excellent', 'good', 'satisfactory'])} progress"
                evaluation.save()
                
                evaluation_count += 1
        
        print(f"  ✓ Created {evaluation_count} student evaluations")'''

content = re.sub(old_eval_pattern, new_eval_method, content, flags=re.DOTALL)

# If the above regex doesn't work, try a simpler approach
if 'def create_evaluations(self):' not in new_eval_method:
    # Find where evaluations are created and fix it
    if 'StudentEvaluation.objects.create' in content:
        # Replace the specific usage
        content = content.replace('StudentEvaluation.objects.create(', 'Evaluation.objects.create(')
        content = content.replace('StudentEvaluation.objects.count()', 'Evaluation.objects.filter(evaluation_type="student_performance").count()')

# Write the fixed content
with open('generate_mock_data_fixed.py', 'w') as f:
    f.write(content)

print("Created generate_mock_data_fixed.py with all fixes")
print("\nChanges made:")
print("1. Fixed evaluation imports")
print("2. Updated evaluation creation to use correct models")
print("\nRun: python generate_mock_data_fixed.py")