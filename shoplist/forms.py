from django.forms import ModelForm
from .models import Meal, AddToMenu

class MealForm(ModelForm):
	class Meta:
		model = Meal
		fields = ['name','servings','ingredients']


class AddToMenuForm(ModelForm):
	class Meta:
		model = AddToMenu
		fields = ['meal','servings']

class RemoveFromMenuForm(ModelForm):
	class Meta:
		model = AddToMenu
		fields = ['meal']

