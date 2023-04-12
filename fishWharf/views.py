from django.shortcuts import render
from products.models import Product
from category.models import Category
from django.http import Http404, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from accounts.models import Banner
 
# Create your views here. 


def home(request):
    products = Product.objects.all().filter(is_available=True)
    banner = Banner.objects.first()

    context = {
        'products' : products,
        'banner' : banner,
    }
    return render(request, 'home.html', context)

# ============================================================================================================================================================================

def  shop(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        # categories = get_object_or_404(Category, slug=category_slug)
        try:
            categories = Category.objects.get(slug = category_slug)
        except ObjectDoesNotExist:
            raise Http404
        
        products = Product.objects.filter(category=categories, is_available=True)

        #pagination
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products =  paginator.get_page(page)

        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        #pagination
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products =  paginator.get_page(page)
        product_count = products.count()

    context = {
        'products' : paged_products,
        'product_count' : product_count,
    }
    return render(request, 'shop.html', context)

# ============================================================================================================================================================================

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e
    
    context = {
        'single_product' : single_product,
    }
    return render(request, 'product_detail.html', context)

# ============================================================================================================================================================================

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword :
            products = Product.objects.order_by('-created_date').filter( Q(description__icontains = keyword) | Q(product_name__icontains = keyword) )
            product_count = products.count()
    context = {
        'products' : products,
        'product_count' : product_count
    }
    return render(request, 'shop.html', context)

# ============================================================================================================================================================================

def sorting(request):
    if 'sort_low_to_high' in request.path:
        products = Product.objects.order_by('price')

    elif 'sort_high_to_low' in request.path:
        products = Product.objects.order_by('-price')

    paginator = Paginator(products, 6)
    page = request.GET.get('page')
    paged_products =  paginator.get_page(page)
    product_count = products.count()
    context = {
        'products' : paged_products,
        'product_count' : product_count
    }
    return render(request, 'shop.html', context)


# ============================================================================================================================================================================
