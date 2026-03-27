from django import forms
from .models import IssueReport, Message


class IssueReportForm(forms.ModelForm):
    """Form for submitting a new service delivery issue."""

    class Meta:
        model = IssueReport
        fields = ['title', 'category', 'description', 'location', 'ward_number', 'photo', 'priority']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'e.g. Large pothole on Main Street near school',
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe the issue in detail. Include how long it has been a problem, how it affects residents, etc.',
                'class': 'form-control'
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'e.g. 45 Dingaan Street, Galeshewe, Kimberley',
                'class': 'form-control'
            }),
            'ward_number': forms.TextInput(attrs={
                'placeholder': 'e.g. Ward 5',
                'class': 'form-control'
            }),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }


class MessageForm(forms.ModelForm):
    """Form for sending a message on a report."""

    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Type your message here...',
                'class': 'form-control'
            })
        }
        labels = {
            'content': ''
        }


class StatusUpdateForm(forms.ModelForm):
    """Form for officials to update report status."""

    class Meta:
        model = IssueReport
        fields = ['status', 'priority', 'assigned_to']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }


class ReportFilterForm(forms.Form):
    """Filter reports by category and status."""
    CATEGORY_CHOICES = [('', 'All Categories')] + IssueReport.CATEGORY_CHOICES
    STATUS_CHOICES = [('', 'All Statuses')] + IssueReport.STATUS_CHOICES

    category = forms.ChoiceField(choices=CATEGORY_CHOICES, required=False,
                                  widget=forms.Select(attrs={'class': 'form-select form-select-sm'}))
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False,
                                widget=forms.Select(attrs={'class': 'form-select form-select-sm'}))
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-sm',
        'placeholder': 'Search by title or location...'
    }))
