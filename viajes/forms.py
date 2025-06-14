import os
from django import forms
from .models import Viaje, Piloto, Guia
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.conf import settings


class RegistroForm(UserCreationForm):
    """
    Formulario para registrar nuevos usuarios.
    Extiende el formulario UserCreationForm de Django para incluir campos adicionales como
    nombre, apellido y correo electrónico.

    Campos:
    - username: Nombre de usuario.
    - first_name: Nombre del usuario.
    - last_name: Apellido del usuario.
    - email: Correo electrónico del usuario.
    - password1: Contraseña.
    - password2: Confirmación de la contraseña.

    Métodos:
    - clean_first_name: Capitaliza el nombre ingresado.
    - clean_last_name: Capitaliza el apellido ingresado.
    - clean_username: Convierte el nombre de usuario a minúsculas.
    """
    first_name = forms.CharField(label='Nombre', max_length=30)
    last_name = forms.CharField(label='Apellido', max_length=30)
    email = forms.EmailField(label='Email')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '')
        return first_name.capitalize()

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', '')
        return last_name.capitalize()

    def clean_username(self):
        username = self.cleaned_data.get('username', '')
        return username.lower()


class EditarUsuarioForm(forms.ModelForm):
    """
    Formulario para editar los datos de un usuario existente.

    Campos:
    - first_name: Nombre del usuario.
    - last_name: Apellido del usuario.
    - email: Correo electrónico del usuario.

    Métodos:
    - clean_first_name: Capitaliza el nombre ingresado.
    - clean_last_name: Capitaliza el apellido ingresado.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
        }

    def clean_first_name(self):
        return self.cleaned_data['first_name'].capitalize()
    
    def clean_last_name(self):
        return self.cleaned_data['last_name'].capitalize()


class GuiaForm(forms.ModelForm):
    """
    Formulario para gestionar los datos de un guía.

    Campos:
    - nombre, apellido, email, dni, telefono, fecha_nac, ciudad, pais, sobre_mi, foto.

    Widgets personalizados:
    - fecha_nac: Selector de fecha.
    - sobre_mi: Área de texto con 4 filas.

    Métodos:
    - __init__: Agrega la clase CSS 'form-control' a todos los campos.
    """
    fecha_nac = forms.DateField(
        label='Fecha de nacimiento',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
    )

    class Meta:
        model = Guia
        fields = ['nombre', 'apellido', 'email', 'dni', 'telefono', 'fecha_nac', 'ciudad', 'pais', 'sobre_mi', 'foto']
        widgets = {
            'sobre_mi': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super(GuiaForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class PilotoForm(forms.ModelForm):
    """
    Formulario para gestionar los datos de un piloto.

    Campos:
    - telefono, fecha_nac, ciudad, pais, sobre_mi, moto, avatar.

    Widgets personalizados:
    - fecha_nac: Selector de fecha.
    - sobre_mi: Área de texto con 4 filas.
    - avatar: Selector de opciones con imágenes disponibles en la carpeta 'static/avatars'.

    Métodos:
    - __init__: Carga las opciones de avatar dinámicamente desde el sistema de archivos.
    """
    fecha_nac = forms.DateField(
        label='Fecha de nacimiento',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
    )
    avatar = forms.ChoiceField(choices=[], widget=forms.RadioSelect)

    class Meta:
        model = Piloto
        fields = ['telefono', 'fecha_nac', 'ciudad', 'pais', 'sobre_mi', 'moto', 'avatar']
        widgets = {
            'sobre_mi': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        avatars_dir = os.path.join(settings.BASE_DIR, 'static/avatars')
        avatars = sorted(os.listdir(avatars_dir))
        self.fields['avatar'].choices = [(a, a) for a in avatars]


class ViajeForm(forms.ModelForm):
    """
    Formulario para gestionar los datos de un viaje.

    Campos:
    - nombre, detalle, fecha_salida, cant_dias, km, dificultad, guia, pilotos, activo, max_pilotos.

    Widgets personalizados:
    - fecha_salida: Selector de fecha.
    - detalle: Área de texto con 4 filas.

    Métodos:
    - __init__: Personaliza los widgets de los campos y ajusta etiquetas y valores predeterminados.
    """
    class Meta:
        model = Viaje
        fields = ['nombre', 'detalle', 'fecha_salida', 'cant_dias', 'km', 'dificultad', 'guia', 'pilotos', 'activo', 'max_pilotos']
        widgets = {
            'fecha_salida': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'detalle': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super(ViajeForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs['class'] = 'form-control'
        self.fields['pilotos'].widget.attrs['id'] = 'id_pilotos'
        self.fields['km'].label = 'Kilómetros'
        self.fields['max_pilotos'].label = 'Máxima cantidad de pilotos'

        # Campo guía: mostrar label según haya guías o no
        guia_field = self.fields.get('guia', None)
        if guia_field and hasattr(guia_field, 'queryset'):
            if not guia_field.queryset.exists(): # type: ignore
                guia_field.empty_label = 'Aún sin asignar' # type: ignore
            else:
                guia_field.empty_label = 'Seleccione una guía' # type: ignore

        # Estado (activo / borrador)
        self.fields['activo'] = forms.ChoiceField(
            choices=[(True, 'Activo'), (False, 'Borrador')],
            widget=forms.Select(attrs={'class': 'form-control'}),
            label='Estado'
        )