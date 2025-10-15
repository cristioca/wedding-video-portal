from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Project, File


class LoginForm(forms.Form):
    """Login form"""
    username = forms.CharField(
        max_length=150,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class ProjectForm(forms.ModelForm):
    """Project creation form - simplified"""
    client_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Client full name',
            'id': 'id_client_name'
        })
    )
    client_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'client@example.com',
            'id': 'id_client_email'
        })
    )
    
    class Meta:
        model = Project
        fields = [
            'name', 'client_name', 'client_email', 'type', 'event_date', 'city'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_name'}),
            'type': forms.Select(attrs={'class': 'form-control', 'id': 'id_type'}),
            'event_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'id_event_date',
                'lang': 'en-GB'
            }),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Pre-populate client fields if editing existing project
        if self.instance and self.instance.pk:
            self.fields['client_name'].initial = self.instance.client_name
            self.fields['client_email'].initial = self.instance.client_email


class ProjectDetailForm(forms.ModelForm):
    """Project detail/editing form - includes all fields for editing"""
    client_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    client_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Project
        fields = [
            'name', 'client_name', 'client_email', 'type', 'status', 'edit_status', 'editing_progress',
            'event_date', 'city', 'title_video', 'civil_union_details',
            'prep', 'church', 'session', 'restaurant', 'main_details',
            'details_extra', 'editing_preferences', 'notes', 'filming_details',
            'videographer_filming_notes', 'critical_production_notes', 'videographer_editing_notes',
            'due_date',  # Due date for editing completion
            # Package fields
            'package_type', 'package_4k', 'package_fullhd', 'package_cameras',
            'montage_highlights', 'montage_movie', 'montage_movie_duration', 'montage_movie_other',
            'montage_bonus_primary', 'montage_bonus_full', 'montage_cinema_duration',
            'equipment_audio_recorder', 'equipment_stabilizer', 'equipment_external_light',
            'team_videographer', 'team_operator', 'team_assistant',
            'delivery_online', 'delivery_usb', 'event_presence',
            # Price fields (admin only)
            'price', 'price_currency', 'price_other_details'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'edit_status': forms.Select(attrs={'class': 'form-control'}),
            'editing_progress': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100', 'step': '5'}),
            'event_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'lang': 'en-GB'
            }),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'title_video': forms.TextInput(attrs={'class': 'form-control'}),
            'civil_union_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'prep': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'church': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'session': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'restaurant': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'details_extra': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'editing_preferences': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'filming_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'videographer_filming_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'critical_production_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'videographer_editing_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'lang': 'en-GB'
            }),
            'main_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 8}),
            # Package widgets
            'package_type': forms.Select(attrs={'class': 'form-control'}),
            'package_4k': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'package_fullhd': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'package_cameras': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'montage_highlights': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'montage_movie': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'montage_movie_duration': forms.Select(attrs={'class': 'form-control'}),
            'montage_movie_other': forms.TextInput(attrs={'class': 'form-control'}),
            'montage_bonus_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'montage_bonus_full': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'montage_cinema_duration': forms.Select(attrs={'class': 'form-control'}),
            'equipment_audio_recorder': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'equipment_stabilizer': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'equipment_external_light': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'team_videographer': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'team_operator': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'team_assistant': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'delivery_online': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'delivery_usb': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'event_presence': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            # Price widgets (admin only)
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'price_currency': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'price_other_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Pre-populate client fields if editing existing project
        if self.instance and self.instance.pk:
            self.fields['client_name'].initial = self.instance.client_name
            self.fields['client_email'].initial = self.instance.client_email
            
            # Remove civil_union_details field for Botez projects
            if self.instance.type == 'BOTEZ':
                if 'civil_union_details' in self.fields:
                    del self.fields['civil_union_details']


class FileUploadForm(forms.ModelForm):
    """File upload form"""
    class Meta:
        model = File
        fields = ['display_name', 'file']
        widgets = {
            'display_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Display name for the file'
            }),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }


class UserRegistrationForm(UserCreationForm):
    """User registration form"""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
