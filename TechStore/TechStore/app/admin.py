from django.contrib import admin
from .models import *

admin.site.register(Categoria)
admin.site.register(Produto)
admin.site.register(Especificacao)
admin.site.register(Comentario)
admin.site.register(FormaPagamento)
admin.site.register(Carrinho)
admin.site.register(ItemCarrinho)
admin.site.register(Pedido)
admin.site.register(ItemPedido)
admin.site.register(Cliente)
