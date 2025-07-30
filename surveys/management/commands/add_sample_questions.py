from django.core.management.base import BaseCommand
from surveys.models import Survey


class Command(BaseCommand):
    help = 'Add sample questions to surveys that don\'t have any questions'

    def handle(self, *args, **options):
        surveys = Survey.objects.filter(questions=[])
        
        if not surveys.exists():
            self.stdout.write(self.style.SUCCESS('No surveys found without questions.'))
            return
        
        sample_questions = [
            {
                "id": 1,
                "type": "text",
                "question": "What is your name?",
                "required": True,
                "options": []
            },
            {
                "id": 2,
                "type": "multiple_choice",
                "question": "How satisfied are you with our services?",
                "required": True,
                "options": ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very Dissatisfied"]
            },
            {
                "id": 3,
                "type": "checkbox",
                "question": "Which services have you used?",
                "required": False,
                "options": ["Medical Consultation", "Health Screening", "Emergency Care", "Follow-up"]
            },
            {
                "id": 4,
                "type": "rating",
                "question": "Rate our service quality (1-5)",
                "required": True,
                "options": ["1", "2", "3", "4", "5"]
            },
            {
                "id": 5,
                "type": "textarea",
                "question": "Please provide any additional comments or suggestions:",
                "required": False,
                "options": []
            }
        ]
        
        for survey in surveys:
            survey.questions = sample_questions
            survey.save()
            self.stdout.write(
                self.style.SUCCESS(f'Added sample questions to survey: {survey.title}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully added sample questions to {surveys.count()} surveys.')
        )