from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, StudentProfile

class StudentSignupForm(UserCreationForm):
    phone = forms.CharField(required=True)
    current_class = forms.CharField(required=True)
    target_exam = forms.ChoiceField(choices=StudentProfile.EXAM_TARGET_CHOICES)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('phone', 'first_name', 'last_name',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'STUDENT'
        user.phone = self.cleaned_data['phone']
        if commit:
            user.save()
            StudentProfile.objects.create(
                user=user,
                current_class=self.cleaned_data['current_class'],
                target_exam=self.cleaned_data['target_exam'],
                board='CBSE' # Default, can change later
            )
        return user