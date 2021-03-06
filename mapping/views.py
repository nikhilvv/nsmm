from django.http import JsonResponse
from django.shortcuts import render, HttpResponseRedirect
from django.contrib import auth
from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from mapping.forms import CountryForm, DepartmentForm, TaskForm, SubtaskForm, DescriptionForm, UserForm, UserEditForm
from mapping.models import Country, CustomUser, Department, Task, Subtask, Description
from mapping.filters import DescriptionFilter

# Create your views here.

def home(request):
    return render(request,'mapping/home.html',{'title':'HOME'})

def login(request):
    # if user is logged in then redirect to the dashboard
    if request.user.is_authenticated():
        return HttpResponseRedirect('/department')

    if request.method == "POST":
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            # Login the user
            auth.login(request, user)
            return JsonResponse({'message': 'Login Successful'}, status=200)
        else:
            return JsonResponse({'message': 'Invalid Username/Password'}, status=500)
    return render(request, 'mapping/login.html')

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/login')

def department(request):
    departments = Department.objects.all().order_by('name')
    d = Department()
    tasks = Task.objects.all().order_by('name')
    t = Task()
    # total_depts = sum(0 == 0 for department in departments)
    # total_tasks = sum(0 == 0 for task in tasks)
    return render(request,'mapping/departments.html',{'departments': departments, 'title':'DEPARTMENTS', 'tasks': tasks})

def tasks(request, department=None, task=None):
    departments = Department.objects.all().order_by('name')
    tasks = Task.objects.all().order_by('name')
    subtasks = Subtask.objects.filter(task=task).order_by('name')
    title = Task.objects.get(id=task).name
    return render(request,'mapping/viewtask.html',{'subtasks': subtasks ,'title': title ,'departments': departments, 'tasks': tasks})

def subtasks(request, department=None, task=None, subtask=None):
    departments = Department.objects.all().order_by('name')
    tasks = Task.objects.all().order_by('name')
    subtasks = Subtask.objects.filter(task=task).order_by('name')
    title = Task.objects.get(id=task).name
    try:
        description = Description.objects.get(subtask=subtask, country=request.user.country)
        date_created = description.created_at.year
        date_today = date.today().year
        if date_today != date_created:
            description = None
    except Description.DoesNotExist:
        description = None
    if request.method == "POST":
        if description:
            form = DescriptionForm(request.POST, instance=description)
        else:
            form = DescriptionForm(request.POST)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.subtask = Subtask.objects.get(id=subtask)
            instance.user = request.user
            instance.country = request.user.country
            instance.save()
            dest_url = '/department/{0}/task/{1}/subtask/{2}'.format(department, task, subtask)
            return HttpResponseRedirect(dest_url, {'success': 'Task Added', 'subtasks': subtasks ,'title': title, 'departments': departments, 'tasks': tasks , 'form': form})
        else:
            return render(request, 'mapping/viewsubtask.html', {'form': form, 'title': 'Task'})
    else:
        if description:
            form = DescriptionForm(instance=description)
        else:
            form = DescriptionForm()
        return render(request,'mapping/viewsubtask.html',{'subtasks': subtasks ,'title': title ,'departments': departments, 'tasks': tasks , 'form':form })

def listdepartment(request):
    departments = Department.objects.all().order_by('name')
    return render(request, 'mapping/department_list.html', {'departments': departments})

def newdepartment(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/admin/department', {'success': 'Department Added'})
        else:
            return render(request,'mapping/newdepartment.html', {'title': 'Department', 'form': form})
    else:
        form = DepartmentForm()
        return render(request,'mapping/newdepartment.html', {'title': 'Department', 'form': form})

def editdepartment(request, id=None):
    department = Department.objects.get(id=id)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/admin/department', {'success': 'Department edited'})
        else:
            return render(request,'mapping/newdepartment.html', {'title': 'Department', 'form': form})
    else:
        form = DepartmentForm(instance=department)
        return render(request,'mapping/newdepartment.html', {'title': 'Department', 'form': form})

def listtask(request,id=None):
    tasks = Task.objects.filter(department=id)
    return render(request, 'mapping/task_list.html', {'tasks': tasks, 'department_id':id})

def newtask(request,id=None):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.department = Department.objects.get(id=id)
            instance.save()
            return HttpResponseRedirect('/admin/department/{0}/task'.format(id), {'success': 'Task Added'})
        else:
            return render(request,'mapping/newtask.html',{'title':'NEW TASK ', 'department_id': id, 'tasks': tasks , 'form' : form})

    else:
        form = TaskForm()
        return render(request,'mapping/newtask.html',{ 'title':'NEW TASK ','department_id': id ,'tasks': tasks , 'form' : form})

def edittask(request, department=None,task=None):
    tasks = Task.objects.get(id=task)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=tasks)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/admin/department/{0}/task'.format(department), {'success': 'Task edited'})
        else:
            return render(request,'mapping/edittask.html', {'title': 'Department', 'form': form, 'department_id': department ,'task_id' : task })
    else:
        form = TaskForm(instance=tasks)
        return render(request,'mapping/edittask.html', {'title': 'Department', 'form': form , 'department_id': department,'task_id' : task })

def newsubtask(request):
    departments = Department.objects.all().order_by('name')
    tasks = Task.objects.all().order_by('name')
    if request.method == "POST":
        form = SubtaskForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/newsubtask', {'success': 'Subtask Added'})
        else:
            return render(request,'mapping/newsubtask.html',{'departments': departments, 'title':'NEW SUBTASK ', 'tasks': tasks , 'form' : form})

    else:
        form = SubtaskForm()
        return render(request,'mapping/newsubtask.html',{'departments': departments, 'title':'NEW SUBTASK ', 'tasks': tasks , 'form' : form})

def filter(request):
    f = DescriptionFilter(request.POST, queryset=Description.objects.all())
    if request.method == 'POST':
        countries = [c.name for c in Country.objects.filter(pk__in=request.POST.getlist('country'))]
        subtasks = [s.name for s in Subtask.objects.filter(pk__in=request.POST.getlist('subtask'))]

        descriptions = {}
        c = 0
        for obj in f:
            if obj.country.name in descriptions:
                descriptions[obj.country.name][obj.subtask.name] = [obj.description, obj.status]
            else:
                descriptions[obj.country.name] = {obj.subtask.name: [obj.description, obj.status]}
            c += 1

        return render(request, 'mapping/print.html', {'descriptions': descriptions, 'countries': countries, 'subtasks': subtasks})
    return render(request, 'mapping/filter.html', {'filter': f, 'title': 'Filter'})

def user(request):
    u = CustomUser.objects.all().order_by('country')
    return render(request, 'mapping/user_list.html', {'title': 'Users', 'users': u})

def newuser(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/user')
        else:
            return render(request, 'mapping/newuser.html', {'title': 'User', 'form': form})
    else:
        form = UserForm()
        return render(request, 'mapping/newuser.html', {'title': 'User', 'form': form})

def edituser(request, id=None):
    user = CustomUser.objects.get(id=id)
    if request.method == "POST":
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/user', {'success': 'User Updated'})
        else:
            return render(request, 'mapping/edituser.html', {'id': user.id, 'form': form, 'title': 'Users'})
    else:
        form = UserEditForm(instance=user)
        return render(request,'mapping/edituser.html', {'id': user.id, 'form': form, 'title': 'Users'})
