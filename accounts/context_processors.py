from masters.models import Branch


def branch_context(request):
    context = {
        'current_branch': getattr(request, 'current_branch', None),
        'user_branches': Branch.objects.none(),
    }
    if hasattr(request, 'user') and request.user.is_authenticated:
        if request.user.is_superuser:
            context['user_branches'] = Branch.objects.filter(is_active=True)
        else:
            context['user_branches'] = request.user.branches.filter(is_active=True)
    return context
