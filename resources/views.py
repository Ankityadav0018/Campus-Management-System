from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Block, Classroom, Event, ClassroomSchedule
from .forms import EventForm
from datetime import datetime, timedelta

def resources_home(request):
    return render(request, 'resources/resources_home.html')

def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()
            messages.success(request, f'Event "{event.name}" added successfully!')
            return redirect('resources_home')
    else:
        form = EventForm()
    return render(request, 'resources/add_event.html', {'form': form})

def suggest_classrooms(request):
    suggested_classrooms = []
    if request.method == 'POST':
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')
        capacity_needed = request.POST.get('capacity_needed', 0)

        try:
            start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
            end_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M')
            capacity_needed = int(capacity_needed)
        except (ValueError, TypeError):
            messages.error(request, 'Invalid date/time or capacity input.')
            return render(request, 'resources/suggest_classrooms.html')

        if start_time >= end_time:
            messages.error(request, 'End time must be after start time.')
            return render(request, 'resources/suggest_classrooms.html')

        all_classrooms = Classroom.objects.filter(capacity__gte=capacity_needed)
        available_classrooms = []

        for classroom in all_classrooms:
            # Check for any overlapping events for this classroom
            overlapping_schedules = ClassroomSchedule.objects.filter(
                classroom=classroom,
                event__start_time__lt=end_time,
                event__end_time__gt=start_time
            ).exists()

            if not overlapping_schedules:
                available_classrooms.append(classroom)
        
        if available_classrooms:
            suggested_classrooms = available_classrooms
            messages.success(request, 'Available classrooms found!')
        else:
            messages.info(request, 'No classrooms available for the selected time and capacity.')

    return render(request, 'resources/suggest_classrooms.html', {'suggested_classrooms': suggested_classrooms})
