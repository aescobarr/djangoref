from django import forms
# from material import *
from georef.models import *
from django.forms import ModelForm
from django.forms import inlineformset_factory
#from datetimewidget.widgets import DateWidget
from bootstrap_datepicker_plus.widgets import DatePickerInput
from georef_addenda.models import Profile, LookupDescription
from djangoref import settings
from georef.cyclic import check_if_cyclic


class ChangePasswordForm(forms.Form):
    password_1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=True)
    password_2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=True)

    def clean_password_2(self):
        cleaned_data = self.cleaned_data
        password_2 = cleaned_data.get('password_2')
        password_1 = cleaned_data.get('password_1')
        if password_1 != password_2:
            raise forms.ValidationError('Els passwords són diferents! Si us plau torna a escriure\'ls')
        return password_2



class ToponimsForm(forms.Form):
    codi = forms.CharField(required=True)
    nom = forms.CharField(required=True)
    aquatic = forms.ChoiceField(choices=((None, ''), ('S', 'Sí'), ('N', 'No')))
    idtipustoponim = forms.ModelChoiceField(queryset=Tipustoponim.objects.extra(order_by=['nom']))
    idpais = forms.ModelChoiceField(queryset=Pais.objects.extra(order_by=['nom']))
    idpare = forms.ModelChoiceField(queryset=Toponim.objects.all())
    sinonims = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))


AQUATIC_CHOICES = (
    ('S','Sí'),
    ('N','No'),
)


class ToponimsUpdateForm(ModelForm):
    aquatic = forms.ChoiceField(choices=AQUATIC_CHOICES,widget=forms.RadioSelect, label='Aquàtic?', required=False)
    idtipustoponim = forms.ModelChoiceField(queryset=Tipustoponim.objects.all().order_by('nom'),widget=forms.Select, label='Tipus topònim')
    sinonims = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)

    class Meta:
        model = Toponim
        exclude = ['id','codi', 'nom_fitxer_importacio', 'linia_fitxer_importacio']
        widgets = {
            'idpare': forms.HiddenInput(),
        }

    def clean_idpare(self):
        cleaned_data = self.cleaned_data
        idtoponim = self.instance.id
        idpare = cleaned_data.get('idpare')
        idpare_id = idpare.id
        found = set()
        found.add(idtoponim)
        try:
            check_if_cyclic(idpare_id, found)
            return idpare
        except:
            raise forms.ValidationError('Aquest pare forma un cicle, operació no permesa')


class ToponimversioForm(ModelForm):
    numero_versio = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}),required=True)
    idqualificador = forms.ModelChoiceField(queryset=Qualificadorversio.objects.all().order_by('qualificador'), widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    #idrecursgeoref  = forms.ModelChoiceField(queryset=Recursgeoref.objects.all().order_by('nom'), widget=forms.Select, required=False)
    coordenada_x_centroide = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly','class': 'form-control'}), required=False)
    coordenada_x_origen = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    coordenada_y_centroide = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly','class': 'form-control'}), required=False)
    coordenada_y_origen = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    altitud_profunditat_maxima = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control'}), required=False)
    altitud_profunditat_minima = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control'}), required=False)
    precisio_h = forms.FloatField(widget=forms.NumberInput(attrs={'readonly':'readonly','class': 'form-control'}), required=False)
    observacions = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '5'}), required=False)
    georefcalc_string = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '5','cols': 50}), required=False)
    georefcalc_uncertainty = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control'}), required=False)
    georeference_protocol = forms.ModelChoiceField(queryset=GeoreferenceProtocol.objects.all().order_by('name'), widget=forms.Select(attrs={'class': 'form-control'}), required=True)
    # dateTimeOptions = {
    #     'format': 'dd/mm/yyyy'
    # }
    # datacaptura = forms.DateField(initial=datetime.date.today, input_formats=['%d/%m/%Y'],widget=DateWidget(bootstrap_version=3, options=dateTimeOptions),required=False)
    datacaptura = forms.DateField(widget=DatePickerInput({'class': 'form-control'}, options={"format": "DD/MM/YYYY"}))
    nom = forms.CharField(widget=forms.TextInput({'class': 'form-control'}))


    class Meta:
        model = Toponimversio
        #fields = ['numero_versio', 'idqualificador','idrecursgeoref','nom','datacaptura','coordenada_x_origen','coordenada_y_origen','coordenada_z_origen','precisio_z_origen','coordenada_x_centroide','coordenada_y_centroide','precisio_h','observacions']
        fields = ['numero_versio', 'idqualificador', 'idrecursgeoref', 'nom', 'datacaptura', 'coordenada_x_origen',
                  'coordenada_y_origen', 'altitud_profunditat_maxima', 'altitud_profunditat_minima', 'coordenada_x_centroide',
                  'coordenada_y_centroide', 'precisio_h', 'observacions', 'georefcalc_string', 'georefcalc_uncertainty', 'centroid_calc_method', 'georeference_protocol']
        widgets = {
            'idrecursgeoref': forms.HiddenInput(),
            'centroid_calc_method': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(ToponimversioForm, self).__init__(*args, **kwargs)
        self.fields['georeference_protocol'].initial = GeoreferenceProtocol.get_default_pk()


class UserForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username')

    def clean_email(self):
        cleaned_data = self.cleaned_data
        proposed_email = cleaned_data.get('email')
        if User.objects.filter(email=proposed_email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('Un altre usuari està fent servir aquest compte de correu, si us plau tria\'n un de diferent')
        return proposed_email


class NewUserForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password')

    def clean_email(self):
        cleaned_data = self.cleaned_data
        proposed_email = cleaned_data.get('email')
        if User.objects.filter(email=proposed_email).exists():
            raise forms.ValidationError('Un altre usuari està fent servir aquest compte de correu, si us plau tria\'n un de diferent')
        return proposed_email

    def clean_password(self):
        cleaned_data = self.cleaned_data
        password_2 = self.data['password_2']
        password_1 = cleaned_data.get('password')
        if password_1 != password_2:
            raise forms.ValidationError('Els passwords són diferents! Si us plau torna a escriure\'ls')
        return password_1


class NewUserProfileForm(forms.ModelForm):
    permission_tesaure_edition = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), required=False)
    permission_administrative = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), required=False)
    permission_filter_edition = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), required=False)
    permission_toponim_edition = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), required=False)
    permission_recurs_edition = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), required=False)
    organization = forms.ModelChoiceField(queryset=Organization.objects.all().order_by('name'), widget=forms.Select(attrs={'class': 'form-control'}), required=True)

    class Meta:
        model = Profile
        fields = ('toponim_permission', 'permission_tesaure_edition', 'permission_administrative', 'permission_filter_edition', 'permission_toponim_edition', 'permission_recurs_edition', 'organization')
        widgets = {
            'toponim_permission': forms.HiddenInput(),
        }

