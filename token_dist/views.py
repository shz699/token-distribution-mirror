import json

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password

from tablib import Dataset

from users.models import EventPermission
from tokens.models import Event, Token, StudentList
from users.models import User
from .decorators import admin_access

# Create your views here.

def index(request):
    return render(request, "index.html")

@login_required
def dashboard(request):
    user = request.user
    if user.is_admin:
        all_users = User.objects.all().exclude(id = user.id)
        context = {
            "user": user,
            "all_users": all_users
        }
        return render(request, "dashboard_admin.html", context)
    else:
        permissions = EventPermission.objects.filter(user=user).order_by("id")
        up_events = list()
        prev_events = list()
        for permission in permissions:
            end_date = permission.event.event_date
            current_date = now()
            end_date = int(end_date.strftime('%Y%m%d%H%M'))
            current_date = int(current_date.strftime('%Y%m%d%H%M'))
            if end_date - current_date > 0:
                up_events.append(permission.event)
            else:
                prev_events.append(permission.event)   

        context = {
            'user': user,
            'up_events': up_events,
            'prev_events': prev_events
        }
        return render(request, "dashboard_executive.html", context)
    
@login_required
def account_settings(request):
    user = request.user
    context = {
        'user': user
    }
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        userEdit = User.objects.get(id=user.id);
        userEdit.name = name
        userEdit.phone = phone
        userEdit.email = email
        userEdit.save()
        context['success'] = "Account Updated Successfully"
        context['user'] = userEdit
    return render(request, "account_settings.html", context)

@login_required
def update_password(request):
    user = request.user
    context = {
        'user': user
    }
    if request.method == "POST":
        prev_pass = request.POST.get("prevpass")
        new_pass = request.POST.get("newpass")
        userEdit = User.objects.get(id=user.id);
        if user.check_password(prev_pass):
            userEdit.password = make_password(new_pass)
            userEdit.save()
            context['success_pass'] = "Password Updated Successfully"
        else:
            print("Not matched") 
            context['error'] = "Passwords do not match"
    return render(request, "account_settings.html", context)

@admin_access
def delete_user(request):
    user = request.user
    all_users = User.objects.all().exclude(id = user.id)
    context = {
        "user": user,
        "all_users": all_users
    }
    if request.method == "POST":    
        user_id = request.POST.get("id")
        try:
            userDelete = User.objects.get(id = user_id)    
            context['user_deleted'] = userDelete.username + " Deleted Successfully"
            userDelete.delete()
        except:
            return redirect("dashboard")
        all_users = User.objects.all().exclude(id = user.id)
        context['all_users'] = all_users
    return render(request, "dashboard_admin.html", context)

def events(request):
    events = Event.objects.all()
    up_events = []
    prev_events = []
    for event in events:
        end_date = event.event_date
        current_date = now()
        end_date = int(end_date.strftime('%Y%m%d%H%M'))
        current_date = int(current_date.strftime('%Y%m%d%H%M'))
        if end_date - current_date > 0:
            up_events.append(event)
        else:
            prev_events.append(event)
    context = {
        'up_events': up_events,
        'prev_events': prev_events
    }
    return render(request, "events.html", context)

def event(request, pk):
    user = request.user
    event = Event.objects.get(id=pk)
    token_status = "Token distribution has not started yet. Stay Tuned"

    current_date = now()
    current_date = int(current_date.strftime('%Y%m%d%H%M'))
    
    end_event = event.event_date
    end_event = int(end_event.strftime('%Y%m%d%H%M'))
    if current_date > end_event:
        token_status = "Event Finished. Thanks for your co-operation"
    else:
        try:
            start_date = event.token_dist_start
            end_date = event.token_dist_end
            place = event.distribution_place

            start_date = int(start_date.strftime('%Y%m%d%H%M'))
            end_date = int(end_date.strftime('%Y%m%d%H%M'))
            

            if current_date >= start_date and current_date <= end_date:
                token_status = "Token distribution started. Collect the token from " + place
            elif current_date < start_date:
                pass
            elif current_date > end_date:
                token_status = "Token distribution finished. Enjoy the event"
        except:
            pass
    # Common context
    context = {
            "event": event,
            "token_status": token_status
        }
    
    if user.is_authenticated:
        if user.is_admin:
            # tags = Tag.objects.all()
            users = User.objects.all().exclude(is_admin=True)
            epall = EventPermission.objects.filter(event=event)
            stu_list = StudentList.objects.filter(event = event).count()
            # context["tags"] = tags
            context["users"] = users
            context["epall"] = epall
            context["stu_list"] = stu_list
            return render(request, "event_admin.html", context)
        else:
            try:
                ep = EventPermission.objects.get(user=user,event=event)
                epall = EventPermission.objects.filter(event=event).exclude(user=user)
                context["user"] = user
                context["epall"] = epall
            except:
                return render(request, "event.html", context)
            return render(request, "event_executive.html", context)
    else:
        return render(request, "event.html", context)

