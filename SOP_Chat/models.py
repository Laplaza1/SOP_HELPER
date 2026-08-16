from pathlib import Path

from django.db import models
import os
from django.utils.text import slugify
from django.contrib.postgres.fields import ArrayField
BASE_DIR = Path(__file__).resolve().parent
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

class Site_Account(models.Model):

    """
            Desc:
                site_name:
                    name of the site
                email:
                    email of user account
                password:
                    password
                Save_files:
                    will the site save the sop files after processing
            
            """
    
    class Meta:
        app_label = "SOP_Chat"
        ##permissions a site has over its data
        permissions = [("modify_sops","Add/Drop Sops"),("modify_users","change User settings")]
        ##notification options
        


    site_name = models.CharField(max_length=255,primary_key=True)
    email = models.EmailField()
    password = models.CharField(max_length=45)
    save_files = models.BooleanField(default=False)
    ##To get all users/sops from Site account in instance use 
    #site = Site_Account.objects.get(pk=1)
    #all_users = site.users.all()
    #all_sops = site.sops.all()

class User(models.Model):
    """
        Desc:
            site_name:
                name of the site
            username:
                username of the account
            email:
                email of user account
            password:
                password
            ServiceLevel:
                user access level to documents
        
        """



    class Meta:
        app_label = "SOP_Chat"
        #What types of users can see the SOPs
    CATEGORY_CHOICES = [
    ('User', 'User'),
    ('Superuser', 'Superuser'),
    ('Admin', 'Admin'),
    ]

    site_name = models.ForeignKey(
                    Site_Account,
                    on_delete=models.CASCADE,
                    default=1,
                    related_name="users")
    username = models.CharField(max_length=255,primary_key=True)
    email = models.EmailField()
    password = models.CharField(max_length=45)
    ServiceLevel = models.CharField(
        max_length=10,
        choices=CATEGORY_CHOICES,
        default='User',
    )




    def __str__(self):
        return f"{self.username} ({self.get_ServiceLevel_display()})"

##Alternative SOP
# class SOP(models.Model):
#     """
#     This is the refernce to SOPs
    
    
#     """

#     name=models.CharField(max_length=255,primary_key=True)
#     file = models.FilePathField(path=MEDIA_ROOT+"/documents",blank=True,null=True)
#     site_name = models.ForeignKey(
#                         Site_Account,
#                         on_delete=models.CASCADE,
#                         default=1,
#                         related_name="sops")

class Document(models.Model):
    """
    Desc:
        title:
            tile of the file
        uploaded_file:
            uploads file to documents/
    
    """

    title = models.CharField(max_length=255)
    uploaded_file = models.FileField(upload_to='documents/',blank=True,null=True)
    site_name = models.ForeignKey(
                            Site_Account,
                            on_delete=models.CASCADE,
                            related_name="sops",blank=True,null=True)
    
    ##file_type = models.CharField(max_length=20, blank=True) |None # e.g., 'pdf', 'txt'

    class Meta:
        app_label = "SOP_Chat"
        


    def remove_sop(self):
        """
        removes sop.
        """
        os.remove(MEDIA_ROOT+"/documents/"+self.title)
        self.delete()

    def __str__(self):
        return self.title
    
    def document_upload_to(instance, filename):
        """
        Force a controlled filename.
        """
        ext = os.path.splitext(filename)[1].lower() or '.pdf'
        safe_title = slugify(instance.title) or 'untitled'
        return f'documents/{safe_title}{ext}'