class ProfileForm(forms.ModelForm):
    permission_tesaure_edition = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), required=False)
    permission_administrative = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), required=False)
    permission_filter_edition = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), required=False)
    permission_toponim_edition = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), required=False)
    permission_recurs_edition = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), required=False)
    organization = forms.ModelChoiceField(queryset=Organization.objects.all().order_by('name'), widget=forms.Select(attrs={'class': 'form-control'}), required=False, disabled=True)

    class Meta:
        model = Profile
        fields = ('toponim_permission', 'permission_tesaure_edition', 'permission_administrative', 'permission_filter_edition', 'permission_toponim_edition', 'permission_recurs_edition', 'organization')
        widgets = {
            'toponim_permission': forms.HiddenInput(),
        }


class AddLookupDescriptionForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '5'}), required=True)
    class Meta:
        model = LookupDescription
        fields = ('description',)


class LookupDescriptionForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '5'}), required=True)
    class Meta:
        model = LookupDescription
        fields = '__all__'
        widgets = {
            'model_fully_qualified_name': forms.HiddenInput(),
            'model_label': forms.HiddenInput(),
            'locale': forms.HiddenInput(),
        }


class RecursForm(forms.ModelForm):

    nom = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    acronim = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    idtipusrecursgeoref = forms.ModelChoiceField(queryset=Tipusrecursgeoref.objects.all().order_by('nom'), widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    versio = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    campidtoponim = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    fitxergraficbase = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    idsistemareferenciamm = forms.ModelChoiceField(queryset=Sistemareferenciamm.objects.all().order_by('nom'), widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    idtipusunitatscarto = forms.ModelChoiceField(queryset=Tipusunitats.objects.all().order_by('tipusunitat'), widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    idsuport = forms.ModelChoiceField(queryset=Suport.objects.all().order_by('nom'), widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    urlsuport = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    actualitzaciosuport = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    ubicaciorecurs = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    comentariinfo = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control','rows':'5'}), required=False)
    comentariconsulta = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control','rows':'5'}), required=False)
    comentariqualitat = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control','rows':'5'}), required=False)
    divisiopoliticoadministrativa = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control','rows':'5'}), required=False)
    base_url_wms = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)

    class Meta:
        model = Recursgeoref
        fields = ('nom', 'acronim', 'idtipusrecursgeoref', 'versio', 'campidtoponim', 'fitxergraficbase','idsistemareferenciamm','idtipusunitatscarto','idsuport',
                  'urlsuport', 'actualitzaciosuport', 'ubicaciorecurs', 'comentariinfo', 'comentariconsulta',
                  'comentariqualitat', 'divisiopoliticoadministrativa', 'base_url_wms')
