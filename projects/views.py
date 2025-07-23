from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Project, ProjectInvitation
from .forms import ProjectForm, InviteMemberForm
from tasks.models import Task

@login_required
def dashboard(request):
    user_projects = Project.objects.filter(
        Q(owner=request.user) | Q(members=request.user)
    ).distinct()
    
    recent_tasks = Task.objects.filter(
        project__in=user_projects,
        assigned_to=request.user
    ).order_by('-created_at')[:5]
    
    pending_invitations = ProjectInvitation.objects.filter(
        invitee=request.user,
        accepted=False
    )
    
    context = {
        'projects': user_projects,
        'recent_tasks': recent_tasks,
        'pending_invitations': pending_invitations,
    }
    return render(request, 'projects/dashboard.html', context)

@login_required
def project_list(request):
    projects = Project.objects.filter(
        Q(owner=request.user) | Q(members=request.user)
    ).distinct()
    return render(request, 'projects/project_list.html', {'projects': projects})

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    # Check if user has access to this project
    if request.user != project.owner and request.user not in project.members.all():
        messages.error(request, "You don't have access to this project.")
        return redirect('projects:dashboard')
    
    tasks = project.tasks.all().order_by('-created_at')
    
    # Group tasks by status
    todo_tasks = tasks.filter(status='todo')
    in_progress_tasks = tasks.filter(status='in_progress')
    done_tasks = tasks.filter(status='done')
    
    context = {
        'project': project,
        'todo_tasks': todo_tasks,
        'in_progress_tasks': in_progress_tasks,
        'done_tasks': done_tasks,
    }
    return render(request, 'projects/project_detail.html', context)

@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            messages.success(request, 'Project created successfully!')
            return redirect('projects:detail', pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, 'projects/create_project.html', {'form': form})

@login_required
def invite_member(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.user != project.owner:
        messages.error(request, "Only project owner can invite members.")
        return redirect('projects:detail', pk=pk)
    
    if request.method == 'POST':
        form = InviteMemberForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['username']
            invitation, created = ProjectInvitation.objects.get_or_create(
                project=project,
                inviter=request.user,
                invitee=user
            )
            if created:
                messages.success(request, f'Invitation sent to {user.username}!')
            else:
                messages.info(request, f'{user.username} has already been invited.')
            return redirect('projects:detail', pk=pk)
    else:
        form = InviteMemberForm()
    
    return render(request, 'projects/invite_member.html', {
        'form': form,
        'project': project
    })

@login_required
def accept_invitation(request, invitation_id):
    invitation = get_object_or_404(ProjectInvitation, pk=invitation_id, invitee=request.user)
    invitation.project.members.add(request.user)
    invitation.accepted = True
    invitation.save()
    messages.success(request, f'You joined {invitation.project.name}!')
    return redirect('projects:detail', pk=invitation.project.pk)
