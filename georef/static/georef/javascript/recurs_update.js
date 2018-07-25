var refreshDigitizedGeometry = function(){
    var geometry = djangoRef.Map.editableLayers.toGeoJSON();
    var json_string = JSON.stringify(geometry);
    $('#geometria').val( json_string );
};

function anarAUrl(inputId){
    window.open ( $('#'+inputId).val() ,'_blank');
    window.focus();
}

function showListToponims(){
    $( "#dialogListToponims" ).dialog( "open" );
}

var get_capawms_ids = function(){
    var retVal = new Array();
    $('.hidden-capawms-id-value').each(function(index,value){
        retVal.push($(this).text());
    });
    return retVal;
};

var capawms_li_element_template = '<li class="tagit-choice ui-widget-content ui-state-default ui-corner-all tagit-choice-editable"><span class="tagit-label">###label</span><span class="hidden-capawms-id-value">###id</span><a class="tagit-close close-capawms"><span class="text-icon">x</span><span class="ui-icon ui-icon-close"></span></a></li>';

$(document).ready(function() {

    var buildCapesWMSUI = function(){
        $('#taulacapes').empty();
        for(var i = 0; i < capes_wms.length; i++){
            var new_template = capawms_li_element_template.replace('###label',capes_wms[i].label);
            new_template = new_template.replace('###id',capes_wms[i].id);
            $('#taulacapes').append(new_template);
        }
    }

    buildCapesWMSUI();

    var buildTagsUI = function (){
        var paraula_array = paraulesclau.split(",");
        $("#paraulaclau_list").tagit("removeAll");
        for(var i = 0; i < paraula_array.length; i++){
            $("#paraulaclau_list").tagit("createTag", paraula_array[i]);
        }
        var autor_array = autors.split(",");
        $("#autor_list").tagit("removeAll");
        for(var i = 0; i < autor_array.length; i++){
            $("#autor_list").tagit("createTag", autor_array[i]);
        }
    };

    buildTagsUI();

    var init_toponims_basats_recurs = function(nodes){
        $('#toponimsbasats ul').empty();
        for(var i = 0; i < toponims_basats_recurs.length; i++){
            var id = toponims_basats_recurs[i].id;
            var nom = toponims_basats_recurs[i].nom;
            var linkVisualitzar = '<li><a target="_blank" href="/toponims/update/' + id + '/-1" title="'+nom+'"><span class="label label-default">' + nom + '</span></a></li>';
            $('#toponimsbasats ul').append(linkVisualitzar);
        }
        if(moretoponims){
            $('#toponimsbasats ul').append('<li><a onclick="javascript:showListToponims();" href="#">...</a></li>');
        }
    };

    var uploader = new qq.FileUploader({
        action: _ajax_upload_url,
        element: $('#fileuploader')[0],
        multiple: false,
        onComplete: function(id, fileName, responseJSON) {
            if(responseJSON.success) {
                //alert("success!");
                var path = responseJSON.path.replace("media//","/");
                importa_shapefile(path);
                //importa_shapefile(responseJSON.path);
            } else {
                alert('upload failed!');
            }
        },
        template:'<div class="qq-uploader">' +
            '<div class="qq-upload-drop-area"><span>Importar shapefile</span></div>' +
            '<div class="qq-upload-button ui-widget-content ui-button ui-corner-all ui-state-default">Importar shapefile</div>' +
            '<ul class="qq-upload-list"></ul>' +
            '</div>',
        params: {
            'csrf_token': csrf_token,
            'csrf_name': 'csrfmiddlewaretoken',
            'csrf_xname': 'X-CSRFToken',
        }
    });

    var connectwms = function(url){
        $('#wms_connect').prop('disabled', true);
        $('#wms_connect').addClass("asyncload");
        $.ajax({
            url: _wms_metadata_url,
            data: 'url=' + encodeURI(url),
            method: 'GET',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                $('#layersWms').empty();
                resultat = data.detail;
                for(var i = 0; i < resultat.length; i++){
                    $('#layersWms').append('<option data-id='+resultat[i].id+' data-xmin='+resultat[i].minx+' data-xmax='+resultat[i].maxx+' data-ymin='+resultat[i].miny+' data-ymax='+resultat[i].maxy+' value='+resultat[i].name+'>' + resultat[i].title + '</option>');
                }
                $('#wms_connect').prop('disabled', false);
                $('#wms_connect').removeClass("asyncload");
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error('Error connectant a servei wms:' + jqXHR.responseJSON.detail);
                $('#wms_connect').prop('disabled', false);
                $('#wms_connect').removeClass("asyncload");
            }
        });
    }

    var importa_shapefile = function(filepath){
        $.ajax({
            url: _import_shapefile_url,
            data: 'path=' + encodeURI(filepath),
            method: 'GET',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                djangoRef_map.editableLayers.clearLayers();
                var geoJson = JSON.parse(data.detail);
                var geoJSONLayer = L.geoJson(geoJson);
                geoJSONLayer.eachLayer(
                    function(l){
                        djangoRef_map.editableLayers.addLayer(l);
                    }
                );
                refreshDigitizedGeometry();
                djangoRef_map.editableLayers.bringToFront();
                if(djangoRef_map.editableLayers.getBounds().isValid()){
                    djangoRef_map.map.fitBounds(djangoRef_map.editableLayers.getBounds());
                }
                toastr.success('Importació amb èxit!');
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error('Error important fitxer:' + jqXHR.responseJSON.detail);
            }
        });
    };

    init_toponims_basats_recurs();

    var target = $('#toponimsbasats');

    $( "#dialogListToponims" ).dialog({
        autoOpen: false,
        show: "blind",
        hide: "explode",
        height: 400,
        width: 350
    });

    var toponims_b_recurs =  {
        name: 'toponims_b_recurs',
        layer : L.tileLayer.wms(
            wms_url,
            {
                layers: 'mzoologia:toponimsbasatsenrecurs',
                format: 'image/png',
                transparent: true,
                CQL_FILTER: cql_filter_ini
            }
        )
    };

    var overlay_list = [];
    overlay_list.push(toponims_b_recurs);

    var overlays_control_config = [
        {
            groupName: 'Toponims',
            expanded: true,
            layers: {
                'Topònims basats en recurs': toponims_b_recurs.layer
            }
        }
    ];

    map_options = {
        editable:true,
        consultable: true,
        show_centroid_after_edit: false,
        show_coordinates: false,
        overlays: overlay_list,
        overlays_control_config: overlays_control_config,
        wms_url: wms_url
    };

    map_options.consultable = [toponims_b_recurs.layer];

    var toponimsbasatsenrecurs_formatter = function(data){
        var html = '';
        html += '<style type="text/css">li.titol {font-size: 80%;padding:2px; } li.text {font-size: 100%;padding:2px;} a.linkFitxa{color:#00008B;text-align:right;padding:2px;} table.contingut{font-size: 80%;width:100%;} th, td {border: none;} td.atribut {text-align:right;vertical-align:top;padding:2px;} td.valor {text-align:left;padding:2px;} th.aladreta{text-align:right;padding:2px;} th.alesquerra{text-align:left;padding:2px;}</style>';
        html += '<table class="contingut"><tbody>';
        html += '<tr><th class="alesquerra">Topònims basats en recurs</th>';
        html += '<tr><td class="atribut">Nom del topònim : </td><td class="valor">' + data.properties.nom + '</td></tr>';
        html += '<tr><td class="atribut">Nom del recurs : </td><td class="valor">' + data.properties.nomrecurs + '</td></tr>';
        html += '</tbody></table></br>';
        return html;
    }

    map_options.formatters = {
        'toponimsbasatsenrecurs' : toponimsbasatsenrecurs_formatter
    };

    map_options.state = {
        overlays: [toponims_b_recurs.name],
        base: 'djangoRef.Map.roads',
        view:{ center:new L.LatLng(40.58, -3.25),zoom:2}
    };

    djangoRef_map = new djangoRef.Map.createMap(map_options);

    djangoRef_map.map.on(L.Draw.Event.CREATED, function (e) {
        refreshDigitizedGeometry();
    });

    djangoRef_map.map.on(L.Draw.Event.EDITED, function (e) {
        refreshDigitizedGeometry();
    });

    djangoRef_map.map.on(L.Draw.Event.DELETED, function (e) {
        refreshDigitizedGeometry();
    });

    var geoJSONLayer = L.geoJson(geometries_json);
    geoJSONLayer.eachLayer(
        function(l){
            djangoRef_map.editableLayers.addLayer(l);
        }
    );

    refreshDigitizedGeometry();
    djangoRef_map.editableLayers.bringToFront();
    if(djangoRef_map.editableLayers.getBounds().isValid()){
        djangoRef_map.map.fitBounds(djangoRef_map.editableLayers.getBounds());
    }

    $('#wms_connect').click(function(){
        var url = $('#id_base_url_wms').val();
        connectwms(url);
    });

    $('#wms_add').click(function(){
        var selected = $('#layersWms').find(":selected");
        var id = selected.attr('data-id');
        var ids = get_capawms_ids();
        if(ids.indexOf(id) == -1){
            var new_template = capawms_li_element_template.replace('###label',selected.text());
            new_template = new_template.replace('###id',id);
            $('#taulacapes').append(new_template);
        }
        $('#capeswms').val(get_capawms_ids());
    });

    $(document).on('click','a.close-capawms',function(){
        var a = $(this);
        var li = a.parent();
        var ul = li.parent();
        li.remove();
        $('#capeswms').val(get_capawms_ids());
    });

    var url = $('#id_base_url_wms').val();
    if(url != '' && url != null){
        connectwms(url);
    }

});