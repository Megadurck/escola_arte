# Generated by Django 5.1.7 on 2025-04-07 02:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscricoes', '0006_alter_horariocurso_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='turma',
            name='vagas_originais',
            field=models.IntegerField(default=30, help_text='Número original de vagas da turma'),
        ),
    ]
