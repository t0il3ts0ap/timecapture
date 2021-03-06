import json,calendar
from datetime import datetime
from django.shortcuts import render
from django.contrib import admin,messages
from django.http import HttpResponse
from django.db.models import Sum,Count
from django.contrib.admin.views.decorators import staff_member_required
from timesheet.models import TsheetEntry,Client,JobType
from timecapture.models import TimeUser
from timesheet import rendertsheet
from timecapture.commons import get_number_of_weekdays
from .forms import MetricInputForm,OldsheetInputForm,LeaveRegisterInputForm,HourlyMetricInputForm

@staff_member_required
def index(request):
    form = MetricInputForm(request.GET or None)
    if form.is_valid():
        query_results1 = []
        query_results2 = []
        total_hours_and_cost = ()
        total_hours = total_hours2 = total_cost = 0
        query_bool = False
        startdate = form.cleaned_data['startdate']
        enddate = form.cleaned_data['enddate']
        client = form.cleaned_data['client']
        jobtypes = form.cleaned_data['jobtype']
        users = form.cleaned_data['e']
        
        queried_jobtypes_list = list(map(lambda x: x.name,jobtypes))
        queried_users_list = list(map(lambda x: x.id,users))
        
        total_users_dict = dict((obj.id,obj) for obj in TimeUser.objects.filter(is_active=True))

        queryset = TsheetEntry.objects.filter(date__range=(startdate.strftime('%Y-%m-%d 00:00:00'),enddate.strftime('%Y-%m-%d 23:59:59'))) \
                                      .filter(client=client.name) \
                                      .filter(jobtype__in=queried_jobtypes_list) \
                                      .filter(employee__in=queried_users_list)

        queryset1 = queryset.values('employee').annotate(Sum('hours'))
        for query_item in queryset1:
            cost_per_hr = total_users_dict[query_item['employee']].cost_per_hr
            cost_per_employee = query_item['hours__sum']*cost_per_hr
            query_results1.append((str(total_users_dict[query_item['employee']]),query_item['hours__sum'],cost_per_hr,cost_per_employee)) 
            total_hours += query_item['hours__sum']
            total_cost += cost_per_employee

        queryset2 = queryset.values('jobtype').annotate(Sum('hours')) 
        for query_item in queryset2:
            query_results2.append((query_item['jobtype'],query_item['hours__sum']))
            total_hours2 += int(query_item['hours__sum'])
        query_bool = True

        total_hours_and_cost = (total_hours,total_cost,total_hours2)

        return render(request,'timemetric/metric.html', {
                    'title':'Analytics', 'has_permission':True, 'site_title':admin.site.site_title,
                    'site_header':admin.site.site_header, 'form':form,'query_results1':query_results1,
                    'query_results2':query_results2, 'query_bool':query_bool,
                    'total_hours_and_cost':total_hours_and_cost, 'client':client,
                    'startdate':startdate, 'enddate':enddate})

    return render(request,'timemetric/metric.html', {
                'title':'Analytics', 'has_permission':True,
                'site_title':admin.site.site_title, 'site_header':admin.site.site_header,
                'form':form})


@staff_member_required
def oldsheet(request):
    form = OldsheetInputForm(request.GET or None)
    get_success = False
    user_n_date = ()
    other_errors = ''
    success_msg = ''
    if form.is_valid():
        print(request.GET)
        user_id = form.cleaned_data['employee']
        date = form.cleaned_data['date']
        if '_save' in request.GET:
            get_success = True
            user_n_date = (user_id.id,date.strftime('%Y-%m-%d'))

        elif '_insert_leave' in request.GET:
            if date.weekday() > 4:
                other_errors = 'Cannot mark a leave on a weekend'
            else:
                query_res = TsheetEntry.objects.filter(date__range=(date.strftime('%Y-%m-%d 00:00:00'),date.strftime('%Y-%m-%d 23:59:59')))\
                                               .filter(employee=user_id.id) 
                if query_res:
                    other_errors = 'There are already some entries for %s on %s' % (user_id,date.strftime('%Y-%m-%d'))
                else:
                    tsheet_obj = TsheetEntry(date=date.strftime('%Y-%m-%d 00:00:00'),
                                             starthr=rendertsheet.DAY_START,
                                             hours=rendertsheet.HOURS_PER_LEAVE,
                                             client=Client.objects.get(pk=1).name,
                                             jobtype=JobType.objects.get(pk=1).name,
                                             employee=user_id.id)
                    tsheet_obj.save()
                    success_msg = 'Success! You have marked leave for %s on %s' % (user_id,date.strftime('%Y-%m-%d'))
                    messages.success(request,success_msg)
    return render(request,'timemetric/oldsheets.html',{
                'title':'Filled Sheets', 'has_permission':True,
                'site_title':admin.site.site_title, 'site_header':admin.site.site_header,
                'form':form, 'get_success':get_success, 'user_n_date':user_n_date,
                'other_errors':other_errors})


