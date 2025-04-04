# Generated by Django 5.1.7 on 2025-03-31 23:22

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Curso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255, verbose_name='Nome do Curso')),
                ('limite_inscricoes', models.PositiveIntegerField(null=True)),
                ('descricao', models.TextField(blank=True, null=True, verbose_name='Descrição')),
            ],
        ),
        migrations.CreateModel(
            name='Funcionario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('cargo', models.CharField(choices=[('professor', 'Professor'), ('coordenador', 'Coordenador'), ('administrativo', 'Administrativo')], max_length=15)),
                ('email', models.EmailField(max_length=254)),
                ('telefone', models.CharField(max_length=11, validators=[django.core.validators.RegexValidator(message='O telefone deve conter entre 10 e 11 dígitos numéricos.', regex='^\\d{10,11}$')])),
                ('cursos', models.ManyToManyField(to='inscricoes.curso')),
            ],
        ),
        migrations.CreateModel(
            name='Inscricao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_completo', models.CharField(max_length=200)),
                ('cpf', models.CharField(max_length=11, unique=True, validators=[django.core.validators.RegexValidator(message='O CPF deve conter exatamente 11 dígitos numéricos.', regex='^\\d{11}$')])),
                ('rua', models.CharField(max_length=100)),
                ('bairro', models.CharField(max_length=100)),
                ('numero', models.CharField(max_length=10)),
                ('telefone_whatsapp', models.CharField(max_length=15, validators=[django.core.validators.RegexValidator(message='O telefone deve conter entre 10 e 11 dígitos numéricos.', regex='^\\d{10,11}$')])),
                ('data_nascimento', models.DateField()),
                ('data_inscricao', models.DateTimeField(auto_now_add=True)),
                ('cursos', models.ManyToManyField(related_name='inscricoes', to='inscricoes.curso')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('usuario',)},
            },
        ),
    ]
