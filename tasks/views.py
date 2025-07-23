from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Task, Comment
from .forms import TaskForm, CommentForm
from projects.models import Project

@login_required
def create_task(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    
    # Check if user has access to this project
    if request.user != project.owner and request.user not in project.members.all():
        messages.error(request, "You don't have access to this project.")
        return redirect('projects:dashboard')
    
    if request.method == 'POST':
        form = TaskForm(request.POST, project=project)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.created_by = request.user
            task.save()
            messages.success(request, 'Task created successfully!')
            return redirect('projects:detail', pk=project.pk)
    else:
        form = TaskForm(project=project)
    
    return render(request, 'tasks/create_task.html', {
        'form': form,
        'project': project
    })

@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    
    # Check if user has access to this task's project
    if (request.user != task.project.owner and 
        request.user not in task.project.members.all()):
        messages.error(request, "You don't have access to this task.")
        return redirect('projects:dashboard')
    
    comments = task.comments.all()
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('tasks:detail', pk=pk)
    else:
        comment_form = CommentForm()
    
    context = {
        'task': task,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'tasks/task_detail.html', context)

@login_required
def edit_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    
    # Check if user has access to this task's project
    if (request.user != task.project.owner and 
        request.user not in task.project.members.all()):
        messages.error(request, "You don't have access to this task.")
        return redirect('projects:dashboard')
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, project=task.project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('tasks:detail', pk=pk)
    else:
        form = TaskForm(instance=task, project=task.project)
    
    return render(request, 'tasks/edit_task.html', {
        'form': form,
        'task': task
    })

@login_required
@require_POST
def update_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    
    # Check if user has access to this task's project
    if (request.user != task.project.owner and 
        request.user not in task.project.members.all()):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    new_status = request.POST.get('status')
    if new_status in ['todo', 'in_progress', 'done']:
        task.status = new_status
        task.save()
        return JsonResponse({'success': True, 'status': task.get_status_display()})
    
    return JsonResponse({'error': 'Invalid status'}, status=400)
