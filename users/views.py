from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Permission
from django.urls import reverse
from users.models.profile_model import UserProfile


@login_required
def users_list_view(request):
    users = User.objects.all().select_related('profile').prefetch_related('groups', 'user_permissions')
    context = {'users': users}
    return render(request, 'users.html', context)

@login_required
@permission_required('admin.change_user', raise_exception=True)  # Ensure only admins can access
def update_user_permissions(request):
    if request.method == 'POST':
        for user in User.objects.all():
            add_perm = request.POST.get(f'add_building_{user.id}') == 'on'
            edit_perm = request.POST.get(f'change_building_{user.id}') == 'on'

            add_building_perm = Permission.objects.get(codename='add_building', content_type__app_label='buildings')
            change_building_perm = Permission.objects.get(codename='change_building', content_type__app_label='buildings')

            if add_perm:
                user.user_permissions.add(add_building_perm)
            else:
                user.user_permissions.remove(add_building_perm)

            if edit_perm:
                user.user_permissions.add(change_building_perm)
            else:
                user.user_permissions.remove(change_building_perm)

        return redirect(reverse('users_list_view')) # Redirect back to the user list

    # If not POST, redirect to the user list view
    return redirect(reverse('users_list_view'))

@login_required
def profile_view(request):
    user_profile = UserProfile.objects.get(user=request.user)
    return render(request, 'profile.html', {'user_profile': user_profile})
