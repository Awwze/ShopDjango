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
    product = Product.objects.get(id=product_id)
    comments = product.reviews.all()

    if request.method == 'POST' and request.user.is_authenticated:
        rating = request.POST.get('rating')
        text = request.POST.get('text')  # Используем text вместо comment
        review = Review(product=product, author=request.user, rating=rating, text=text)
        review.save()
        messages.success(request, 'Ваш комментарий был добавлен!')
        return redirect('product_detail', product_id=product_id)

    return render(request, 'shop/product_detail.html', {'product': product, 'comments': comments})

def product_list(request):
    categories = Category.objects.all()
    selected_category = request.GET.get('category')

    if selected_category:
        products = Product.objects.filter(category_id=selected_category)
    else:
        products = Product.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
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
    cart_items = CartItem.objects.all()
    total_price = sum(item.total_price for item in cart_items)

    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

def update_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = request.POST.get('quantity')

    if quantity is not None:
        quantity = int(quantity)

        # Prevent quantity from going below 1
        if quantity < 1:
            # Optionally, remove item from cart if quantity is zero or less
            CartItem.objects.filter(product=product).delete()
        else:
            # Update cart item quantity logic
            cart_item, created = CartItem.objects.get_or_create(product=product)
            cart_item.quantity = quantity
            cart_item.save()

    return redirect('cart')  # Adjust to redirect to your cart view

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')  # Redirect to cart view after adding

def remove_from_cart(request, product_id):
    if request.method == "POST":
        cart_item = get_object_or_404(CartItem, product_id=product_id)
        cart_item.delete()  # Remove the item from the cart
    return redirect('cart')

def product_search(request):
    query = request.GET.get('q')
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.all()
    return render(request, 'shop/product_list.html', {'products': products, 'query': query})

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
