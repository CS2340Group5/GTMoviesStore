from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, Report, User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce

# Create your views here.

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
        search_term = ''
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html',
                  {'template_data': template_data, 'search_term':search_term})

def show(request, id):
    movie = Movie.objects.get(id=id)
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = Review.objects.filter(movie=movie)

    total = 0
    count = 0

    for review in template_data['reviews']:
        if review.rating != 0:
            total += review.rating
            count += 1
    if count == 0:
        template_data['average_rating'] = ''
    else:
        template_data['average_rating'] = f"{(total / count):.2f}"

    return render(request, 'movies/show.html',
                  {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and (request.POST['comment'] != '' or request.POST['rating'] != 0):
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.rating = request.POST['rating']
        review.movie = movie
        review.user = request.user
        review.save()
    return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html',
            {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.rating = request.POST['rating']
        review.save()

    return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id,
        user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

def report(request, id, review_id):
    report = Report()
    review = get_object_or_404(Review, id=review_id)
    report.review = review
    report.save()
    return redirect('movies.show', id=id)

@login_required
def admin_statistics(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You do not have access to view this page.")

    movies = Movie.objects.all()
    users = User.objects.all()
    sort_by = request.GET.get('sort')
    top_buyer = None

    if sort_by == 'purchases':
        movies = movies.annotate(total_sales=Sum('item__quantity')).order_by('-total_sales')
    elif sort_by == 'comments':
        movies = movies.annotate(num_reviews=Count('review')).order_by('-num_reviews')
    elif sort_by == 'commenter':
        users = users.annotate(num_reviews=Count('review')).order_by('-num_reviews')
    elif sort_by == 'buyers':
        users = users.annotate(movies_bought = Coalesce(Sum('order__item__quantity'), 0)).order_by('-movies_bought', 'username')
        top_buyer = users.first()
        
    template_data = {
        'title' : 'Admin Statistics',
        'movies' : movies,
        'users' : users,
        'sort_by' : sort_by,
        'top_buyer' : top_buyer
    }

    return render(request, 'movies/admin_stats.html', {'template_data' : template_data})

@login_required
def admin_best_buyers(request):
    if not request.user.is_superuser:
            return HttpResponseForbidden("You do not have access to view this page.")
    users = User.objects.annotate(
        movies_purchased = Coalesce(Sum('order__item__quantity'), 0)
    ).order_by('-movie_purchased', 'username')
    total_users = users.count()
    list_size = None
    error = None
    size_parameter = request.GET.get('size', '').strip()
    if size_parameter:
        try:
            list_size = int(size_parameter)
            if list_size < 1:
                raise ValueError
        except ValueError:
            list_size = None
            error = 'Size should be integer'

    if list_size is not None:
        users = users[:list_size]
    users = list(users)

    template_data = {
            'title' : 'Best Buyers',
            'users' : users,
            'list_size' : list_size,
            'shown_count' : len(users),
            'total_users' : total_users,
            'error' : error
    }
    return render(request, 'movies/admin_best_buyers.html', {'template_data' : template_data})
