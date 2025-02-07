var sidebar;

var exportXLS = function(){
    var params = table.ajax.params();
    window.location.href = _recursos_list_xls + '?' + jQuery.param(params);
}

var exportCSV = function(){
    var params = table.ajax.params();
    window.location.href = _recursos_list_csv + '?' + jQuery.param(params);
};

var exportPDF = function(){
    var params = table.ajax.params();
    window.location.href = _recursos_list_pdf + '?' + jQuery.param(params);
};

$(document).ready(function() {
    table = $('#recursos_list').DataTable( {
        'ajax': {
            'url': _recurs_list_url,
            'dataType': 'json',
            'data': function(d){
                var valorFiltre = getCookie('filtre_r');
                if(valorFiltre){
                    d.filtrejson = valorFiltre;
                }else{
                    d.filtrejson = extreureJSONDeFiltre();
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
        //"dom": '<"toolbar"><"top"iflp<"clear">>rt<"bottom"iflp<"clear">>',
        'dom': '<"top"iflp<"clear">>rt<"bottom"iflp<"clear">>',
        stateSaveCallback: function(settings,data) {
            localStorage.setItem( 'DataTables_' + settings.sInstance, JSON.stringify(data) );
        },
        stateLoadCallback: function(settings) {
            return JSON.parse( localStorage.getItem( 'DataTables_' + settings.sInstance ) );
        },
        'columns': [
            { 'data': 'nom' }
        ],
        'columnDefs': [
            {
                'targets': 1,
                'data': 'deletable',
                'sortable': false,
                'render': function(value){
                    if(value==true){
                        return '<button class="delete_button btn btn-danger"><i class="fa fa-times" aria-hidden="true"></i></button>';
                    }else{
                        return '&nbsp;';
                    }
                }
            },
            {
                'targets': 2,
                'data': 'editable',
                'sortable': false,
                'render': function(value){
                    return '<button class="edit_button btn btn-info"><i class="fa fa-pencil-square-o" aria-hidden="true"></i></button>';
                }
            },
            {
                'targets':0,
                'title': gettext('Nom recurs')
            }
        ]
    } );

    var check_nomfiltre = function(){
        var json = extreureJSONDeFiltre();
        var nomfiltre = $('#autoc_filtres').val();
        var modul = 'RECURSOS';
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
                //scrollToTableTop();
            },
            error: function(jqXHR, textStatus, errorThrown){
                var idfiltre = jqXHR.responseJSON.detail;
                $( '#dialog-confirm' ).dialog({
                    resizable: false,
                    height: 'auto',
                    width: 400,
                    modal: true,
                    buttons: {
                        'Sobreescriure i filtrar': function() {
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

    $( '#addRecurs' ).click(function() {
        var url = '/recursos/create/';
        window.location.href = url;
    });

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
                toastr.success('Filtre actualitzat amb èxit!');
                filter();
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error('Error actualitzant filtre');
            }
        });
    };

    var delete_recurs = function(id){
        $.ajax({
            url: _recurs_delete_url + id + "/",
            method: 'DELETE',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                toastr.success('Recurs esborrat amb èxit!');
                table.ajax.reload();
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error('Error esborrant recurs');
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
                toastr.success('Filtre esborrat amb èxit!');
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error('Error esborrant');
            }
        });
    };

    var confirmDialog = function(message,id){
        $('<div></div>').appendTo('body')
            .html('<div><h6>'+message+'</h6></div>')
            .dialog({
                modal: true, title: 'Esborrant recurs...', zIndex: 10000, autoOpen: true,
                width: 'auto', resizable: false,
                buttons: {
                    Yes: function () {
                        delete_recurs(id);
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

    $('#recursos_list tbody').on('click', 'td button.delete_button', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
        var id = row.data().id;
        confirmDialog("Segur que vols esborrar?",id);
    });

    $('#recursos_list tbody').on('click', 'td button.edit_button', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
        var id = row.data().id;
        url = '/recursos/update/' + id;
        window.location.href = url;
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
                toastr.success('Filtre desat amb èxit!');
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error('Error desant filtre!');
            }
        });
    };

    $( '#autoc_filtres' ).autocomplete({
        source: function(request,response){
            $.getJSON( _filtres_list_url + '?modul=RECURSOS&term=' + request.term, function(data){
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
            var listname = ui.item.label;
            crearTaulaFiltre(ui.item.json);
            var activeOverlays = djangoRef.Map.getActiveOverlays();
            for(var i = 0; i < activeOverlays.length; i++){
                var layer = activeOverlays[i];
                filterCQL(ui.item.json,layer);
            }
            $('#autoc_filtres').val(listname);
            return false;
        }
    });

    $( '#saveDoFilter' ).click(function() {
        var nomfiltre = $('#autoc_filtres').val();
        if (nomfiltre === '' || nomfiltre === null){
            toastr.error("El nom de filtre està en blanc. Cal posar un nom vàlid.");
        }else{
            var jsonFiltre = extreureJSONDeFiltre();
            var json = JSON.parse(jsonFiltre);
            if(json.filtre.length == 0){
                toastr.error("El filtre no té condicions, està en blanc. Tria alguns criteris i torna-ho a intentar.");
            }else{
                check_nomfiltre();
            }
        }
    });

    $( '#doFilter' ).click(function() {
        filter();
        //scrollToTableTop();
    });

    $( '#doClear' ).click(function() {
        clearTaula('taulafiltre');
        map.editableLayers.clearLayers();
        filter();
        $('#autoc_filtres').val('');
    });

    var scrollToTableTop = function() {
        $('html, body').animate({scrollTop: $("#recursos_list_wrapper").offset().top - 100}, 500);
    };
        

    var recursos =  {
        name: 'recursos',
        layer : L.tileLayer.wms(
            wms_url,
            {
                layers: 'mzoologia:recursosgeoreferenciacio',
                format: 'image/png',
                transparent: true,
                opacity: 0.4
            }
        )
    };

    var overlay_list = [];
    overlay_list.push(recursos);
    var recurs_key = gettext('Recursos de georeferenciació (límits digitalitzats)');
    var layers_obj = {};
    layers_obj[recurs_key] = recursos.layer;

    var overlays_control_config = [
        {
            groupName: gettext('Recursos de georeferenciació'),
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
        attribution_position: 'bottomleft'
    };

    var recursosgeoreferenciacio_formatter = function(data){
        var html = '';
        html += '<style type="text/css">li.titol {font-size: 80%;padding:2px; } li.text {font-size: 100%;padding:2px;} a.linkFitxa{color:#00008B;text-align:right;padding:2px;} table.contingut{font-size: 80%;width:100%;} th, td {border: none;} td.atribut {text-align:right;vertical-align:top;padding:2px;} td.valor {text-align:left;padding:2px;} th.aladreta{text-align:right;padding:2px;} th.alesquerra{text-align:left;padding:2px;}</style>';
        html += '<table class="contingut"><tbody>';
        html += '<tr><th class="alesquerra">' + gettext('Recursos de georeferenciació (límits digitalitzats)') + '</th>';
        html += '<tr><td class="atribut">' + gettext('Nom recurs') + ' : </td><td class="valor">' + data.properties.nom + '</td></tr>';
        html += '<tr><td class="atribut">' + gettext('Acrònim') + ' : </td><td class="valor">' + data.properties.acronim + '</td></tr>';
        html += '</tbody></table></br>';
        return html;
    }

    map_options.formatters = {
        'recursosgeoreferenciacio' : recursosgeoreferenciacio_formatter
    };

    var valorView = getCookie('view_r');
    if(valorView){
        var jsonView = JSON.parse(valorView);
        map_options.center = jsonView.center;
        map_options.zoom = jsonView.zoom;
    }

    var valorEstat = getCookie('layers_r');
    if(valorEstat){
        var jsonState = JSON.parse(valorEstat);
        map_options.state = jsonState;
    }else{
        map_options.state = {
            overlays: [recursos.name],
            base: 'djangoRef.Map.roads',
            view:{ center:new L.LatLng(40.58, -3.25),zoom:2}
        };
    }

    map_options.consultable = [recursos.layer];

    map = new djangoRef.Map.createMap(map_options);

    upload_component = new djangoRef.FileUploader.createFileUploader({internal_map: map});

    sidebar = L.control.sidebar('sidebar',{position:'right'}).addTo(map.map);

    //$('[data-toggle="tooltip"]').tooltip();
    sidebar.on('opening', function(e) {
        setCookie('sb_r', 'open');
    });

    sidebar.on('closing', function(e) {
        setCookie('sb_r', 'closed');
    });

    var open = getCookie('sb_r');
    if(open != '' && open == 'open'){
        sidebar.open('home');
    }
});

$(window).bind('beforeunload', function(){
    var state = djangoRef.Map.getState();
    var state_string = JSON.stringify(state);
    setCookie('layers_r', state_string);
    var view = {};
    var center = djangoRef.Map.getCenter();
    var zoom = djangoRef.Map.getZoom();
    view = {center: center, zoom: zoom};
    var view_string = JSON.stringify(view);
    setCookie('view_r', view_string);
});
