from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Perfil(models.Model):

    class Tipo(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        TECNICO = 'tecnico', 'Técnico'
        CLIENTE = 'cliente', 'Cliente'

    # cada usuário tem exatamente um perfil
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil'
    )

    tipo = models.CharField(
        max_length=10,
        choices=Tipo.choices,
        default=Tipo.CLIENTE
    )

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return f'{self.usuario.username} — {self.get_tipo_display()}'

    # propriedades auxiliares para uso nas views
    @property
    def is_admin(self):
        return self.tipo == self.Tipo.ADMIN

    @property
    def is_tecnico(self):
        return self.tipo == self.Tipo.TECNICO

    @property
    def is_cliente(self):
        return self.tipo == self.Tipo.CLIENTE



@receiver(post_save, sender=User)
def criar_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)