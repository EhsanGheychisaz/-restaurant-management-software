from django.core.cache import cache
from random import randint
from kavenegar import *
from order.models import order
import qrcode
from PIL import Image
from uuid import uuid4
import os


def path_and_rename(instance, filename):
    upload_to = 'users/profile_images'
    ext = filename.split('.')[-1]
    # get filename
    if instance.pk:
        filename = '{}.{}'.format(uuid4().hex, ext)
    else:
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)
    
kaveApi = '6A776234335663495752696441514B622F77727A61384A38447466342B79656B56756354697152704E2B593D'

def otp(phoneNumber, exists, user):
    try:
        token = randint(1000, 9999)
        api = KavenegarAPI(kaveApi)
        params = {
            'receptor': phoneNumber,
            'template': 'user',
            'token' : token,
            'type': 'sms'
        }
        if exists:
            data = {'token': str(token), 'verify': True, 'exists': True, 'role':user} 
        else:
            data = {'token': str(token), 'verify': False, 'exists': False, 'role':user} 
        
        tokenCache = cache.set(str(phoneNumber), data, 120)
        tokenCacheExists = cache.get(str(phoneNumber))
        
        response = api.verify_lookup(params)
        return response, tokenCacheExists
    except APIException as e: 
        return e
    except HTTPException as e: 
        return e

def bestsellingItems(complex, menu, count):
    try:
        freq = {}
        itemList = []
        orderList = order.objects.filter(foodComplex=complex, relatedMenu=menu)
        
        for eachOrder in orderList:
            for item in eachOrder.items:
                if item.get('id') in freq:
                    freq[item.get('id')]+=1
                else:
                    freq[item.get('id')]=1
        
        if len(freq) <= count:
            itemsList = list(freq.keys())
        else:
            for i in range(count):
                keymax = max(zip(freq.values(), freq.keys()))[1]
                freq.pop(keymax)
                itemList.append(keymax)
            itemsList = itemList

        return itemsList
    except Exception as e:
        return str(e)

def generateQR(logo, name):
    try:

        # taking image which user wants
        # in the QR code center
        Logo_link = logo
        
        logo = Image.open(Logo_link)
        
        # taking base width
        basewidth = 100
        
        # adjust image size
        wpercent = (basewidth/float(logo.size[0]))
        hsize = int((float(logo.size[1])*float(wpercent)))
        logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)
        QRcode = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_H
        )
        
        # taking url or text
        url = f'https://xr7.ir/{name}'
        
        # adding URL or text to QRcode
        QRcode.add_data(url)
        
        # generating QR code
        QRcode.make()
        
        # taking color name from user
        QRcolor = 'Green'
        
        # adding color to QR code
        QRimg = QRcode.make_image(
            fill_color=QRcolor, back_color="white").convert('RGB')
        
        # set size of QR code
        pos = ((QRimg.size[0] - logo.size[0]) // 2,
            (QRimg.size[1] - logo.size[1]) // 2)
        QRimg.paste(logo, pos)
        
        # save the QR code generated
        # name = name.strip()
        # print(name)
        name = name.replace(' ', '')
        print(name)
        path = f'media/users/qr/{name}_qr.png'
        QRimg.save(path)
        return True, path
    except Exception as e:
        return False, path
