from django.core.exceptions import ValidationError


def valid_extension(value):
    if (not value.name.endswith('.png') and
            not value.name.endswith('.jpeg') and
            not value.name.endswith('.gif') and
            not value.name.endswith('.bmp') and
            not value.name.endswith('.jpg') and
            not value.name.endswith('.pdf')):
        raise ValidationError("Archivos permitidos: .jpg, .jpeg, .png, .gif, .bmp, .pdf")


def valid_image_extension(value):
    if (not value.name.endswith('.png') and
            not value.name.endswith('.jpeg') and
            not value.name.endswith('.gif') and
            not value.name.endswith('.bmp') and
            not value.name.endswith('.jpg')):
        raise ValidationError("Archivos permitidos: .jpg, .jpeg, .png, .gif, .bmp")


def valid_csv_extension(value):
    if not value.name.endswith('.csv'):
        raise ValidationError("Archivos permitidos: .csv")