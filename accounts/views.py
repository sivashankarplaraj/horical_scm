from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import BranchSelectionForm, LoginForm


class LoginView(DjangoLoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def select_branch(request):
    if request.method == 'POST':
        form = BranchSelectionForm(request.POST, user=request.user)
        if form.is_valid():
            branch = form.cleaned_data['branch']
            request.session['current_branch_id'] = branch.pk
            return redirect('/')
    else:
        form = BranchSelectionForm(user=request.user)
    return render(request, 'accounts/select_branch.html', {'form': form})


@require_POST
@login_required
def switch_branch(request):
    branch_id = request.POST.get('branch_id')
    if branch_id:
        # Verify the user has access to this branch
        if request.user.is_superuser:
            from masters.models import Branch
            if Branch.objects.filter(pk=branch_id, is_active=True).exists():
                request.session['current_branch_id'] = int(branch_id)
        else:
            if request.user.branches.filter(pk=branch_id, is_active=True).exists():
                request.session['current_branch_id'] = int(branch_id)
    return redirect(request.META.get('HTTP_REFERER', '/'))
