var counter = 0;
var node_load_callback = function(node,status){
    counter=counter+1;
    if(counter < node_list.length ){
        if(!this.is_loaded(node_list[counter])){
            this.load_node(node_list[counter],node_load_callback);
        }
    }
    //This condition should only activate on second-to-last node
    if(counter == node_list.length - 1){
        //true/true avoids full selection when selecting deepest node
        this.select_node(node_list[counter],true,false);
        //From deepest node upwards, expand folders
        for(var i = node_list.length-2 ; i >= 0; i--){
            this.open_node(node_list[i]);
        }
    }
};

var init_ariadna = function(nodes){
    $('#ariadna ul').empty();
    for(var i = 0; i < nodes.length; i++){
        var id = nodes[i].split('$')[0];
        var nom = nodes[i].split('$')[1];
        var linkVisualitzar;
        if(i == 0){
            linkVisualitzar = '<li><a href="/toponims/update/' + id + '/-1" title="'+nom+'">' + nom + '</a></li>';
        }else{
            linkVisualitzar = '<li><a href="/toponims/update/' + id + '/-1" title="'+nom+'"> <- ' + nom + '</a></li>';
        }
        $('#ariadna ul').append(linkVisualitzar);
    }
};

var confirmDialog = function(message,id){
        $('<div></div>').appendTo('body')
            .html('<div><h6>'+message+'</h6></div>')
            .dialog({
                modal: true, title: 'Esborrant versió...', zIndex: 10000, autoOpen: true,
                width: 'auto', resizable: false,
                buttons: {
                    Yes: function () {
                        delete_versio(id);
                        $(this).dialog("close");
                    },
                    No: function () {
                        $(this).dialog("close");
                    }
                },
                close: function (event, ui) {
                    $(this).remove();
                }
        });
    };

var delete_versio = function(id){
    $.ajax({
        url: _versio_delete_url + id,
        method: "DELETE",
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                var csrftoken = getCookie('csrftoken');
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        success: function( data, textStatus, jqXHR ) {
             toastr.success("Versió esborrada amb èxit!");
             $('table#versions tr#' + id).remove();
             window.location.href = _last_version_url;
        },
        error: function(jqXHR, textStatus, errorThrown){
            toastr.error("Error esborrant la versió");
        }
    });
};

var refreshDigitizedGeometry = function(){
    var geometry = djangoRef.Map.editableLayers.toGeoJSON()
    var json_string = JSON.stringify(geometry);
    $('#geometria').val( json_string );
};


var refreshCentroidUI = function(radius_m){
    var centroid_data = djangoRef.Map.getCurrentCentroid();
    if(centroid_data != null){
        $('#id_coordenada_x_centroide').val( centroid_data.centroid.geometry.coordinates[0] );
        $('#id_coordenada_y_centroide').val( centroid_data.centroid.geometry.coordinates[1] );
        if(radius_m){
            $('#id_precisio_h').val(radius_m);
        }else{
            $('#id_precisio_h').val(centroid_data.radius * 1000);
        }
    }else{
        $('#id_coordenada_x_centroide').val( '' );
        $('#id_coordenada_y_centroide').val( '' );
        $('#id_precisio_h').val( '' );
    }
};

