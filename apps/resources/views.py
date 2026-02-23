from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q, Exists, OuterRef
from django.db.models.functions import ExtractHour, ExtractWeekDay
from .models import Block, CampusClassroom, Event, ClassroomSchedule, CampusFaculty, Course
from .forms import EventForm, CampusClassroomForm, CourseForm, BlockForm
from datetime import datetime, timedelta

def resources_home(request):
    """OPTIMIZED: Fetch all counts in parallel"""
    total_blocks = Block.objects.count()
    total_classrooms = CampusClassroom.objects.count()
    total_courses = Course.objects.count()
    total_faculty = CampusFaculty.objects.count()
    total_events = Event.objects.filter(start_time__gte=datetime.now()).count()
    # Fixed: Event doesn't have a direct relationship with campus_classroom
    # Events are related to classrooms through ClassroomSchedule (many-to-many)
    recent_events = Event.objects.filter(start_time__gte=datetime.now()).order_by('start_time')[:5]
    
    context = {
        'total_blocks': total_blocks,
        'total_classrooms': total_classrooms,
        'total_courses': total_courses,
        'total_faculty': total_faculty,
        'total_events': total_events,
        'recent_events': recent_events,
    }
    return render(request, 'resources/resources_home.html', context)

def campus_classroom_list(request):
    """OPTIMIZED: Prefetch related block data"""
    classrooms = CampusClassroom.objects.select_related('block').all()
    return render(request, 'resources/campus_classroom_list.html', {'classrooms': classrooms})

def add_campus_classroom(request):
    if request.method == 'POST':
        form = CampusClassroomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campus Classroom added successfully!')
            return redirect('resources:campus_classroom_list')
    else:
        form = CampusClassroomForm()
    return render(request, 'resources/add_campus_classroom.html', {'form': form})

def edit_campus_classroom(request, pk):
    classroom = get_object_or_404(CampusClassroom, pk=pk)
    if request.method == 'POST':
        form = CampusClassroomForm(request.POST, instance=classroom)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campus Classroom updated successfully!')
            return redirect('resources:campus_classroom_list')
    else:
        form = CampusClassroomForm(instance=classroom)
    return render(request, 'resources/edit_campus_classroom.html', {'form': form})

def delete_campus_classroom(request, pk):
    classroom = get_object_or_404(CampusClassroom, pk=pk)
    if request.method == 'POST':
        classroom.delete()
        messages.success(request, 'Campus Classroom deleted successfully!')
        return redirect('resources:campus_classroom_list')
    return render(request, 'resources/confirm_delete.html', {'object': classroom})

def course_list(request):
    """OPTIMIZED: Prefetch related faculty data"""
    # Fixed: Use 'assigned_faculty' which is the correct field name in Course model
    courses = Course.objects.select_related('assigned_faculty').all()
    
    # Calculate statistics for the template
    total_courses = courses.count()
    assigned_courses = courses.filter(assigned_faculty__isnull=False).count()
    unassigned_courses = courses.filter(assigned_faculty__isnull=True).count()
    
    return render(request, 'resources/course_list.html', {
        'courses': courses,
        'total_courses': total_courses,
        'assigned_courses': assigned_courses,
        'unassigned_courses': unassigned_courses,
    })

def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course added successfully!')
            return redirect('resources:course_list')
    else:
        form = CourseForm()
    return render(request, 'resources/add_course.html', {'form': form})

def edit_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('resources:course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'resources/edit_course.html', {'form': form})

def delete_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully!')
        return redirect('resources:course_list')
    return render(request, 'resources/confirm_delete.html', {'object': course})

def event_list(request):
    """OPTIMIZED: Prefetch related classroom schedules"""
    # Fixed: Event doesn't have direct relation to campus_classroom
    # Use prefetch_related to get classroom schedules instead
    events = Event.objects.prefetch_related('classroom_schedules__classroom__block').order_by('-start_time')
    return render(request, 'resources/event_list.html', {'events': events})

def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()
            messages.success(request, f'Event "{event.name}" added successfully!')
            return redirect('resources:event_list') # Changed redirect to event_list
    else:
        form = EventForm()
    return render(request, 'resources/add_event.html', {'form': form})

def suggest_classrooms(request):
    """OPTIMIZED: Use subquery for availability check instead of N+1 queries"""
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
        
        # OPTIMIZED: Use database-level filtering with subquery
        overlapping_schedules = ClassroomSchedule.objects.filter(
            classroom=OuterRef('pk'),
            event__start_time__lt=end_time,
            event__end_time__gt=start_time
        )
        
        available_classrooms = CampusClassroom.objects.filter(
            capacity__gte=capacity_needed
        ).annotate(
            has_overlap=Exists(overlapping_schedules)
        ).filter(has_overlap=False).select_related('block')
        
        if available_classrooms:
            suggested_classrooms = available_classrooms
            messages.success(request, f'Found {len(available_classrooms)} available classrooms!')
        else:
            messages.info(request, 'No classrooms available for the selected time and capacity.')
    return render(request, 'resources/suggest_classrooms.html', {'suggested_classrooms': suggested_classrooms})

def faculty_list(request):
    """OPTIMIZED: Annotate with course count"""
    faculty = CampusFaculty.objects.annotate(course_count=Count('course')).order_by('name')
    return render(request, 'resources/faculty_list.html', {'faculty': faculty})

# ============================================
# BLOCK MANAGEMENT VIEWS
# ============================================

def block_list(request):
    """View all blocks/buildings"""
    blocks = Block.objects.annotate(
        classroom_count=Count('campusclassroom')
    ).order_by('name')
    
    # Calculate statistics
    total_blocks = blocks.count()
    total_classrooms = sum(block.classroom_count for block in blocks)
    avg_classrooms = total_classrooms / total_blocks if total_blocks > 0 else 0
    
    return render(request, 'resources/block_list.html', {
        'blocks': blocks,
        'total_blocks': total_blocks,
        'total_classrooms': total_classrooms,
        'avg_classrooms': avg_classrooms,
    })

def add_block(request):
    """Add new block/building"""
    if request.method == 'POST':
        form = BlockForm(request.POST)
        if form.is_valid():
            block = form.save()
            messages.success(request, f'Block "{block.name}" added successfully!')
            return redirect('resources:block_list')
    else:
        form = BlockForm()
    return render(request, 'resources/add_block.html', {'form': form})

def edit_block(request, pk):
    """Edit existing block"""
    block = get_object_or_404(Block, pk=pk)
    if request.method == 'POST':
        form = BlockForm(request.POST, instance=block)
        if form.is_valid():
            form.save()
            messages.success(request, f'Block "{block.name}" updated successfully!')
            return redirect('resources:block_list')
    else:
        form = BlockForm(instance=block)
    return render(request, 'resources/edit_block.html', {'form': form, 'block': block})

def delete_block(request, pk):
    """Delete block"""
    block = get_object_or_404(Block, pk=pk)
    if request.method == 'POST':
        # Check if block has classrooms
        classroom_count = block.campusclassroom_set.count()
        if classroom_count > 0:
            messages.error(request, f'Cannot delete block "{block.name}" because it has {classroom_count} classroom(s). Please delete or reassign the classrooms first.')
            return redirect('resources:block_list')
        
        block_name = block.name
        block.delete()
        messages.success(request, f'Block "{block_name}" deleted successfully!')
        return redirect('resources:block_list')
    return render(request, 'resources/confirm_delete_block.html', {'block': block})