@admin_access
def event_stulist(request, pk):
    event = Event.objects.get(id = pk)
    stu_list = StudentList.objects.filter(event = event).count()
    status = False
    msg = ""
    type = ""
    context = {
        "event":event,
        "stu_list":stu_list,
    }
    
    if request.method == "POST":
        event = Event.objects.get(id = pk)
        dataset = Dataset()
        new_record = request.FILES.get("student_list")
   
        if not new_record.name.endswith('xlsx'):
            status = True
            msg = "Wrong file format."
            type = "danger"
            context["status"] = status
            context["msg"] = msg
            context["type"] = type
            return render(request, "event_studentlist.html",context)
        
        if(stu_list > 0):
            StudentList.objects.filter(event = event).delete()
        
        data = dataset.load(new_record.read(),format="xlsx")
        bulk_list = list()
        for datum in data:
            bulk_list.append(
                StudentList(student_id=datum[1],name = datum[2],event = event)
            )
        StudentList.objects.bulk_create(bulk_list)

        status = True
        msg = "Student list submitted successfully."
        type = "success"
        context["status"] = status
        context["msg"] = msg
        context["type"] = type
    return render(request, "event_studentlist.html",context)

@admin_access
def event_update(request):
    if request.method == "POST":
        pk = request.POST.get('pk')
        name = request.POST.get('name')
        place = request.POST.get('place')
        date = request.POST.get('date')
        time = request.POST.get('time')
        token_start_date = request.POST.get('token_start_date')
        token_start_time = request.POST.get('token_start_time')
        token_end_date = request.POST.get('token_end_date')
        token_end_time = request.POST.get('token_end_time')
        desc = request.POST.get('desc')
        usage = request.POST.get('usage')
        
        event = Event.objects.get(id = pk)
        
        if time != "":
            time = date+" "+time+":00.000000"
            event.event_date = time
        if token_start_date != "":
            token_start_time = token_start_date+" "+token_start_time+":00.000000"
            event.token_dist_start = token_start_time
        if token_end_time != "":
            token_end_time = token_end_date+" "+token_end_time+":00.000000"
            event.token_dist_end = token_end_time

        
        if int(usage) != int(event.token_usage):
            if int(usage) > 1:
                Token.objects.filter(event=event).update(
                    entry_flag = True,
                    food_flag = True
                )
                event.token_usage = usage
            elif int(usage) == 1:
                Token.objects.filter(event=event).update(
                    entry_flag = False,
                    food_flag = True
                )
            event.token_usage = usage

        executives = request.POST.getlist('users')
        if executives != 'None':    
            EventPermission.objects.filter(event=event).delete()
            for executive in executives:
                user = User.objects.get(id=executive)
                EventPermission.objects.create(
                    event = event,
                    user = user
                )

        event.name = name
        event.distribution_place = place
        event.desc = desc

        event.save()

    return redirect(f'/event/{pk}')

@admin_access
def delete_event(request):
    if request.method == "POST":
        data = json.loads(request.body)
        id = data['event_id']
        Event.objects.get(id=id).delete()
    return JsonResponse({"msg":"Deleted"},safe=False)

@admin_access
def create_user(request):
    return render(request, "create_user.html")

@admin_access
def create_event(request):
    if request.method == "POST":
        name = request.POST.get('name')
        place = request.POST.get('place')
        date = request.POST.get('date')
        time = request.POST.get('time')
        token_start_date = request.POST.get('token_start_date')
        token_start_time = request.POST.get('token_start_time')
        token_end_date = request.POST.get('token_end_date')
        token_end_time = request.POST.get('token_end_time')
        desc = request.POST.get('desc')
        usage = request.POST.get('usage')


        time = date+" "+time+":00.000000"
        token_start_time = token_start_date+" "+token_start_time+":00.000000"
        token_end_time = token_end_date+" "+token_end_time+":00.000000"

        Event.objects.create(
            name = name,
            event_date = time,
            token_dist_start = token_start_time,
            token_dist_end = token_end_time,
            token_usage = usage,
            distribution_place = place,
            desc = desc
        )
        return redirect("dashboard")
    return render(request, "create_event.html")

@admin_access
def create_user_post(request):
    if request.method == "POST":
        data = json.loads(request.body)
        name = data['name']
        username = data['username']
        phone = data['phone']
        email = data['email']
        password = data['password']
        adm = data['adm']
        if adm:
            User.objects.create(
                name = name,
                phone = phone,
                username = username,
                email = email,
                password = make_password(password),
                is_admin = True,
                is_executive = False
            )
        else:
            User.objects.create(
                name = name,
                phone = phone,
                username = username,
                email = email,
                password = make_password(password),
            )
    return JsonResponse({"msg":"Done"},safe=False)


def handle_page_not_found(request, exception):
    msg = "404 - Requested page not found."
    context = {
        "msg":  msg
    }
    return render(request, "error.html", context)

def handle_server_error(request):
    msg = "500 - Internal Server Error."
    context = {
        "msg" : msg
    }
    return render(request, "error.html", context)

def handle_bad_request(request, exception):
    msg = "400 - Bad Request."
    context = {
        "msg" : msg
    }
    return render(request, "error.html", context)