$(document).ready(function() {

    function updateTips( t, class_name ) {
        var tips = $( "." + class_name );
        tips.text( t ).addClass( "ui-state-highlight" );
        setTimeout(function() {
            tips.removeClass( "ui-state-highlight", 1500 );
        }, 500 );
    }

    function checkLat( control, error_message, tipsclass ) {
        var latValue = parseFloat(control.val());
        if (0 <= latValue && latValue <= 90){
            control.removeClass( "ui-state-error" );
            return true;
        }else{
            control.addClass( "ui-state-error" );
            updateTips( error_message, tipsclass );
        }
    }

    function checkLong( control, error_message, tipsclass ) {
        var longValue = parseFloat(control.val());
        if (-180 <= longValue && longValue <= 180){
            control.removeClass( "ui-state-error" );
            return true;
        }else{
            control.addClass( "ui-state-error" );
            updateTips( error_message, tipsclass );
        }
    }

    function checkRegexp( o, regexp, n, tipsclass ) {
      if ( !( regexp.test( o.val() ) ) ) {
        o.addClass( "ui-state-error" );
        updateTips( n, tipsclass );
        return false;
      } else {
        o.removeClass( "ui-state-error" );
        return true;
      }
    }

    function enterMarkerUncertaintyRadius () {
        var valid = true;
        //Draw centroid
        var radius = $('#radi').val();
        var radius_ctrl = $('#radi');
        valid = valid && checkRegexp(radius_ctrl, /^[+-]?\d+(\.\d+)?$/ , 'Cal posar un nombre decimal o enter vàlid. Si és decimal,  usar com a separador el caràcter ".". Per exemple, 206.57', "validateTips");
        if(valid){
            djangoRef_map.refreshCentroid(radius/1000);
            refreshCentroidUI(radius);
            refreshDigitizedGeometry();
            djangoRef_map.editableLayers.bringToFront();
            if(djangoRef_map.centroid.getBounds().isValid()){
                djangoRef_map.map.fitBounds(djangoRef_map.centroid.getBounds());
            }
            dialog_centroid.dialog( "close" );
        }
        return valid;
    };

    function digitizeViaKb (){
        var valid = true;
        var radius = $('#inc_radius_kb').val();
        var radius_ctrl = $('#inc_radius_kb');
        var coord_x = $('#coord_x_kb').val();
        var coord_x_ctrl = $('#coord_x_kb');
        var coord_y = $('#coord_y_kb').val();
        var coord_y_ctrl = $('#coord_y_kb');
        valid = valid && checkRegexp(radius_ctrl, /^[+-]?\d+(\.\d+)?$/ , 'Cal posar un nombre decimal o enter vàlid pel radi d\'incertesa. Si és decimal,  usar com a separador el caràcter ".". Per exemple, 206.57', "validateTipsKb");
        valid = valid && checkRegexp(coord_x_ctrl, /^[+-]?\d+(\.\d+)?$/ , 'Cal posar un nombre decimal o enter vàlid per la coordenada x. Si és decimal,  usar com a separador el caràcter ".". Per exemple, 206.57', "validateTipsKb");
        valid = valid && checkRegexp(coord_y_ctrl, /^[+-]?\d+(\.\d+)?$/ , 'Cal posar un nombre decimal o enter vàlid per la coordenada y. Si és decimal,  usar com a separador el caràcter ".". Per exemple, 206.57', "validateTipsKb");
        valid = valid && checkLat(coord_y_ctrl, 'La latitud no pot ser superior a 90 ni inferior a 0', "validateTipsKb");
        valid = valid && checkLong(coord_x_ctrl, 'La longitud no pot ser superior a 180 ni inferior a -180', "validateTipsKb");
        if(valid){
            //Draw geometry
            djangoRef.Map.editableLayers.clearLayers();
            var wkt = new Wkt.Wkt();
            wkt.read("POINT (" + coord_x + " " + coord_y + ")");
            var geoJson_point = wkt.toJson();
            var geoJSONLayer = L.geoJson(geoJson_point);
            geoJSONLayer.eachLayer(
                function(l){
                    djangoRef_map.editableLayers.addLayer(l);
                }
            );
            //Draw centroid
            djangoRef.Map.centroid.clearLayers();
            var centroid_data = djangoRef.Map.getCurrentCentroid();
            var circle = turf.circle(centroid_data.centroid,parseFloat(radius)/1000);
            djangoRef.Map.centroid.addData(circle);

            refreshCentroidUI(parseFloat(radius));
            refreshDigitizedGeometry();

            //Zoom on features
            djangoRef_map.editableLayers.bringToFront();
            if(djangoRef_map.centroid.getBounds().isValid()){
                djangoRef_map.map.fitBounds(djangoRef_map.centroid.getBounds());
            }

            //...and close dialog
            dialog_kb.dialog( "close" );
        }
        return valid;
    }

    var dialog_kb = $( "#dialog-digitize-kb").dialog({
        autoOpen: false,
        height: 300,
        width: 450,
        modal: true,
        buttons: {
            "Digitalitza": digitizeViaKb,
            Cancel: function() {
                dialog_kb.dialog( "close" );
            }
        },
        close: function() {
            $('#inc_radius_kb').val('');
            $('#coord_x_kb').val('');
            $('#coord_y_kb').val('');
        }
    });

    $('#kb_digit').click( function(e) {
        e.preventDefault();
        /*your_code_here;*/
        dialog_kb.dialog( "open" );
        return false;
    });

    var dialog_centroid = $( "#dialog-uncertainty-radius").dialog({
      autoOpen: false,
      height: 250,
      width: 400,
      modal: true,
      buttons: {
        "D'acord": enterMarkerUncertaintyRadius,
        Cancel: function() {
            dialog_centroid.dialog( "close" );
            djangoRef_map.editableLayers.clearLayers();
            djangoRef_map.centroid.clearLayers();
        }
      },
      close: function() {
        $('#radi').val('');
        /*djangoRef_map.editableLayers.clearLayers();
        djangoRef_map.centroid.clearLayers();*/
        //allFields.removeClass( "ui-state-error" );
      }
    });


    $('#jstree')
        .on('loaded.jstree', function(event, data) {
            if(node_list != null && node_list.length>1 && node_list[0]!='1'){
                data.instance.load_node(node_list[0],node_load_callback);
            }else{
                data.instance.select_node(node_list[0]);
            }
        })
        .on('select_node.jstree', function (e, data) {
            $('#id_idpare').val(data.instance.get_top_selected()[0]);
        })
        .on('deselect_node.jstree', function (e, data) {
            if(data.instance.get_top_selected().length > 1){
                //top_selected_node = "";
                $('#id_idpare').val('');
            }else{
                //top_selected_node = data.instance.get_top_selected()[0];
                $('#id_idpare').val(data.instance.get_top_selected()[0]);
            }
        })
        .jstree({
            'plugins' : [
                'checkbox'
            ],
            'core' : {
                'multiple' : false,
                'data' : {
                    'url' : function (node) {
                        return node.id === '#' ? '/toponimstree/' : '/toponimstree/?id=' + node.id;
                    },
                    'data' : function (node) {
                        if(node.id=='#'){
                            return { 'id' : node_ini };
                        }else{
                            return { 'id' : node.id };
                        }
                    }
                }
            }
        });

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
            '<div class="qq-upload-button ui-widget-content ui-button ui-corner-all ui-state-default"><span>Importar shapefile</span></div>' +
            '<ul class="qq-upload-list"></ul>' +
            '</div>',
        params: {
            'csrf_token': csrf_token,
            'csrf_name': 'csrfmiddlewaretoken',
            'csrf_xname': 'X-CSRFToken',
        }
    });

    var load_crs_label = function(id){
        $('#sistref_recurs').html("");
        $.ajax({
            url: _sistref_list_url,
            data: 'id=' + encodeURI(id),
            method: 'GET',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                if(data.detail == ''){
                    $('#sistref_recurs').html('Sistema de referència no especificat');
                }else{
                    $('#sistref_recurs').html(data.detail);
                }
            },
            error: function(jqXHR, textStatus, errorThrown){
                $('#sistref_recurs').html('');
            }
        });
    };

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
                if(geoJSONIsSinglePoint(geoJson)){
                    dialog_centroid.dialog("open");
                }else{
                    djangoRef_map.refreshCentroid();
                    refreshCentroidUI();
                    refreshDigitizedGeometry();
                    djangoRef_map.editableLayers.bringToFront();
                    if(djangoRef_map.centroid.getBounds().isValid()){
                        djangoRef_map.map.fitBounds(djangoRef_map.centroid.getBounds());
                    }
                    toastr.success('Importació amb èxit!');
                }

            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error('Error important fitxer:' + jqXHR.responseJSON.detail);
            }
        });
    };

    init_ariadna(node_list_full);

    /*$('#testbutton').click(function(){
        var checked = get_undetermined_nodes('#jstree');
        var top_selected = get_top_selected_node('#jstree');
        checked.push(top_selected);
    });*/

    var toponims =  {
        name: 'toponims',
        layer : L.tileLayer.wms(
            wms_url,
            {
                layers: 'mzoologia:toponimsdarreraversio',
                format: 'image/png',
                transparent: true
            }
        )
    };

    var overlay_list = [];
    overlay_list.push(toponims);

    var overlays_control_config = [
        {
            groupName: 'Toponims',
            expanded: true,
            layers: {
                'Topònims': toponims.layer
            }
        }
    ];

    for(var key in wmslayers){
        var added_layers = {};
        for(var i = 0; i < wmslayers[key].length; i++){
            layer_data_i = wmslayers[key][i];
            var layer_i = {
                name: layer_data_i.name,
                layer : L.tileLayer.wms(
                    layer_data_i.baseurlservidor + '?',
                    {
                        layers: layer_data_i.name,
                        format: 'image/png',
                        transparent: true,
                        opacity: 0.4
                    }
                )
            };
            layer_i.layer.on('tileerror', function(error, tile) {
                console.log(error);
            });
            added_layers[layer_data_i.label] = layer_i.layer;
        }
        overlays_control_config.push({
            groupName: key,
            expanded: true,
            layers: added_layers
        });
    }

    map_options = {
        editable:true,
        show_centroid_after_edit: true,
        overlays: overlay_list,
        overlays_control_config: overlays_control_config,
        wms_url: wms_url
    };

    map_options.state = {
        overlays: [toponims.name],
        base: 'djangoRef.Map.roads',
        view:{ center:new L.LatLng(40.58, -3.25),zoom:2}
    };

    var toponimsdarreraversio_formatter = function(data){
        var html = '';
        html += '<style type="text/css">li.titol {font-size: 80%;padding:2px; } li.text {font-size: 100%;padding:2px;} a.linkFitxa{color:#00008B;text-align:right;padding:2px;} table.contingut{font-size: 80%;width:100%;} th, td {border: none;} td.atribut {text-align:right;vertical-align:top;padding:2px;} td.valor {text-align:left;padding:2px;} th.aladreta{text-align:right;padding:2px;} th.alesquerra{text-align:left;padding:2px;}</style>';
        html += '<table class="contingut"><tbody>';
        html += '<tr><th class="alesquerra">Darreres versions de topònims</th>';
        html += '<tr><td class="atribut">Nom topònim : </td><td class="valor">' + data.properties.nomtoponim + '</td></tr>';
        html += '<tr><td class="atribut">Aquàtic? : </td><td class="valor">' + data.properties.aquatic + '</td></tr>';
        html += '<tr><td class="atribut">Tipus de topònim : </td><td class="valor">' + data.properties.tipustoponim + '</td></tr>';
        html += '<tr><td class="atribut">Número de versió : </td><td class="valor">' + data.properties.numero_versio + '</td></tr>';
        html += '</tbody></table></br>';
        return html;
    }

    map_options.formatters = {
        'toponimsdarreraversio' : toponimsdarreraversio_formatter
    };

    map_options.consultable = [toponims.layer];

    djangoRef_map = new djangoRef.Map.createMap(map_options);

    djangoRef_map.deselectAllOverlays();

    djangoRef_map.map.on(L.Draw.Event.CREATED, function (e) {
        var type = e.layerType,layer = e.layer;
        if(type=='marker'){
            //Prompt imprecision
            dialog_centroid.dialog("open");
        }else{
            refreshCentroidUI();
            refreshDigitizedGeometry();
        }
    });

    djangoRef_map.map.on(L.Draw.Event.EDITED, function (e) {
        var digitizedStuff = djangoRef_map.getDigitizedFeaturesJSON();
        if(digitizedStuff.features.length == 1 && digitizedStuff.features[0].geometry && digitizedStuff.features[0].geometry.type == 'Point'){
            dialog_centroid.dialog("open");
        }else{
            refreshCentroidUI();
            refreshDigitizedGeometry();
        }
    });

    djangoRef_map.map.on(L.Draw.Event.DELETED, function (e) {
        refreshCentroidUI();
        refreshDigitizedGeometry();
    });

    var geoJSONLayer = L.geoJson(geometries_json);
    geoJSONLayer.eachLayer(
        function(l){
            djangoRef_map.editableLayers.addLayer(l);
        }
    );
    if(stored_centroid_radius_m){
        djangoRef_map.refreshCentroid(stored_centroid_radius_m/1000);
    }else{
        djangoRef_map.refreshCentroid();
    }
    if(stored_centroid_radius_m){
        refreshCentroidUI(stored_centroid_radius_m);
    }else{
        refreshCentroidUI();
    }
    refreshDigitizedGeometry();
    djangoRef_map.editableLayers.bringToFront();
    if(djangoRef_map.centroid.getBounds().isValid()){
        djangoRef_map.map.fitBounds(djangoRef_map.centroid.getBounds());
    }

    $('[data-toggle="tooltip"]').tooltip();

    $( '#autoc_vcr' ).autocomplete({
        source: function(request,response){
            $.getJSON( _versio_capturada_url + '?term=' + request.term, function(data){
                response($.map(data.results, function(item){
                    return {
                        label: item.nom,
                        value: item.id,
                        json: item.json
                    };
                }));
            });
        },
        minLength: 2,
        select: function( event, ui ) {
            var listname = ui.item.label;
            load_crs_label(ui.item.value);
            $('#autoc_vcr').val(listname);
            $('#id_idrecursgeoref').val(ui.item.value);
            return false;
        }
    });
});