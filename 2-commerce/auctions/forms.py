from django.core.exceptions import ValidationError
from django.forms import widgets
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple, TextInput
from .models import Auction, Category, Comment, Bid
from django.forms import ModelForm, Textarea
from django.forms.utils import ErrorList


class MyCheckboxSelectMultiple(CheckboxSelectMultiple):
    
    pass


class DivErrorList(ErrorList):
    def __str__(self):
        return self.as_divs()

    def as_divs(self):
        if not self:
            return ''
        return '<div class="errorlist">%s</div>' % ''.join(['<div class="alert alert-danger" role="alert">%s</div>' % e for e in self])


class AuctionForm(ModelForm):
    class Meta:
        model = Auction
        fields = [
            'categories', 
            'description',
            'image_url',
            'title', 
        ]
        widgets = {
            'description': Textarea(attrs={'cols': 40, 'rows': 3}), 
            'categories': CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super(AuctionForm, self).__init__(*args, **kwargs)
        self.fields['categories'].queryset = Category.objects.order_by(
            'category')
        
        
class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']
            

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
        labels = {
            'comment': ''
        }
        widgets = {
            'comment': Textarea(attrs={'placeholder': 'Write a comment...',
                                       'rows': 1,
                                       'cols': 40})
        }
        
