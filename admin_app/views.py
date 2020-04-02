from django.shortcuts import render,redirect
from .forms import EmployeeForm
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse

def createEmployee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            ## backend code goes here
            messages.success(request, f'New account created')
            return redirect(settings.BASE_URL+'/user_home/home')
        else:
            messages.error(request, f'Failed to create account')
            return redirect(settings.BASE_URL+'/user_home/home')
    else:
        form = EmployeeForm()
        return render(request, 'create_emp_account.html', {'form': form})

def modifyEmployee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            ## backend code goes here
            messages.success(request, f'Account modified successfully')
            return redirect(settings.BASE_URL+'/user_home/home')
        else:
            messages.error(request, f'Failed to modify account')
            return redirect(settings.BASE_URL+'/user_home/home')
    else:
        form = EmployeeForm()
        return render(request, 'modify_emp_account.html', {'form': form})

def deleteEmployee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            ## backend code goes here
            messages.success(request, f'Account deleted successfully')
            return redirect(settings.BASE_URL+'/user_home/home')
        else:
            messages.error(request, f'Failed to delete account')
            return redirect(settings.BASE_URL+'/user_home/home')
    else:
        form = EmployeeForm()
        return render(request, 'close_emp_account.html', {'form': form})

def searchEmployee(request):
    searchString = request.POST['employeeSearchString']

    #backend code to search empolyee
    #Employee form must be populated with the data from db
    form = EmployeeForm()
    if request.POST['context_page']=='modify_employee':
        return render(request, 'modify_emp_account.html', {'form': form})
    elif request.POST['context_page']=='delete_employee':
        return render(request, 'close_emp_account.html', {'form': form})

    return render(request, 'view_employee.html')

def systemLog(request):
    filename = 'system_log.log'
    with open(filename, 'rb') as log:
        response = HttpResponse(log, content_type='text/plain')
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        return response
