from django import forms
from .models import Ad, ExchangeProposal


class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ['title', 'description', 'image_url', 'category', 'condition']

    image_url = forms.URLField(assume_scheme='https', required=False)


class ExchangeProposalForm(forms.ModelForm):
    class Meta:
        model = ExchangeProposal
        fields = ['ad_sender', 'ad_receiver', 'comment']

    def clean(self):
        cleaned_data = super().clean()
        sender = cleaned_data.get('ad_sender')
        receiver = cleaned_data.get('ad_receiver')

        if sender and receiver:
            if sender == receiver:
                raise forms.ValidationError("Нельзя обмениваться одним и тем же объявлением.")
            if sender.user == receiver.user:
                raise forms.ValidationError("Нельзя обмениваться своими собственными объявлениями.")