from .models import Category, FoodItem
from django import forms

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields=['category_name','description',]
