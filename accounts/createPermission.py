from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType

from menu.models import *
from order.models import *
from .models import *
import os, sys
import traceback


class MetaMenuPermissions:

    def __init__(self, user):
        self.user = user

    def permission_add(self, model, limitedList=None):
        try:
            permission_list = list()
            content_type = ContentType.objects.get_for_model(model)
            model_permission = Permission.objects.filter(content_type=content_type)
            for perm in model_permission:
                permission_list.append(perm.codename)
            
            for permission in model_permission:
                try:
                    print(permission.codename)
                    if limitedList:
                        if permission.codename in limitedList:
                            pass
                        else: 
                            self.user.user_permissions.add(permission)
                    else:
                        self.user.user_permissions.add(permission)
                except:
                    return False
            allocate_new_instance_user = get_user_model().objects.get(username=self.user.username)
            return True
            
            # for permission in model_permission:
            #     res = allocate_new_instance_user.has_perm(permission)
            #     if limitedList:
            #         if res ==False and permission.codename not in limitedList:
            #             return False, permission
            #     else:
            #         if res ==False:
            #             return False, permission
            # if res == True:
            #     return True, 'ALL'
        except:
            logger.exception('OPPS ...')
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)           

    def permission_remove(self, model):
        try:
            permission_list = list()
            content_type = ContentType.objects.get_for_model(model)
            
            model_permission = Permission.objects.filter(content_type=content_type)
            
            for perm in model_permission:
                permission_list.append(perm.codename)

            for permission in model_permission:
                try:
                    self.user.user_permissions.remove(permission)
                except:
                    pass

            allocate_new_instance_user = get_user_model().objects.get(username=self.user.username)
            
            for permission in permission_list:
                res = allocate_new_instance_user.has_perm(permission)
                if res ==True:
                    return False, permission
            if res == False:
                return True, "ALL"
        except Exception as e:
            logger.exception('OPPS ...')


    def menu_permissions_add(self):
        try:
            menu_model_list = [
                additional,
                Menu,
                itemDiscount,
                priceCard,
                Item,
                itemImageShip,
                itemShip,
                category,
                catShip,
                subCategory,
            ]
            for model in menu_model_list:
                status = self.permission_add(model)
                if status == False:
                    return False
            return True
        except:
            logger.exception('OPPS ...')
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)           
    
    def menu_permissions_remove(self):
        try:    
            menu_model_list = [
                additional,
                Menu,
                itemDiscount,
                priceCard,
                Item,
                itemImageShip,
                itemShip,
                category,
                catShip,
                subCategory,
            ]
            log_list= list()
            for model in menu_model_list:
                status, permission = self.permission_remove(model)
                if status == False:
                    log_list.append(dict(errorDetails = permission, model=model))
            if not log_list:
                return True, "DONE"
            else:
                return False, log_list     
        except Exception as e:
            logger.exception('OPPS ...')

    def order_permissions_add(self):
        try:
            order_model_list = [
                order,
            ]
            for model in order_model_list:
                status = self.permission_add(model)
                if status == False:
                    return False
            return True
        except Exception as e:
            logger.exception('OPPS ...')

    def order_permissions_remove(self):
        try:
            order_model_list = [
                order,
            ]
            log_list= list()
            for model in order_model_list:
                status, permission = self.permission_remove(model)
                if status == False:
                    log_list.append(dict(errorDetails = permission, model=model))
            if not log_list:
                return True, "DONE"
            else:
                return False, log_list    
        except Exception as e:
            logger.exception('OPPS ...')

    def account_permissions_add(self):
        try:
            account_model_list = [
                worker,
                complex,
                image,
                imageShip,
                bannerShip,
            ]
            log_list= list()
            for model in account_model_list:
                if model == complex:
                    limitedList = ['add_complex', 'delete_complex']
                else:
                    limitedList = None
                status = self.permission_add(model, limitedList)
                if status == False:
                    return False
            return True
        except Exception as e:
            logger.exception('OPPS ...')

    def account_permissions_remove(self):
        try:
            account_model_list = [
                worker,
                complex,
                image,
                imageShip,
                bannerShip,
            ]
            log_list= list()
            for model in account_model_list:
                status, permission = self.permission_remove(model)
                if status == False:
                    log_list.append(dict(errorDetails = permission, model=model))
            if not log_list:
                return True, "DONE"
            else:
                return False, log_list   
        except Exception as e:
            logger.exception('OPPS ...')

    def payment_permissions_add(self):
        try:
            payment_model_list = [
                payment,
            ]
            log_list= list()
            for model in payment_model_list:
                if model == payment:
                    limitedList = ['add_payment', 'delete_payment',
                    'change_payment']
                else:
                    limitedList = None
                status = self.permission_add(model, limitedList)
                if status == False:
                    return False
            return True
        except Exception as e:
            logger.exception('OPPS ...')

    def payment_permissions_remove(self):
        try:
            payment_model_list = [
                payment,
            ]
            log_list= list()
            for model in payment_model_list:
                status, permission = self.permission_remove(model)
                if status == False:
                    log_list.append(dict(errorDetails = permission, model=model))
            if not log_list:
                return True, "DONE"
            else:
                return False, log_list
        except Exception as e:
            logger.exception('OPPS ...')