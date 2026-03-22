from django.shortcuts import redirect
from masters.models import Branch


class BranchSelectionMiddleware:
    EXEMPT_URLS = [
        '/accounts/login/',
        '/accounts/logout/',
        '/accounts/select-branch/',
        '/admin/',
        '/static/',
        '/media/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            branch_id = request.session.get('current_branch_id')
            if branch_id:
                try:
                    request.current_branch = Branch.objects.get(pk=branch_id)
                except Branch.DoesNotExist:
                    request.current_branch = None
                    del request.session['current_branch_id']
            else:
                request.current_branch = None
                if not any(request.path.startswith(url) for url in self.EXEMPT_URLS):
                    return redirect('accounts:select_branch')
        else:
            request.current_branch = None
        return self.get_response(request)
