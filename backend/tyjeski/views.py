from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'index.html')

def portfolio_01(request):
    return render(request, 'portfolio-item-01.html')

def portfolio_02(request):
    return render(request, 'portfolio-item-02.html')

def portfolio_03(request):
    return render(request, 'portfolio-item-03.html')

def portfolio_04(request):
    return render(request, 'portfolio-item-04.html')