from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Ad, ExchangeProposal
from .forms import AdForm, ExchangeProposalForm


def signup(request):
    if request.user.is_authenticated:
        return redirect('ad_list')

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('ad_list')
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


# Список объявлений + поиск + фильтрация
def ad_list(request):
    query = request.GET.get("q")
    category = request.GET.get("category")
    condition = request.GET.get("condition")
    ads = Ad.objects.all()

    if query:
        ads = ads.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if category:
        ads = ads.filter(category__icontains=category)
    if condition:
        ads = ads.filter(condition=condition)

    paginator = Paginator(ads.order_by('-created_at'), 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "ad/list.html", {"page_obj": page_obj})


# Создание объявления
@login_required
def ad_create(request):
    if request.method == "POST":
        form = AdForm(request.POST)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.user = request.user
            ad.save()
            return redirect("ad_detail", ad.id)
    else:
        form = AdForm()
    return render(request, "ad/form.html", {"form": form})


# Редактирование объявления
@login_required
def ad_edit(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)
    if ad.user != request.user:
        return HttpResponseForbidden("Вы не можете редактировать это объявление.")

    form = AdForm(request.POST or None, instance=ad)
    if form.is_valid():
        form.save()
        return redirect("ad_detail", ad.id)
    return render(request, "ad/form.html", {"form": form})


# Удаление объявления
@login_required
def ad_delete(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id, user=request.user)
    if request.method == "POST":
        ad.delete()
        return redirect("ad_list")
    return render(request, "ad/confirm_delete.html", {"ad": ad})


# Детали объявления
def ad_detail(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)
    return render(request, "ad/detail.html", {"ad": ad})


# Создание предложения
@login_required
def proposal_create(request):
    ad_receiver_id = request.GET.get("ad_receiver_id")
    ad_receiver = Ad.objects.filter(id=ad_receiver_id).first()

    if request.method == "POST":
        form = ExchangeProposalForm(request.POST)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.status = "pending"
            proposal.save()
            messages.success(request, "Предложение успешно отправлено.")
            return redirect("proposal_list")
        else:
            messages.error(request, "Ошибка при создании предложения.")
    else:
        form = ExchangeProposalForm(initial={'ad_receiver': ad_receiver})

    user_ads = Ad.objects.filter(user=request.user)

    return render(request, "proposal/form.html", {
        "form": form,
        "user_ads": user_ads
    })


# Список предложений
@login_required
def proposal_list(request):
    # Получаем все предложения, где пользователь — отправитель или получатель
    proposals = ExchangeProposal.objects.filter(
        Q(ad_sender__user=request.user) | Q(ad_receiver__user=request.user)
    ).select_related("ad_sender", "ad_receiver")

    # Фильтрация
    status = request.GET.get("status")
    sender_id = request.GET.get("sender")
    receiver_id = request.GET.get("receiver")

    if status in ["pending", "accepted", "rejected"]:
        proposals = proposals.filter(status=status)

    if sender_id:
        proposals = proposals.filter(ad_sender__id=sender_id)

    if receiver_id:
        proposals = proposals.filter(ad_receiver__id=receiver_id)

    # Разделяем объявления:
    user_ads = Ad.objects.filter(user=request.user).distinct()
    other_ads = Ad.objects.filter(id__in=proposals.values_list("ad_receiver__id", flat=True)) \
        .exclude(user=request.user) \
        .distinct()

    return render(request, "proposal/list.html", {
        "proposals": proposals,
        "user_ads": user_ads,  # для фильтра "Что я предлагаю"
        "other_ads": other_ads,  # для фильтра "Что хочу получить"
        "request": request,
    })


@login_required
def proposal_update(request, proposal_id):
    proposal = get_object_or_404(ExchangeProposal, id=proposal_id)

    # Только получатель может менять статус
    if proposal.ad_receiver.user != request.user:
        return redirect("proposal_list")

    if request.method == "POST":
        status = request.POST.get("status")
        if status in ["accepted", "rejected"]:
            proposal.status = status
            proposal.save()
    return redirect("proposal_list")
