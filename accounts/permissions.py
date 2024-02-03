from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from .models import complex,customer,User, worker

class is_complex_owner(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
            # return Response({'detail': "user not register"}, status=status.HTTP_403_FORBIDDEN)
        user = request.user
        comp = complex.objects.filter(owner=user).exists()
        if comp:
            return True
        else:
            return False
            # return Response({"detail":"user not complex owner"}, status=status.HTTP_403_FORBIDDEN)



account_permission = [
    "accounts.add_worker",
    "accounts.change_worker",
    "accounts.delete_worker",
    "accounts.view_worker",

    "accounts.change_complex",
    "accounts.view_complex",

    "accounts.add_image",
    "accounts.change_image",
    "accounts.delete_image",
    "accounts.view_image",

    "accounts.add_imageship",
    "accounts.change_imageship",
    "accounts.delete_imageship",
    "accounts.view_imageship",

    "accounts.add_bannership",
    "accounts.change_bannership",
    "accounts.delete_bannership",
    "accounts.view_bannership",
]


class checkPermission_for_account(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        user = request.user
        comp = complex.objects.filter(owner=user)
        if comp.exists():
            return True
        else:
            workerQuery = worker.objects.filter(user=user)
            if workerQuery.exists():
                userPerm = workerQuery[0].user.user_permissions.all()
                if userPerm:
                    for perm in account_permission:
                        if user.has_perm(perm) :
                            pass
                        else:
                            return False
                    return True
                else:
                    return False 
            else:
                return False


class isCustomer(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        user = request.user
        customerQuery = customer.objects.filter(user=user).exists()
        if customerQuery:
            return True
        else:
            return False

class icComplex_isWorker(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        user = request.user
        
        complexQuery = complex.objects.filter(owner=user)
        if not complexQuery.exists():
            complexQuery = worker.objects.filter(user=user)

        if complexQuery:
            return True
        else:
            return False