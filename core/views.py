import json
from pyexpat.errors import messages

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect

from core.models import Evento


# Create your views here.

def login_user(request):
    return render(request, 'login.html')


def logout_user(request):
    logout(request)
    return redirect('/')


def login_submit(request):
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        usuario = authenticate(username=username, password=password)
        if usuario is not None:
            login(request, usuario)
            return redirect('/')
        else:
            messages.error(request, 'Usuário ou senha inválidos!')
    return redirect('/')


@login_required(login_url='/login/')
def lista_eventos(request):
    usuario = request.user
    eventos = Evento.objects.filter(usuario=usuario).order_by('data_evento').reverse()
    dados = {'eventos': eventos}
    return render(request, 'agenda.html', dados)


# def index(request):
#     return redirect('/agenda')

@login_required(login_url='/login/')
def evento(request):
    id_evento = request.GET.get('id')
    dados = {}
    if id_evento:
        dados['evento'] = Evento.objects.get(id=id_evento)
    return render(request, 'evento.html', dados)


@login_required(login_url='/login/')
def evento_submit(request):
    if request.POST:
        titulo = request.POST.get('titulo')
        data_evento = request.POST.get('data_evento')
        descricao = request.POST.get('descricao')
        usuario = request.user
        id_evento = request.POST.get('id_evento')

        if id_evento:
            evento = Evento.objects.get(id=id_evento)

            if evento.usuario == usuario:
                evento.titulo = titulo
                evento.data_evento = data_evento
                evento.descricao = descricao
                evento.save()
            # Evento.objects.filter(id=id_evento).update(titulo=titulo,
            #                                            data_evento=data_evento,
            #                                            descricao=descricao
            #                                            )
        else:
            Evento.objects.create(titulo=titulo,
                                  data_evento=data_evento,
                                  descricao=descricao,
                                  usuario=usuario
                                  )
        return redirect('/')


@login_required(login_url='/login/')
def evento_delete(request, id_evento):
    usuario = request.user
    try:
        evento = Evento.objects.get(id=id_evento)
    except Exception:
        raise Http404

    if usuario == evento.usuario:
        evento.delete()
    else:
        raise Http404

    return redirect('/')


@login_required(login_url='/login/')
def evento_json(request, id_usuario):
    if id_usuario is None:
        usuario = request.user
    else:
        usuario = User.objects.get(id=id_usuario)
    try:
        evento = Evento.objects.filter(usuario=usuario).values()
    except Exception:
        raise Http404
    return JsonResponse(list(evento), safe=False)
