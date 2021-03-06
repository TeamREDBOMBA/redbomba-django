# -*- coding: utf-8 -*-
 
from django import forms
import re
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
 
class RegistrationForm(forms.Form):
    username = forms.CharField(label='사용자 이름', max_length=30)
    email = forms.EmailField(label='이메일')
    password1 = forms.CharField(
        label='비밀번호',
        widget=forms.PasswordInput()
    )
    password2 = forms.CharField(
        label='비밀번호(확인용)',
        widget=forms.PasswordInput()
    )
     
    def clean_password2(self):
        if 'password1' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            password2 = self.cleaned_data['password2']
            if password1 == password2:
                return password2
        raise forms.ValidationError('비밀번호가 일치하지 않습니다.')
     
    def clean_username(self):
        username = self.cleaned_data['username']
        return username

class UploadFileForm(forms.Form):
    file = forms.FileField()