var sidebar;
var zoom_to_extent = false;

var exportPDF = function(){
    var params = table.ajax.params();
    window.location.href = _toponims_list_pdf + '?' + jQuery.param(params);
};

var exportCSV = function(){
    var params = table.ajax.params();
    window.location.href = _toponims_list_csv + '?' + jQuery.param(params);
};

var exportXLS = function(){
    var params = table.ajax.params();
    window.location.href = _toponims_list_xls + '?' + jQuery.param(params);
}

var exportKML = function(){
    var filtrejson = extreureJSONDeFiltre();
    if(filtrejson!=null && filtrejson!=''){
        var cql = transformarJSONACQL(filtrejson);
        var cql_filter_text = 'TRUE=TRUE';
        if(cql != null){
            cql_filter_text = new OpenLayers.Format.CQL().write(cql);
        }
        document.kml.CQL_FILTER.value = cql_filter_text;
    }else{
        document.kml.CQL_FILTER.value = "TRUE=TRUE";
    }
    document.kml.submit();
}

var exportSHP = function(){
    var filtrejson = extreureJSONDeFiltre();
    if(filtrejson!=null && filtrejson!=''){
        var cql = transformarJSONACQL(filtrejson);
        var cql_filter_text = 'TRUE=TRUE';
        if(cql != null){
            cql_filter_text = new OpenLayers.Format.CQL().write(cql);
        }
        document.shp.CQL_FILTER.value = cql_filter_text;
    }else{
        document.shp.CQL_FILTER.value = "TRUE=TRUE";
    }
    document.shp.submit();
}

