from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, F, FloatField

# 1. Categoria de Produto
class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome


# 2. Produto
class Produto(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="produtos")
    estoque = models.PositiveIntegerField(default=0)
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True)

    def __str__(self):
        return self.nome


# 3. Especificação de Produto
class Especificacao(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name="especificacoes")
    chave = models.CharField(max_length=100)  # ex: "Processador", "Memória RAM"
    valor = models.CharField(max_length=200)  # ex: "Intel Core i7", "16GB"

    def __str__(self):
        return f"{self.chave}: {self.valor}"


# 4. Comentário
class Comentario(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name="comentarios")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    comentario = models.TextField()
    data_comentario = models.DateTimeField(auto_now_add=True)
    nota = models.PositiveSmallIntegerField(default=5)  # Nota de 1 a 5

    def __str__(self):
        return f"Comentário de {self.usuario.username} em {self.produto.nome}"


# 5. Forma de Pagamento
class FormaPagamento(models.Model):
    nome = models.CharField(max_length=50)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome


# 6. Carrinho
class Carrinho(models.Model):
    data_criacao = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    @property
    def valor_total(self):
        total = self.itens.all().aggregate(
            total=Sum(F('quantidade') * F('produto__preco'), output_field=FloatField())
        )['total'] or 0.0
        return round(total, 2)

    def __str__(self):
        return f'Carrinho #{self.id} - Total: R${self.valor_total}'


# 7. Item no Carrinho
class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, related_name='itens', on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return round(self.quantidade * self.produto.preco, 2)

    def __str__(self):
        return f'{self.quantidade} x {self.produto.nome} - Subtotal: R${self.subtotal}'


# 8. Pedido
class Pedido(models.Model):
    carrinho = models.OneToOneField(Carrinho, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    data_pedido = models.DateTimeField(auto_now_add=True)
    forma_pagamento = models.ForeignKey(FormaPagamento, on_delete=models.PROTECT)
    endereco_entrega = models.TextField()
    status = models.CharField(max_length=20, choices=[('Pendente', 'Pendente'), ('Enviado', 'Enviado'), ('Entregue', 'Entregue')])

    @property
    def valor_total(self):
        return self.carrinho.valor_total

    def __str__(self):
        return f'Pedido #{self.id} - Total: R${self.valor_total} - Status: {self.status}'


# 9. Item no Pedido
class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    @property
    def subtotal(self):
        return self.quantidade * self.preco_unitario

    def save(self, *args, **kwargs):
        # Preencher o preço unitário com o preço do produto se não estiver definido
        if not self.preco_unitario:
            self.preco_unitario = self.produto.preco
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantidade} x {self.produto.nome} no pedido {self.pedido.id}"

    @classmethod
    def criar_itens_do_pedido(cls, carrinho, pedido):
        itens_carrinho = ItemCarrinho.objects.filter(carrinho=carrinho)
        for item_carrinho in itens_carrinho:
            item_pedido = cls(
                pedido=pedido,
                produto=item_carrinho.produto,
                quantidade=item_carrinho.quantidade,
                preco_unitario=item_carrinho.produto.preco
            )
            item_pedido.save()



# 10. Cliente
class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=20)
    endereco = models.TextField()

    def __str__(self):
        return f"Cliente: {self.usuario.username}"
