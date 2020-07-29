from django import forms
from .models import Prediction
from django.forms import modelformset_factory, formset_factory


class PredictionForm(forms.ModelForm):
    class Meta:
        model = Prediction
        fields = ['game', 'player', 'match', 'joker']
        # match = forms.ComboField(label="Match", disabled=True, widget=forms.ComboField)
        home_score = forms.IntegerField(widget=forms.Textarea, label='')
        away_score = forms.IntegerField(widget=forms.Textarea, label='')
        # joker = forms.BooleanField(initial=False)
        # widgets = [{'player': forms.HiddenInput()}, {'game': forms.HiddenInput()}, {'match': forms.HiddenInput()}, ]


PredictionFormSet = modelformset_factory(model=Prediction, form=PredictionForm, extra=0)