$(document).ready(function() {
    table = $('#toponims_list').DataTable( {
        'ajax': {
            'url': _toponim_list_url,
            'dataType': 'json',
            'dataSrc': function(json){
                if(zoom_to_extent == true){
                    //const bounds = [ [ json.extent[1],json.extent[0] ], [ json.extent[3],json.extent[2] ] ];
                    const corner_min = L.latLng( json.extent[1],json.extent[0] );
                    const corner_max = L.latLng( json.extent[3],json.extent[2] );
                    const bounds = L.latLngBounds([ corner_min, corner_max ]);
                    if(bounds.isValid()){
                        djangoRef.Map.map.fitBounds(bounds);
                    }
                    //map.map.fitBounds();
                    zoom_to_extent = false;
                }
                return json.data;
            },
            'data': function(d){
                var valorFiltre = getCookie('filtre_t');
                var valorOrg = getCookie('torg' + current_user_id);
                if(valorFiltre){
                    if(valorOrg == ''){
                        d.filtrejson = valorFiltre;
                    }else{
                        //Add org filter condition
                        var filtreJson = JSON.parse(valorFiltre);
                        if ( filtreJson.filtre.length > 0 ){
                            filtreJson.filtre.push( { "condicio":"org", "not":"", "operador":"and", "text_valor":"", "valor":valorOrg } );
                        }else{
                            filtreJson.filtre.push( { "condicio":"org", "not":"", "operador":"", "text_valor":"", "valor":valorOrg } );
                        }
                        d.filtrejson = JSON.stringify(filtreJson);
                    }
                }else{
                    if(valorOrg == '' || valorOrg != current_user_idorg){
                        d.filtrejson = extreureJSONDeFiltre();
                    }else{
                        //Add org filter condition
                        var filtreJson = JSON.parse(valorFiltre);
                        if ( filtreJson.filtre.length > 0 ){
                            filtreJson.filtre.push( { "condicio":"org", "not":"", "operador":"and", "text_valor":"", "valor":valorOrg } );
                        }else{
                            filtreJson.filtre.push( { "condicio":"org", "not":"", "operador":"", "text_valor":"", "valor":valorOrg } );
                        }
                        d.filtrejson = JSON.stringify(filtreJson);
                    }
                }
            }
        },
        'serverSide': true,
        'processing': true,
        "language": opcions_llenguatge,
        'pageLength': 25,
        'pagingType': 'full_numbers',
        'bLengthChange': false,
        stateSave: true,
        'dom': '<"top"iflp<"clear">>rt<"bottom"iflp<"clear">>',
        stateSaveCallback: function(settings,data) {
            localStorage.setItem( 'DataTables_' + settings.sInstance, JSON.stringify(data) );
        },
        stateLoadCallback: function(settings) {
            return JSON.parse( localStorage.getItem( 'DataTables_' + settings.sInstance ) );
        },
        'columns': [
            { 'data': 'nom_str' }
            ,{ 'data': 'aquatic_str' }
            ,{ 'data': 'idtipustoponim.nom' }
            ,{ 'data': 'idorganization.name' }
        ],
        'columnDefs': [
            {
                'targets': 4,
                'data': 'deletable',
                'sortable': false,
                'render': function(value){
                    if(value==true){
                        return '<button class="delete_button btn btn-sm btn-danger"><i class="fa fa-times" aria-hidden="true"></i></button>';
                    }else{
                        return '&nbsp;';
                    }
                }
            },
            {
                'targets': 5,
                'data': 'editable',
                'sortable': false,
                'render': function(value){
                    if(value){
                        return '<button class="edit_button btn btn-sm btn-info"><i class="fa fa-pencil-square-o" aria-hidden="true"></i></button>';
                    }else{
                        return '&nbsp;';
                    }
                }
            },
            {
                'targets': 6,
                'data': 'coords_centroide',
                'sortable': false,
                'render': function(value){
                    if(value){
                        return '<button class="lookup_button btn btn-sm btn-info"><i class="fa fa-binoculars" aria-hidden="true"></i></button>';
                    }else{
                        return '&nbsp;';
                    }
                }
            },
            {
                'targets':0,
                'title': gettext('Topònim')
            },
            {
                'targets':1,
                'title': gettext('Aquàtic')
            },
            {
                'targets':2,
                'title': gettext('Tipus')
            },
            {
                'targets':3,
                'title': gettext('Organització'),
                'render': function(value){
                    if(value){
                        //console.log(value);
                        return value;
                    }else{
                        return gettext('No assignada');
                        //console.log(value);
                    }
                }
            }
        ]
    } );


    $( '#autoc_filtres' ).autocomplete({
        source: function(request,response){
            $.getJSON( _filtres_list_url + '?modul=TOPONIMS&term=' + request.term, function(data){
                response($.map(data.results, function(item){
                    return {
                        label: item.nomfiltre,
                        value: item.idfiltre,
                        json: item.json
                    };
                }));
            });
        },
        minLength: 2,
        select: function( event, ui ) {
            //log( "Selected: " + ui.item.value + " aka " + ui.item.id );
            var listname = ui.item.label;
            crearTaulaFiltre(ui.item.json);
            var activeOverlays = djangoRef.Map.getActiveOverlays();
            for(var i = 0; i < activeOverlays.length; i++){
                var layer = activeOverlays[i];
                filterCQL(ui.item.json,layer);
            }
            $('#autoc_filtres').val(listname);
            filter();
            return false;
        }
    });

    var add_filtre = function(json,modul,nomfiltre){
        var data = {
            'json': json,
            'modul': modul,
            'nomfiltre': nomfiltre
        };
        $.ajax({
            url: _filtres_create_url,
            method: 'POST',
            data: data,
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                toastr.success(gettext('Filtre desat amb èxit!'));
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error(gettext('Error afegint filtre!'));
            }
        });
    };

    var update_filtre = function(json, nomfiltre, idfiltre, modul){
        var data = {
            'json': json,
            'modul': modul,
            'nomfiltre': nomfiltre
        };
        $.ajax({
            url: _filtres_update_url + idfiltre + '/',
            data: data,
            method: 'PUT',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                toastr.success(gettext('Filtre actualitzat amb èxit!'));
                filter();
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error(gettext('Error actualitzant filtre'));
            }
        });
    };

    var delete_filtre = function(id){
        $.ajax({
            url: _filtres_delete_url + id + "/",
            method: 'DELETE',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                toastr.success(gettext('Filtre esborrat amb èxit!'));
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error(gettext('Error esborrant'));
            }
        });
    };

    var confirmDialog = function(message,id){
        $('<div></div>').appendTo('body')
            .html('<div><h6>'+message+'</h6></div>')
            .dialog({
                modal: true, title: gettext('Esborrant topònim...'), zIndex: 10000, autoOpen: true,
                width: 'auto', resizable: false,
                position:['left',20],
                buttons: {
                    Yes: function () {
                        delete_toponim(id);
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

    var check_nomfiltre = function(){
        var json = extreureJSONDeFiltre();
        var nomfiltre = $('#autoc_filtres').val();
        var modul = 'TOPONIMS';
        var label_sobreescriure_i_filtrar = gettext('Sobreescriure i filtrar');
        $.ajax({
            url: _check_filtre_url,
            data: 'nomfiltre=' + encodeURI(nomfiltre) + "&modul=" + modul,
            method: 'GET',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                add_filtre(json,modul,nomfiltre);
            },
            error: function(jqXHR, textStatus, errorThrown){
                var idfiltre = jqXHR.responseJSON.detail;
                $( '#dialog-confirm' ).dialog({
                    resizable: false,
                    height: 'auto',
                    width: 400,
                    modal: true,
                    buttons: {
                        Ok: function() {
                            update_filtre(json,nomfiltre,idfiltre,modul);
                            $( this ).dialog( 'close' );
                        },
                        Cancel: function() {
                            $( this ).dialog( 'close' );
                        }
                    }
                });
            }
        });
    };

    var delete_toponim = function(id){
        $.ajax({
            url: _toponim_delete_url + id + '/',
            method: 'DELETE',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                toastr.success(gettext('Topònim esborrat amb èxit!'));
                table.ajax.reload();
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error(gettext('Error esborrant topònim'));
            }
        });
    };

    $('#toponims_list tbody').on('click', 'td button.delete_button', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
        var id = row.data().id;
        if(id != '0'){
            confirmDialog(gettext("S'esborrarà el topònim '") + row.data().nom_str + gettext("' i totes les seves versions i informació associada! Segur que vols continuar?"),id);
        }
    });

    $('#toponims_list tbody').on('click', 'td button.edit_button', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
        var id = row.data().id;
        url = '/toponims/update/' + id + '/-1';
        window.location.href = url;
    });

    $('#toponims_list tbody').on('click', 'td button.lookup_button', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
        /*var coords = row.data().coords_centroide;
        map.map.setView( { lon:coords.x,lat:coords.y }, 10 );*/
        map.highLightVersion( row.data().id );
    });

    $( '#saveDoFilter' ).click(function() {
        var nomfiltre = $('#autoc_filtres').val();
        if (nomfiltre === '' || nomfiltre === null){
            toastr.error(gettext("El nom de filtre està en blanc. Cal posar un nom vàlid."));
        }else{
            var jsonFiltre = extreureJSONDeFiltre();
            var json = JSON.parse(jsonFiltre);
            if(json.filtre.length == 0){
                toastr.error(gettext("El filtre no té condicions, està en blanc. Tria alguns criteris i torna-ho a intentar."));
            }else{
                check_nomfiltre();
            }
        }
    });

    var scrollToTableTop = function() {
        $('html, body').animate({scrollTop: $("#toponims_list_wrapper").offset().top - 100}, 500);
    };

    $( '#doFilter' ).click(function() {
        zoom_to_extent = true;
        filter();
        //scrollToTableTop();
    });

    $( '#doClear' ).click(function() {
        zoom_to_extent = false;
        clearTaula('taulafiltre');
        map.editableLayers.clearLayers();
        if(map.highLightLayer){
            map.highLightLayer.clearLayers();
        }
        filter();
        $('#autoc_filtres').val('');
    });

    $( '#addToponim' ).click(function() {
        var url = '/toponims/create/';
        window.location.href = url;
    });

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
    var toponim_key = gettext('Topònims');
    var layers_obj = {};
    layers_obj[toponim_key] = toponims.layer;

    var overlays_control_config = [
        {
            groupName: gettext('Topònims'),
            expanded: true,
            layers: layers_obj
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

    /* Move control capes to bottom left position */
    var controlcapes_options = {
        position: "bottomleft"
    };

    /* Move coordinates to bottom left position */
    var coordinates_options = {
        position:"bottomleft"
    };

    map_options = {
        editable:true,
        overlays: overlay_list,
        overlays_control_config: overlays_control_config,
        controlcapes_options: controlcapes_options,
        coordinates_options: coordinates_options,
        wms_url: wms_url,
        attribution_position: 'bottomleft',
        highlight: true
    };

    var toponimsdarreraversio_formatter = function(data){
        var html = '';
        html += '<style type="text/css">li.titol {font-size: 80%;padding:2px; } li.text {font-size: 100%;padding:2px;} a.linkFitxa{color:#00008B;text-align:right;padding:2px;} table.contingut{font-size: 80%;width:100%;} th, td {border: none;} td.atribut {text-align:right;vertical-align:top;padding:2px;} td.valor {text-align:left;padding:2px;} th.aladreta{text-align:right;padding:2px;} th.alesquerra{text-align:left;padding:2px;}</style>';
        html += '<table class="contingut"><tbody>';
        html += '<tr><th class="alesquerra">' + gettext('Topònims') + '</th>';
        html += '<tr><td class="atribut">' + gettext('Nom topònim') + ' : </td><td class="valor">' + data.properties.nomtoponim + '</td></tr>';
        html += '<tr><td class="atribut">' + gettext('Aquàtic') + '? : </td><td class="valor">' + data.properties.aquatic + '</td></tr>';
        html += '<tr><td class="atribut">' + gettext('Tipus de topònim') + ' : </td><td class="valor">' + data.properties.tipustoponim + '</td></tr>';
        html += '<tr><td class="atribut">' + gettext('Número de versió') + ' : </td><td class="valor">' + data.properties.numero_versio + '</td></tr>';
        html += '</tbody></table></br>';
        return html;
    }

    map_options.formatters = {
        'toponimsdarreraversio' : toponimsdarreraversio_formatter
    };

    map_options.consultable = [toponims.layer];

    var valorView = getCookie('view_t');
    if(valorView){
        var jsonView = JSON.parse(valorView);
        map_options.center = jsonView.center;
        map_options.zoom = jsonView.zoom;
    }

    var valorEstat = getCookie('layers_t');
    if(valorEstat){
        var jsonState = JSON.parse(valorEstat);
        map_options.state = jsonState;
    }else{
        map_options.state = {
            overlays: [toponims.name],
            base: 'djangoRef.Map.roads',
            view:{ center:new L.LatLng(40.58, -3.25),zoom:2}
        };
    }

    map_options.consultable = [toponims.layer];

    map = new djangoRef.Map.createMap(map_options);

    upload_component = new djangoRef.FileUploader.createFileUploader({internal_map: map});

    $('.btn.btn-default.sometbtn').click( function(e) {
        $('.btn-group').find('.btn').toggleClass('active');
        setCookie('torg' + current_user_id,$(this).data('idorg'));
        filter();
    });

    $('.btn.btn-default.alltbtn').click( function(e) {
        $('.btn-group').find('.btn').toggleClass('active');
        setCookie('torg' + current_user_id,'');
        filter();
    });

    var idorg = getCookie('torg'  + current_user_id);
    if( idorg != '' ){
        $('.btn.btn-default.sometbtn').addClass('active');
        $('.btn.btn-default.alltbtn').removeClass('active');
    }

    setTimeout(function(){ filterMap(); }, 1000);

    sidebar = L.control.sidebar('sidebar',{position:'right'}).addTo(map.map);

    sidebar.on('opening', function(e) {
        setCookie('sb_t', 'open');
    });

    sidebar.on('closing', function(e) {
        setCookie('sb_t', 'closed');
    });

    var open = getCookie('sb_t');
    if(open != '' && open == 'open'){
        sidebar.open('home');
    }

});

$(window).bind('beforeunload', function(){
    var state = djangoRef.Map.getState();
    var state_string = JSON.stringify(state);
    setCookie('layers_t', state_string);
    var view = {};
    var center = djangoRef.Map.getCenter();
    var zoom = djangoRef.Map.getZoom();
    view = {center: center, zoom: zoom};
    var view_string = JSON.stringify(view);
    setCookie('view_t', view_string);
});
