from django import forms 
from django.core.validators import MinValueValidator,MaxValueValidator

from .models import Category,Balance

class BalanceForm(forms.ModelForm):

    class Meta:
        model   = Balance
        fields  = [ "category","pay_date","value","user" ]

class CategoryForm(forms.ModelForm):

    class Meta:
        model   = Category
        fields  = [ "name","income","user" ]
        error_messages = { 
            'comment': {
                'max_length': "これで実現できます",
                'required': "文字列入力してください",
            },
        }


#モデルを継承しないフォームクラス
class YearMonthForm(forms.Form):
    year    = forms.IntegerField()
    month   = forms.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(12)])

