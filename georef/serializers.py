from rest_framework import serializers
from georef.models import Toponim, Tipustoponim, Filtrejson, Recursgeoref, Toponimversio, Paraulaclau, Capawms, \
    Capesrecurs, Qualificadorversio, Pais, Tipusrecursgeoref, Suport, Tipusunitats, Sistemareferenciamm
from georef_addenda.models import Profile, Autor, Organization, MenuItem, GeoreferenceProtocol
from django.contrib.auth.models import User
import json

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'


class TipusToponimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tipustoponim
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)
    organization = OrganizationSerializer()
    class Meta:
        model = Profile
        fields = '__all__'


class ToponimSearchSerializer(serializers.ModelSerializer):
    aquatic_str = serializers.ReadOnlyField()
    nom_str = serializers.ReadOnlyField()
    idtipustoponim = TipusToponimSerializer(required=True)
    coordenada_x_centroide = serializers.SerializerMethodField()
    coordenada_y_centroide = serializers.SerializerMethodField()
    precisio = serializers.SerializerMethodField()
    precisio_calc = serializers.SerializerMethodField()

    class Meta:
        model = Toponim
        fields = '__all__'

    def get_coordenada_x_centroide(self, obj):
        darrera_versio = obj.get_darrera_versio()
        if darrera_versio is None:
            return None
        else:
            return darrera_versio.get_coordenada_x_centroide

    def get_coordenada_y_centroide(self, obj):
        darrera_versio = obj.get_darrera_versio()
        if darrera_versio is None:
            return None
        else:
            return darrera_versio.get_coordenada_y_centroide

    def get_precisio(self, obj):
        darrera_versio = obj.get_darrera_versio()
        if darrera_versio is None:
            return None
        else:
            return darrera_versio.get_incertesa_centroide

    def get_precisio_calc(self, obj):
        darrera_versio = obj.get_darrera_versio()
        if darrera_versio is None:
            return None
        else:
            return darrera_versio.georefcalc_uncertainty


class ToponimSerializer(serializers.ModelSerializer):
    aquatic_str = serializers.ReadOnlyField()
    nom_str = serializers.ReadOnlyField()
    idtipustoponim = TipusToponimSerializer(required=True)
    idorganization = OrganizationSerializer()
    editable = serializers.SerializerMethodField()
    deletable = serializers.SerializerMethodField()
    coords_centroide = serializers.SerializerMethodField()

    class Meta:
        model = Toponim
        fields = '__all__'

    def get_org(self, obj):
        pass

    def get_coords_centroide(self,obj):
        darrera_versio = obj.get_darrera_versio()
        if darrera_versio:
            if darrera_versio.get_coordenada_x_centroide and darrera_versio.get_coordenada_y_centroide:
                return {'x': darrera_versio.get_coordenada_x_centroide ,'y': darrera_versio.get_coordenada_y_centroide }
        return None

    def is_editable(self, obj, user):
        if user.is_superuser:
            return True
        if not user.is_anonymous and user.profile and user.profile.toponim_permission == '1':
            return True
        if not user.is_anonymous and user.profile:
            if user.profile.toponim_permission:
                if user.profile.toponim_permission in obj.denormalized_toponimtree:
                    return True
        return False

    def get_editable(self, obj):
        user = self.context['request'].user
        return self.is_editable(obj, user)

    def get_deletable(self,obj):
        user = self.context['request'].user
        editable = self.is_editable(obj, user)
        deletable = False
        if not user.is_anonymous and user.profile and user.profile.permission_administrative is True:
            deletable = True
        return editable and deletable




class ToponimVersioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Toponimversio
        fields = '__all__'


class FiltrejsonSerializer(serializers.ModelSerializer):
    description = serializers.ReadOnlyField()
    editable = serializers.SerializerMethodField()

    class Meta:
        model = Filtrejson
        #fields = '__all__'
        fields = ('idfiltre', 'json', 'modul', 'nomfiltre', 'description', 'editable')

    def get_editable(self, obj):
        user = self.context['request'].user
        if user.is_superuser:
            return True
        if not user.is_anonymous and user.profile and user.profile.can_edit_filtre:
            return True
        return False


class RecursgeorefSerializer(serializers.ModelSerializer):
    editable = serializers.SerializerMethodField()

    class Meta:
        model = Recursgeoref
        fields = ('id', 'nom', 'editable')

    def get_editable(self, obj):
        user = self.context['request'].user
        return self.is_editable(obj,user)

    def get_deletable(self,obj):
        user = self.context['request'].user
        editable = self.is_editable(obj, user)
        deletable = False
        if not user.is_anonymous and user.profile and user.profile.permission_administrative is True:
            deletable = True
        return editable and deletable

    def is_editable(self, obj, user):
        if user.is_superuser:
            return True
        if not user.is_anonymous and user.profile and user.profile.can_edit_recurs:
            return True
        return False


class TipusunitatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tipusunitats
        fields = ('id', 'tipusunitat', 'description')


class SistemareferenciammSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sistemareferenciamm
        fields = ('id', 'nom')


class PaisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pais
        fields = ('id', 'nom', 'description')


class SuportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suport
        fields = ('id', 'nom', 'description')


class TipusrecursgeorefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tipusrecursgeoref
        fields = ('id', 'nom', 'description')


class QualificadorversioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qualificadorversio
        fields = ('id', 'qualificador', 'description')


class AutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Autor
        fields = ('id', 'nom', 'description')


class GeoreferenceProtocolSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeoreferenceProtocol
        fields = ('id', 'name', 'description')

class ParaulaClauSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paraulaclau
        fields = ('id', 'paraula', 'description')


class CapawmsSerializer(serializers.ModelSerializer):

    visible = serializers.SerializerMethodField()

    class Meta:
        model = Capawms
        fields = ('id','baseurlservidor','name','label','minx','maxx','miny','maxy','boundary','visible')

    def get_visible(self, obj):
        user = self.context['request'].user
        if len(user.prefswms.all()) > 0:
            prefs = user.prefswms.first()
            p_json = json.loads(prefs.prefscapesjson)
            for elem in p_json:
                if elem['id'] == obj.id:
                    return True
        return False


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'
