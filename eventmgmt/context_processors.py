from .models import Category

def categories(request):
    return {'footer_categories': Category.objects.all()} 