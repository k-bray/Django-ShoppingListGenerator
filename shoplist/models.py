from django.db import models
from django.contrib.auth.models import User

class Meal(models.Model):
	name = models.CharField(max_length=50)
	servings = models.IntegerField()
	datecreated = models.DateTimeField(auto_now_add=True)
	ingredients = models.TextField()

	user = models.ForeignKey(User, on_delete=models.CASCADE)

	def __str__(self):
		return self.name


class AddToMenu(models.Model):
	meal = models.CharField(max_length=50)
	servings = models.IntegerField()

	user = models.ForeignKey(User, on_delete=models.CASCADE)

	def __str__(self):
		return self.meal

class MyList(models.Model):
	
	data = models.TextField(null=True)
	datecreated = models.DateTimeField(auto_now_add=True)

	user = models.ForeignKey(User, on_delete=models.CASCADE)

	


