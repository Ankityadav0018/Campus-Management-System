from django.shortcuts import render

def make_up_class_home(request):
    return render(request, 'make_up_class/make_up_class_home.html')
