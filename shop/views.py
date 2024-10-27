from django.contrib.auth import login, logout
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Review, Wishlist, Category,  UserLoginForm, CartItem
from django.contrib.auth.decorators import login_required
from .forms import CommentForm, UserRegistrationForm
from django.contrib import messages
from django.core.paginator import Paginator


def remove_from_wishlist(request, product_id):
    wishlist_item = get_object_or_404(Wishlist, user=request.user, product_id=product_id)
    wishlist_item.delete()
    return redirect('wishlist')

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    comments = product.reviews.all()

    if request.method == 'POST' and request.user.is_authenticated:
        rating = request.POST.get('rating')
        text = request.POST.get('text')  # Используем text вместо comment
        review = Review(product=product, author=request.user, rating=rating, text=text)
        review.save()
        messages.success(request, 'Ваш комментарий был добавлен!')
        return redirect('product_detail', product_id=product_id)

    return render(request, 'shop/product_detail.html', {
        'product': product,
        'comments': comments,
    })


def product_list(request):
    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    search_query = request.GET.get('q')

    products = Product.objects.all()

    if selected_category:
        products = products.filter(category_id=selected_category)

    if search_query:
        products = products.filter(name__icontains=search_query)

    context = {
        'categories': categories,
        'products': products,
        'selected_category': int(selected_category) if selected_category else None,
        'search_query': search_query,
    }
    return render(request, 'shop/product_list.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Вход пользователя после регистрации
            return redirect('product_list')  # Перенаправление на страницу с продуктами
    else:
        form = UserRegistrationForm()
    return render(request, 'shop/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('product_list')  # Перенаправление на страницу с продуктами
    else:
        form = UserLoginForm()
    return render(request, 'shop/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')  # Перенаправление на страницу входа

def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        product = Product(name=name, price=price, description=description, image=image)
        product.save()
        return redirect('product_list')

    return render(request, 'shop/add_product.html')

@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.total_price for item in cart_items)

    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })


@login_required
def update_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item = get_object_or_404(CartItem, product=product, user=request.user)

    quantity = int(request.POST.get('quantity'))

    if quantity > cart_item.quantity:
        if product.stock >= (quantity - cart_item.quantity):
            product.stock -= (quantity - cart_item.quantity)
            cart_item.quantity = quantity
        else:
            messages.error(request, "Недостаточно товара на складе.")
    elif quantity < cart_item.quantity:
        product.stock += (cart_item.quantity - quantity)
        cart_item.quantity = quantity

        if cart_item.quantity <= 0:
            cart_item.delete()
            messages.success(request, f"{product.name} был удален из вашей корзины.")

    product.save()
    if cart_item.quantity > 0:
        cart_item.save()

    return redirect('cart')


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.stock > 0:
        cart_item, created = CartItem.objects.get_or_create(product=product, user=request.user)
        if not created:
            cart_item.quantity += 1
        else:
            cart_item.quantity = 1
        product.stock -= 1
        product.save()

        cart_item.save()
    else:
        messages.error(request, "Товар закончился на складе!")

    return redirect('cart')



@login_required
def remove_from_cart(request, product_id):
    if request.method == "POST":
        cart_item = get_object_or_404(CartItem, product_id=product_id, user=request.user)
        product = cart_item.product
        product.stock += cart_item.quantity
        product.save()

        cart_item.delete()

    return redirect('cart')


def product_search(request):
    query = request.GET.get('q')
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.all()
    categories = Category.objects.all()  # Получаем все категории

    return render(request, 'shop/product_list.html', {
        'products': products,
        'query': query,
        'categories': categories,  # Передаем категории в шаблон
    })

def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        product = Product(name=name, price=price, description=description, image=image)
        product.save()
        return redirect('product_list')

    return render(request, 'shop/add_product.html')

def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Проверяем, есть ли уже этот продукт в списке желаемого
    if not Wishlist.objects.filter(user=request.user, product=product).exists():
        Wishlist.objects.create(user=request.user, product=product)
        return redirect('wishlist')  # Перенаправляем на страницу желаемого
    else:
        return redirect('product_detail', product_id=product.id)

@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'shop/wishlist.html', {'wishlist_items': wishlist_items})
