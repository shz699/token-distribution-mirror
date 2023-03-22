import math
import json

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required

from token_dist.decorators import admin_access
from .models import Token, Event, StudentList

# Create your views here.
@admin_access
def token(request, pk):
    event = Event.objects.get(id=pk)

    end_event = event.event_date
    end_event = int(end_event.strftime('%Y%m%d%H%M'))

    current_date = now()
    current_date = int(current_date.strftime('%Y%m%d%H%M'))

    if current_date > end_event:
        return HttpResponse("This event has already finished. To generate tokens please consider changing event date from event management page. Thanks.")
    context = {
        "event": event,
    }
    return render(request, "tokens.html", context)

@admin_access
def print_token(request, num, pk):
    event = Event.objects.get(id=pk)
    count = event.get_tokens_non_printed_count
    if num > count:
        num = count
    tokens = event.token_set.filter(is_printed=False)[:num]
    token_index = []

    total_pgs = math.ceil(num/10)


    try:
        st = int(tokens[0].token_serial[8:])
        last_ck = int(tokens[num-1].token_serial[8:])
        start_token = int(tokens[0].token_serial[8:])
        end_token = int(tokens[num-1].token_serial[8:])
        first_token_id = tokens[0].id
    except:
        first_token_id = 0
        st = 0
        last_ck = 0
        start_token = 0
        end_token = 0

    if total_pgs <= 17:
        meta_pg = 1
    elif total_pgs <= 43:
        meta_pg = 2
    elif total_pgs > 43:
        meta_pg = 3

    for i in range(total_pgs):
        if st + 9 <= last_ck:
            ft = st + 9
        else:
            ft = (last_ck - st) + st
        token_index.append({"page":(i+1+meta_pg),"starting_token":st,"finish_token": ft,"count":(ft-st)+1})
        st = ft + 1
    
    dt = now()

    context = {
        "num": num,
        "event": event,
        "tokens": tokens,
        "start_token": start_token,
        "end_token": end_token,
        "token_index": token_index,
        "total_pgs": total_pgs+meta_pg,
        "dt": dt,
        "first_token_id" : first_token_id
    }
    return render(request,"print_tokens.html",context)

@admin_access
def generate_tokens(request):
    if request.method == "POST":
        data = json.loads(request.body)
        num = data['num']
        event_id = data['event_id']
        event = Event.objects.get(id=event_id)

        bulk_list = list()

        check_existing_tokens= Token.objects.filter(event = event).order_by('-id')[:1]
        event_id_token = int(event_id) + 100
        tmp = 10000

        if len(check_existing_tokens) > 0:
            tmp = int(check_existing_tokens[0].token_serial[8:])

        num = int(num)
        if num > 300:
            num = 300

        # Token usage
        if(event.token_usage == 1):
            food_flag = True
            entry_flag = False
        if(event.token_usage == 2):
            food_flag = True
            entry_flag = True

        for i in range(num):
            tmp = tmp + 1
            token_sr = 'CSE-'+ str(event_id_token) + '-' + str(tmp)
            bulk_list.append(
                Token(event=event,token_serial = token_sr,food_flag =food_flag, entry_flag = entry_flag)
            )
        Token.objects.bulk_create(bulk_list)
    return JsonResponse({"msg":"Ok"}, safe=False)

@admin_access
def update_print_status(request):
    if request.method == "POST":
        data = json.loads(request.body)
        num = data['total_tokens']
        starting_token_id = data['s_token_id']
        ending_token_id = int(starting_token_id) + int(num)

        for i in range(int(starting_token_id),ending_token_id):
            token = Token.objects.get(id=i)
            token.is_printed = True
            token.save()

    return JsonResponse({"msg":"Done"}, safe=False)

@login_required
def scanner_dist(request, pk):
    event = Event.objects.get(id=pk)
    context = {
        "event": event
    }
    return render(request, "scanner_dist.html",context)

@login_required
def scanner_receive(request, pk):
    event = Event.objects.get(id=pk)
    context = {
        "event": event
    }
    return render(request, "scanner_receive.html",context)

@login_required
def token_activate(request):
    if request.method == "POST":
        data = json.loads(request.body)
        code = data['code']
        stu_id = data['stu_id']
        event_id = data['event_id']

        event = Event.objects.get(id = event_id)
        msg = "404"
        stu = ""
        try:
            stu = StudentList.objects.get(student_id = stu_id,event = event)
            if stu.claimed == True:
                msg = "303"
                return JsonResponse({"msg":msg}, safe=False)
        except:
            msg = "304"
            return JsonResponse({"msg":msg}, safe=False)
        try:
            # token = Token.objects.get(token_serial='CSE-101-10005',event=event,is_printed=True)
            token = Token.objects.get(token_serial=code,event=event,is_printed=True)
            if token.is_activated == True:
                msg = "403"
            else:
                msg = "200"
                token.student_id = stu_id
                token.is_activated = True
                token.save()
                stu.claimed = True
                stu.save()
            return JsonResponse({"msg":msg}, safe=False)
        except:
            return JsonResponse({"msg":msg}, safe=False)
    return JsonResponse({"msg":"No permission"}, safe=False)

@login_required
def token_activate_new(request):
    if request.method == "POST":
        data = json.loads(request.body)
        event_id = data['event_id']
        code = data['code']
        stu_id = data['stu_id']
        name = data['name']

        event = Event.objects.get(id = event_id)
        msg = "404"
        try:
            # token = Token.objects.get(token_serial="2051",event=event,is_printed=True)
            token = Token.objects.get(token_serial=code,event=event,is_printed=True)
            if token.is_activated == True:
                msg = "403"
            else:
                msg = "200"
                token.student_id = stu_id
                token.is_activated = True
                token.save()
                StudentList.objects.create(
                    name = name,
                    student_id = stu_id,
                    event = event,
                    claimed = True
                )
            return JsonResponse({"msg":msg}, safe=False)
        except:
            return JsonResponse({"msg":msg}, safe=False)
    return JsonResponse({"msg":"No permission"}, safe=False)
            
@login_required
def token_receive(request):
    if request.method == "POST":
        data = json.loads(request.body)
        code = data['code']
        event_id = data['event_id']
        tag = data['tag']
        msg = "404"
        event = Event.objects.get(id = event_id)
        try:
            token = Token.objects.get(token_serial=code,event=event,is_printed=True)
            # token = Token.objects.get(token_serial="CSE-101-10005",event=event,is_printed=True)
            if token.is_activated == False:
                msg = "403"
                return JsonResponse({"msg":msg}, safe=False)
            else:
                if int(tag) == 2:
                    if token.food_flag == False:
                        msg = "402"
                        return JsonResponse({"msg":msg}, safe=False)
                    else:
                        token.food_flag = False
                        msg = "202"
                        token.save()
                        return JsonResponse({"msg":msg}, safe=False)
                elif int(tag) == 1:
                    if token.entry_flag == False:
                        msg = "401"
                        return JsonResponse({"msg":msg}, safe=False)
                    else:
                        token.entry_flag = False
                        msg = "201"
                        token.save()
                        return JsonResponse({"msg":msg}, safe=False)
        except:
            return JsonResponse({"msg":msg}, safe=False)
    return JsonResponse({"msg":"No permission"}, safe=False)