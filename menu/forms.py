from .models import Category, FoodItem
from django import forms
from accounts.validators import allow_only_images_validator

class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields=['category_name','description',]


class FoodItemForm(forms.ModelForm):
    image = forms.FileField(validators=[allow_only_images_validator])

    class Meta:
        model = FoodItem
        fields=['category','food_title','description','image','price','is_available',]
