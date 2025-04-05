from django import template

register = template.Library()

@register.filter
def split(value, delimiter):
    """Divide uma string usando o delimitador especificado."""
    return value.split(delimiter)

@register.filter
def get_field(form, field_name):
    """
    Retorna o campo do formulário pelo nome.
    """
    return form[field_name] 