@staff_member_required
def render_leave_register(request):
    form = LeaveRegisterInputForm(request.GET or None)
    queryset = None
    user_dict = {}
    msg = ''
    if form.is_valid():
        startdate = form.cleaned_data['startdate']
        enddate = form.cleaned_data['enddate']
        user_list = []
        for user in TimeUser.objects.filter(is_active=True):
            user_dict[user.id] = str(user)
            user_list.append(user.id)
        queryset = TsheetEntry.objects.filter(date__range=(startdate.strftime('%Y-%m-%d 00:00:00'),enddate.strftime('%Y-%m-%d 23:59:59'))) \
                                      .filter(client=Client.objects.get(pk=1).name) \
                                      .filter(jobtype=JobType.objects.get(pk=1).name) \
                                      .filter(hours=rendertsheet.HOURS_PER_LEAVE) \
                                      .filter(employee__in=user_list) \
                                      .values('employee') \
                                      .annotate(Count('id'))                
        return render(request,'timemetric/leaves.html', {   
                    'title':'Leave Register', 'has_permission':True,
                    'site_title':admin.site.site_title, 'site_header':admin.site.site_header,
                    'form':form, 'queryset':queryset, 'user_dict':user_dict,'startdate':startdate,'enddate':enddate})
    return render(request,'timemetric/leaves.html', {   
                'title':'Leave Register', 'has_permission':True,
                'site_title':admin.site.site_title, 'site_header':admin.site.site_header, 'form':form})


@staff_member_required
def render_hourly_metric(request):
    form = HourlyMetricInputForm(request.GET or None)
    if form.is_valid():
        startdate = form.cleaned_data['startdate']
        enddate = form.cleaned_data['enddate']
        users = form.cleaned_data['e']
        queried_users_list = list(map(lambda x: x.id,users))
        queryset = TsheetEntry.objects.filter(date__range=(startdate.strftime('%Y-%m-%d 00:00:00'),enddate.strftime('%Y-%m-%d 23:59:59'))) \
                                      .filter(employee__in=queried_users_list).values('employee').annotate(Sum('hours'))

        total_users_dict = dict((obj.id,obj) for obj in TimeUser.objects.filter(is_active=True))
        total_work_hrs = get_number_of_weekdays(startdate,enddate) * rendertsheet.HOURS_PER_LEAVE
        return render(request,'timemetric/hourly_metric.html', {
            'title':'Hourly Metric', 'has_permission':True, 'site_title':admin.site.site_title,
            'site_header':admin.site.site_header, 'form':form, 
            'total_users_dict':total_users_dict, 'queryset':queryset,
            'startdate':startdate,'enddate':enddate,'total_work_hrs':total_work_hrs})
    return render(request,'timemetric/hourly_metric.html', {
        'title':'Hourly Metric', 'has_permission':True, 'site_title':admin.site.site_title,
        'site_header':admin.site.site_header, 'form':form, })


@staff_member_required
def render_oldsheet(request,uid,dt):
    dt = datetime.strptime(dt,'%Y-%m-%d')
    return rendertsheet.render_monthly_timesheet(request,uid,dt,'timesheet/monthly.html')

