from django import forms
import requests


class CountryChoiceField(forms.ChoiceField):

    def __init__(self, *args, **kwargs):
        kwargs['choices'] = self.get_country_choices()
        super().__init__(*args, **kwargs)

    def get_country_choices(self):
        response = requests.get('https://restcountries.com/v3.1/all')
        data = response.json()
        country_choices = [(country['name']['common'], country['name']['common']) for country in data]
        country_choices.sort(key=lambda x: x[0])  # Sort choices alphabetically
        return country_choices

