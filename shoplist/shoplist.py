import pandas as pd
from pandas import DataFrame
import csv
from csv import writer, reader
import re


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def ingredient_adjust(originalservings, servings, ingredients):
    # adjusts ingredients for a meal based on stated servings
    scale = servings / originalservings
    for key, value in ingredients.items():
        valuelist = value.split()
        if len(valuelist) == 1:

            if is_number(value):
                n_ingredient = round((float(value) * scale), 1)
                if str(n_ingredient)[-1] == '0':
                    n_ingredient = int(n_ingredient)  # remove .0
                ingredients[key] = str(n_ingredient)

            elif value[-1:] == 'g' and is_number(value[:-1]):
                n_ingredient = float(value[:-1]) * scale
                ingredients[key] = str(int(n_ingredient)) + value[-1:]

            elif value[-1:] == 'l' and is_number(value[:-1]):
                n_ingredient = float(value[:-1]) * scale
                ingredients[key] = str(int(n_ingredient)) + value[-1:]

            elif value[-2:] == 'ml' and is_number(value[:-2]):
                n_ingredient = float(value[:-2]) * scale
                ingredients[key] = str(int(n_ingredient)) + value[-2:]

            else:
                if str(scale)[-1] == '0':
                    ingredients[key] = value + f'(x{(int(scale))})'
                else:
                    ingredients[key] = value + f'(x{float(round(scale, 1))})'

        elif len(valuelist) > 1:
            if is_number(valuelist[0]):
                n_ingredient = float(valuelist[0]) * scale
                n_ingredient = round(n_ingredient, 1)
                if str(n_ingredient)[-1] == '0':
                    n_ingredient = int(n_ingredient)  # remove .0
                valuelist[0] = str(n_ingredient)
                ingredients[key] = (' ').join(valuelist)

            else:
                if (str(scale))[-1] == 0:
                    ingredients[key] = value + f'(x{int(scale)})'
                else:
                    ingredients[key] = value + f'(x{round(scale, 1)})'
    return ingredients


def change_servings(meal_dict, recipename_dict, recipes):
    # edit servings of meal on shopping list
    newdict = {}
    print("\nWhich meal do you want to change the servings for?\n")
    i = 0
    for m, s in meal_dict.items():
        newdict[i] = m
        print(f"{i}: {recipename_dict[m]} ({s} servings)")
        i += 1
    meal_to_edit = input("\nPlease input corresponding number: ")
    new_servings = input("\nNew serving size: ")
    meal_dict[newdict[int(meal_to_edit)]] = new_servings
    print(
        f"\n{(recipename_dict[newdict[int(meal_to_edit)]])} changed to {new_servings} servings\n")

    return meal_dict


def combine_amounts(ingredients):
    # combines all similar amounts from ingredient amounts (e.g. 100g, 50g; 1 tsp, 3 tsp) to create clean ingredients list
    for key, value in ingredients.items():
        comb_amount = []
        str_amount = []

        ingredients[key] = value + ','

        # change 'a handful' to '1 handful' for example
        regex_a = re.compile(r'a (?P<u> ?[a-zA-Z]*( [a-zA-Z]*)?)(,|$)')
        a = regex_a.search(value)
        if a:
            for match in regex_a.finditer(value):
                value = '1' + match.group('u')

        regex = re.compile(
            r'(?P<n>\d+|\d+\.\d+)(?P<u> ?[a-zA-Z]*( [a-zA-Z]*)?)(,|$)')
        i = 0
        u = regex.search(value)
        unit_list = []
        num_list = []
        if u:
            for match in regex.finditer(value):
                unit_list.append(match.group('u'))
            #print(f"raw unit list: {unit_list}")

            plural_dict = {'tins': 'tin',
                           'cans': 'can',
                           'cups': 'cup',
                           'pinches': 'pinch',
                           'handfuls': 'handful',
                           'sprigs': 'sprig',
                           'bunches': 'bunch',
                           'stalks': 'stalk',
                           'florets': 'floret',
                           'cloves': 'clove',
                           'bulbs': 'bulb'}

            def convert_plurals(unit, conversion):
                def translate(match):
                    word = match.group(0)
                    if word in conversion:
                        return conversion[word]
                    return word

                return re.sub(r'\w+', translate, unit)

            new_unit_list = []
            for unit in unit_list:
                newunit = convert_plurals(unit, plural_dict)
                new_unit_list.append(newunit)

            unit_list = new_unit_list
            

            unit_list = list(dict.fromkeys(unit_list))

            for unit in unit_list:
                amountslist = []
                if unit == '':
                    regex_num = re.compile(r'(\d+|\d+\.\d+)(,|$)')
                    for n in regex_num.findall(value):
                        n_amount = (list(n))[0]

                        amountslist.append(float(n_amount))

                    amount = sum(amountslist)
                    s_amount = str(amount)
                    if s_amount[-2:] == '.0':
                        amount = int(amount)
                    else:
                        amount = float(amount)
                    comb_amount.append(amount)

                else:
                    amountslist = []
                    regex2 = re.compile(fr'(\d+|\d+\.\d+)({unit})')
                    for n in regex2.findall(value):
                        n_amount = (list(n))[0]

                        amountslist.append(float(n_amount))
                    amount = sum(amountslist)
                    s_amount = str(amount)
                    if s_amount[-2:] == '.0':
                        amount = int(amount)
                    else:
                        amount = float(amount)

                    amount_unit = str(amount) + unit
                    comb_amount.append(amount_unit)

            

        x = value.split(", ")
        for x in x:
            if x[0].isalpha():
                str_amount.append(x)

        

        comb_amount = [str(a) for a in comb_amount]
        full_amount = comb_amount + str_amount
        ingredients[key] = ', '.join(full_amount)

    uppercase_ingredients = dict((key[0].upper() + key[1:], value) for key, value in ingredients.items() )
    ingredients = uppercase_ingredients


    return ingredients


def shopping_list(all_meals, selected_meals):
    
    ingredients = {}

    for m, s in selected_meals.items():
        for meal in all_meals:
            if m == meal[0]:
                recipe_ingredients = meal[2]
                ingredient_adjust(int(meal[1]), int(s), recipe_ingredients)
                # print(ingredients)

                

        # check if ingredient already somewhere in main ingredients dictionary - if so append to existing key
        for key, value in recipe_ingredients.items():
            if key in ingredients:
                ingredients[key] = ingredients[key] + ", " + value
            else:
                ingredients[key] = value

    
    ingredients = {key.lower(): value for key, value in ingredients.items()}

    # print(f"Ingredients dict: {ingredients}")

    # clean up combined ingredients list - combine amounts together for each ingredient
    ingredients = combine_amounts(ingredients)

    # save ingredients dictionary as data frame and export to CSV

    ingredients_data = DataFrame(list(sorted(ingredients.items())), columns=["Ingredient", "Amount"])

    # print("All finished! Here's your shopping list:")
    # print(ingredients_data)

    return ingredients_data