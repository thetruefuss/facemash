import math
import random

from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect, render

from .forms import FaceMashForm
from .models import FaceMash


def play(request):
    """
    View to populate homepage with two contestant photos and serve previously voted photos.
    """
    try:
        if request.GET.get("prev"):
            first_photo_id = request.session.get("first_photo_id", None)
            second_photo_id = request.session.get("second_photo_id", None)
            if first_photo_id is not None and second_photo_id is not None:
                contestant_1 = FaceMash.objects.get(id=first_photo_id)
                contestant_2 = FaceMash.objects.get(id=second_photo_id)
                context = {'contestant_1': contestant_1, 'contestant_2': contestant_2}
            else:
                prev_error = True
                context = {'prev_error': prev_error}
        else:
            contestants = FaceMash.objects.all()
            contestant_1 = random.choice(contestants)
            contestant_2 = random.choice(contestants)
            while contestant_1 == contestant_2:
                contestant_2 = random.choice(contestants)
            context = {'contestant_1': contestant_1, 'contestant_2': contestant_2}
    except IndexError:
        index_error = True
        context = {'index_error': index_error}
    return render(request, 'facemash/homepage.html', context)


def submit(request):
    if request.method == 'POST':
        form = FaceMashForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Photo Added Successfully.')
        return redirect('submit')
    else:
        form = FaceMashForm()
    return render(request, 'facemash/submit_form.html', {'form': form})


def glicko2_rating_system(request, winner_id, loser_id):
    """
    View to calculate contestants ratings using Glicko 2 Algorithm and save their ids in sessions.
    """
    try:
        winner = FaceMash.objects.get(id=winner_id)
        loser = FaceMash.objects.get(id=loser_id)
        request.session['first_photo_id'] = winner.id
        request.session['second_photo_id'] = loser.id
        w = winner
        l = loser

        """ GLicko 2 Algorithm """
        TAU = 0.5
        s_w = 1.0
        s_l = 0.0
        mu_w = (w.ratings - 1500.0) / 173.7178
        mu_l = (l.ratings - 1500.0) / 173.7178
        phi_w = w.rd / 173.7178
        phi_l = l.rd / 173.7178
        g_w = 1.0 / math.sqrt(1.0 + 3.0 * pow(phi_w, 2) / pow(math.pi, 2))
        g_l = 1.0 / math.sqrt(1.0 + 3.0 * pow(phi_l, 2) / pow(math.pi, 2))
        E_w = 1.0 / (1.0 + math.exp(-g_w * (mu_w - mu_l)))
        E_l = 1.0 / (1.0 + math.exp(-g_l * (mu_l - mu_w)))
        nu_w = 1.0 / (pow(g_l, 2) * E_w * (1 - E_w))
        nu_l = 1.0 / (pow(g_w, 2) * E_l * (1 - E_l))
        delta_w = nu_w * g_l * (s_w - E_w)
        delta_l = nu_l * g_w * (s_l - E_l)
        a_w = math.log(pow(w.sigma, 2), math.e)
        a_l = math.log(pow(l.sigma, 2), math.e)
        def function_x(x, delta, phi, nu, a):
            e_x = math.exp(x)
            multi = pow(delta, 2) - pow(phi, 2) - nu - math.exp(x)
            divi = 2.0 * pow((phi+nu+e_x), 2)
            minus = (x-a) / pow(TAU, 2)
            result = e_x * multi/divi - minus
            return result
        EPSILON = 0.000001
        A_w = a_w
        if pow(delta_w, 2) > (pow(phi_w, 2) + nu_w):
            B_w = math.log((pow(delta_w, 2) - pow(phi_w, 2) - nu_w), math.e)
        else:
            k = 1
            x = a_w - k * TAU
            f_x = function_x(x, delta_w, phi_w, nu_w, a_w)
            while f_x < 0:
                k += 1
                x = a_w - k * TAU
                function_x(x, delta_w, phi_w, nu_w, a_w)
            B_w = a_w - k * TAU
        f_A_w = function_x(A_w, delta_w, phi_w, nu_w, a_w)
        f_B_w = function_x(B_w, delta_w, phi_w, nu_w, a_w)
        while abs(B_w - A_w) > EPSILON:
            C_w = A_w + (A_w-B_w) * f_A_w / (f_B_w-f_A_w)
            f_C_w = function_x(C_w, delta_w, phi_w, nu_w, a_w)
            if f_C_w * f_B_w < 0:
                A_w = B_w
                f_A_w = f_B_w
            else:
                f_A_w = f_A_w/2.0
            B_w = C_w
            f_B_w = f_C_w
        sigma_2_w = math.exp(A_w/2.0)
        p_s_w = math.sqrt(pow(phi_w, 2)+pow(sigma_2_w, 2))
        A_l = a_l
        if pow(delta_l, 2) > (pow(phi_l, 2) + nu_l):
            B_l = math.log((pow(delta_l, 2) - pow(phi_l, 2) - nu_l), math.e)
        else:
            k = 1
            x = a_l - k * TAU
            f_x = function_x(x, delta_l, phi_l, nu_l, a_l)
            while f_x < 0:
                k += 1
                x = a_l - k * TAU
                function_x(x, delta_l, phi_l, nu_l, a_l)
            B_l = a_l - k * TAU
        f_A_l = function_x(A_l, delta_l, phi_l, nu_l, a_l)
        f_B_l = function_x(B_l, delta_l, phi_l, nu_l, a_l)
        while abs(B_l - A_l) > EPSILON:
            C_l = A_l + (A_l-B_l)*f_A_l/(f_B_l-f_A_l)
            f_C_l = function_x(C_l, delta_l, phi_l, nu_l, a_l)
            if f_C_l * f_B_l < 0:
                A_l = B_l
                f_A_l = f_B_l
            else:
                f_A_l = f_A_l/2.0
            B_l = C_l
            f_B_l = f_C_l
        sigma_2_l = math.exp(A_l/2.0)
        p_s_l = math.sqrt(pow(phi_l, 2)+pow(sigma_2_l, 2))
        p_2_w = 1.0/math.sqrt(1.0/pow(p_s_w, 2) + 1.0/nu_w)
        p_2_l = 1.0/math.sqrt(1.0/pow(p_s_l, 2) + 1.0/nu_l)
        u_2_w = mu_w + pow(p_s_w, 2) * g_l * (s_w - E_w)
        u_2_l = mu_l + pow(p_s_l, 2) * g_w * (s_l - E_l)
        w.ratings = 173.7178 * u_2_w + 1500
        w.sigma = sigma_2_w
        l.ratings = 173.7178 * u_2_l + 1500
        l.sigma = sigma_2_l
        w.rd = 173.7178 * p_2_w
        if w.rd < 30:
            w.rd = 30
        l.rd = 173.7178 * p_2_l
        if l.rd < 30:
            l.rd = 30
        w.save()
        l.save()
        return redirect('play')
    except FaceMash.DoesNotExist:
        raise Http404


def ratings_page(request):
    """
    View to serve photos based on their ratings with a pagination serving 5 photos at a time.
    """
    photos = FaceMash.objects.all().order_by('-ratings')
    paginator = Paginator(photos, 5)
    page = request.GET.get('page')
    if paginator.num_pages > 1:
        p = True
    else:
        p = False
    try:
        photos = paginator.page(page)
    except PageNotAnInteger:
        photos = paginator.page(1)
    except EmptyPage:
        photos = paginator.page(paginator.num_pages)
    context = {'photos' : photos, 'p': p}
    return render(request, "facemash/ratings_page.html", context)


def about_page(request):
    return render(request, "facemash/about_page.html")
