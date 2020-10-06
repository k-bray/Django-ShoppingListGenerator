from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.utils import timezone
from django.forms import formset_factory
from .models import Meal, AddToMenu, MyList
from .forms import MealForm, AddToMenuForm, RemoveFromMenuForm
from .shoplist import shopping_list, ingredient_adjust, combine_amounts
from django.contrib import messages
import sqlite3
from pandas import DataFrame
import pandas as pd
import json


def home(request):
	return render(request, 'shoplist/home.html')

def signupuser(request):
	if request.method == "GET":
		return render(request, 'shoplist/signupuser.html', {'form':UserCreationForm()})
	else:
		if request.POST['password1'] == request.POST['password2']:
			try:
				user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
				user.save()
				login(request, user)
				return redirect('home')
			except IntegrityError:
				return render(request, 'shoplist/signupuser.html', {'form':UserCreationForm(), 'error':'That username has already been taken. Please choose another.'})
		else:
			return render(request, 'shoplist/signupuser.html', {'form':UserCreationForm(), 'error':'Passwords did not match'})

def loginuser(request):
	if request.method == "GET":
		return render(request, 'shoplist/loginuser.html', {'form':AuthenticationForm()})
	else:
		user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
		if user is None:
			return render(request, 'shoplist/loginuser.html', {'form':AuthenticationForm(), 'error': 'Username and password did not match'})
		else:
			login(request, user)
			return redirect('home')

@login_required
def logoutuser(request):
	if request.method == "POST":
		logout(request)
		return redirect('home')


@login_required
def generate(request):
	
	meals = Meal.objects.filter(user=request.user)
	menu = AddToMenu.objects.filter(user=request.user)

	if request.method == "GET":
		return render(request, 'shoplist/generate.html', {'meals':meals, 'form':MealForm(), 'menu':menu})
		
	
	elif request.method == "POST":
		
		if 'newmeal' in request.POST:
			return render(request, 'shoplist/addmeal.html', {'form':MealForm()})

		elif 'addtomenu' in request.POST:
			return render(request, 'shoplist/addtomenu.html', {'meal':meal})
		
		elif 'removefrommenu' in request.POST:
			return render(request, 'shoplist/removefrommenu.html', {'meal':meal})
						
	
	return redirect('meals')
		
@login_required
def addmeal(request):
 	
	if request.method == "GET":
		return render(request, 'shoplist/addmeal.html', {'form':MealForm()})
	elif request.method == "POST":
		try:
			form = MealForm(request.POST)
			meal = form.save(commit=False)
			meal.user = request.user
			meal.save()
			return redirect('generate')
		except ValueError:
			return render(request, 'shoplist/addmeal.html', {'form':MealForm(), 'error':'Invalid data passed in'})


@login_required
def samplemeals(request):

 	return render(request, 'shoplist/samplemeals.html', {'form':MealForm()})

@login_required
def viewmeal(request, meal_pk):
	meal = get_object_or_404(Meal, pk=meal_pk)
	return render(request, 'shoplist/viewmeal.html', {'meal':meal})

@login_required
def editmeal(request, meal_pk):
	meal = get_object_or_404(Meal, pk=meal_pk)
	form = MealForm(instance=meal)
	return render(request, 'shoplist/editmeal.html', {'meal':meal, 'form':form})

@login_required
def addtomenu(request, meal_pk):
	meal = get_object_or_404(Meal, pk=meal_pk)
	

	if request.method == "GET":
		form = AddToMenuForm(initial={'meal': meal.name, 'servings': meal.servings})
		return render(request, 'shoplist/addtomenu.html', {'meal':meal, 'form':form})
		
		
	elif request.method == "POST":
		try:
			form = AddToMenuForm(request.POST)
			selectedmeal = form.save(commit=False)
			selectedmeal.user = request.user
			selectedmeal.save()

			return redirect('generate')
		except ValueError:
			return render(request, 'shoplist/addtomenu.html', {'form':AddToMenuForm(), 'error':'Invalid data passed in'})

@login_required
def removefrommenu(request, meal_pk):

	meal = AddToMenu.objects.get(pk=meal_pk)
	print(meal)
	meal.delete()
	return redirect('generate')


@login_required
def newshoppinglist(request):
	menu = AddToMenu.objects.filter(user=request.user)

	all_meals = []
	selected_meals = {}

	conn = sqlite3.connect("db.sqlite3")
	c = conn.cursor()

	#get all possible meals and ingredients from users account
	c.execute("SELECT * FROM shoplist_meal")
	for result in c:
		ingredientdict = {}
		for i in result[4].splitlines():
			split_i = i.split(', ')
			ingredientdict[split_i[0]] = split_i[1]

		meal_details = [result[1], result[2], ingredientdict]
		all_meals.append(meal_details)

	#get meal selections and serving sizes from menu in users account
	c.execute("SELECT * FROM shoplist_addtomenu ")
	for result in c:
		print(result)
		selected_meals[result[1]] = result[2]
		
	conn.close()

	#compile ingredients list from backend code
	shoppinglist = shopping_list(all_meals, selected_meals)

	json_records = shoppinglist.reset_index().to_json(orient = 'records')
	data = []
	data = json.loads(json_records)

	print(data)

	model = MyList()
	model.data = data
	model.user = request.user
	model.save()

	
	context = {'d':data}

	menu.delete()

	return render(request, 'shoplist/newshoppinglist.html', context)


@login_required
def mylists(request):
	shoplists = MyList.objects.filter(user=request.user)
	
	return render(request, 'shoplist/mylists.html', {'shoplists':shoplists})

@login_required
def mylist(request, list_pk):

	shoplist = MyList.objects.get(pk=list_pk)
	shoplistdata = str(shoplist.data).replace("'", '"')

	data = []
	data = json.loads(shoplistdata)

	context = {'d':data}
	return render(request, 'shoplist/mylist.html', context)
