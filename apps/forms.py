import json
from pathlib import Path
from django import forms
from .models import Service,Team
from django.core.exceptions import ValidationError

class DynamicProposalForm(forms.Form):
    def __init__(self, website_type, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Static client fields
        self.fields['client_name'] = forms.CharField(
            label="Full Name",
            max_length=100,
            required=True
        )
        self.fields['client_email'] = forms.EmailField(
            label="Email",
            required=True
        )
        self.fields['client_phone'] = forms.CharField(
            label="Phone Number",
            max_length=20,
            required=False
        )
        self.fields['client_company'] = forms.CharField(
            label="Company (optional)",
            max_length=100,
            required=False
        )

        # Load questions from JSON
        BASE_DIR = Path(__file__).resolve().parent.parent  # fraternal folder
        safe_name = website_type.lower().replace(' ', '').replace('-', '')  # sanitize name
        json_path = BASE_DIR / 'website_types' / f'{safe_name}.json'

        # Debug print or logging
        print("\n" + "="*50)
        print(f"INATAFUTA FAILI HAPA: {json_path}")
        print("="*50 + "\n")

        if not json_path.exists():
            raise forms.ValidationError(f"Faili ya {website_type}.json haipatikani. Hakikisha iko katika: {json_path}")

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                questions = json.load(f)

            for field_name, field_data in questions.items():
                field_label = field_data.get('question', field_name)
                is_required = field_data.get('required', True)

                if field_data['type'] == 'text':
                    self.fields[field_name] = forms.CharField(
                        label=field_label,
                        required=is_required
                    )
                elif field_data['type'] == 'checkbox':
                    self.fields[field_name] = forms.MultipleChoiceField(
                        choices=[(opt, opt) for opt in field_data['options']],
                        widget=forms.CheckboxSelectMultiple,
                        label=field_label,
                        required=is_required
                    )
        except json.JSONDecodeError:
            raise forms.ValidationError(f"Faili ya {website_type}.json haijaandikwa vizuri. Angalia syntax ya JSON")




class ServiceAdminForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = '__all__'

    class Media:
        js = [
            'https://ucarecdn.com/libs/widget/3.x/uploadcare.full.min.js',
        ]


class TeamAdminForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = '__all__'

    class Media:
        js = [
            'https://ucarecdn.com/libs/widget/3.x/uploadcare.full.min.js',
        ]
