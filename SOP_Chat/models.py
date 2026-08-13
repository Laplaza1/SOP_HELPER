from django.db import models

class Document(models.Model):
    """
    Desc:
        title:
            tile of the file
        uploaded_file:
            uploads file to documents/
    
    """

    title = models.CharField(max_length=255)
    uploaded_file = models.FileField(upload_to='documents/')
    ##file_type = models.CharField(max_length=20, blank=True) |None # e.g., 'pdf', 'txt'

    class Meta:
        app_label = "SOP_Chat"
    def __str__(self):
        return self.title


    