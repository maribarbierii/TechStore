from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import *
from django.http import JsonResponse

class IndexView(View):
    def get(self, request):
        produtos = Produto.objects.all()  # Busca todos os produtos cadastrados
        return render(request, 'index.html', {'produtos': produtos})
    
from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import Produto, Comentario
from django.http import JsonResponse

class ProdutoView(View):
    def get(self, request, produto_id):
        produto = get_object_or_404(Produto, id=produto_id)
        especificacoes = produto.especificacoes.all()  # Obtendo as especificações do produto
        comentarios = produto.comentarios.all()  # Obtendo os comentários do produto
        
        context = {
            'produto': produto,
            'especificacoes': especificacoes,
            'comentarios': comentarios,
        }
        return render(request, 'produtos.html', context)
    
    def post(self, request, produto_id):
        produto = get_object_or_404(Produto, id=produto_id)
        
        # Verifica se o formulário foi enviado corretamente
        if request.method == "POST":
            comentario_texto = request.POST.get('comentario')
            nota = request.POST.get('nota')
            usuario = request.user  # Assume que o usuário está autenticado

            if comentario_texto and nota:
                # Criação do comentário
                comentario = Comentario.objects.create(
                    produto=produto,
                    usuario=usuario,
                    comentario=comentario_texto,
                    nota=nota
                )

                # Redireciona para a página do produto
                return render(request, 'produtos.html', {'produto': produto, 'comentarios': produto.comentarios.all()})
            
        # Em caso de erro ou falta de dados
        return render(request, 'produtos.html', {'produto': produto, 'comentarios': produto.comentarios.all()})

