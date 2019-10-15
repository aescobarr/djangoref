$(document).ready(function() {

    $('#filename').val('');
    $('#id_nomcapa').val('');

    table = $('#capeswmslocal').DataTable( {
        "ajax": {
            "url": _capawmslocal_list_url,
            "dataType": 'json'
            ,"data": function(d){
                d.filtrejson = '{"filtre":[{"idrecurs":"mz_recursgeoref_r"}]}';
            }
        },
        "serverSide": true,
        "processing": true,
        "language": opcions_llenguatge,
        "pageLength": 25,
        "pagingType": "full_numbers",
        "bLengthChange": false,
        stateSave: true,
        "dom": '<"top"iflp<"clear">>rt<"bottom"iflp<"clear">>',
        stateSaveCallback: function(settings,data) {
            localStorage.setItem( 'DataTables_' + settings.sInstance, JSON.stringify(data) )
        },
        stateLoadCallback: function(settings) {
            return JSON.parse( localStorage.getItem( 'DataTables_' + settings.sInstance ) )
        },
        "columns": [
            { "data": "name" }
            ,{ "data": "label" }
            ,{ "data": "baseurlservidor" }
            ,{ "data": "button_delete" }
        ],
        "columnDefs": [
            {
                "targets":0,
                "title": "Nom de la capa"
            },
            {
                "targets":1,
                "title": "Títol de la capa"
            },
            {
                "targets":2,
                "title": "URL servidor wms"
            },
            {
                "targets": -1,
                "data": null,
                "defaultContent": "<button class=\"delete_button btn btn-danger\">Esborrar</button>",
                "sortable": false
            }
        ]
    } );

    var creacapawms = function(title, file){
        $.ajax({
            url: _create_wms_url,
            data: 'title=' + encodeURI(title) + '&filename=' + encodeURI(file),
            method: 'POST',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                toastr.success('Capa WMS creada amb èxit!');
                table.ajax.reload();
                $('#id_nomcapa').val('');
                $('.qq-upload-list').empty();
            },
            error: function(jqXHR, textStatus, errorThrown){
                console.log(jqXHR.responseJSON);
                toastr.error(jqXHR.responseJSON.detail);
            }
        });
    }

    var uploader = new qq.FileUploader({
        action: _ajax_upload_url,
        element: $('#fileuploader')[0],
        multiple: false,
        onSubmit: function(id, fileName){
            $('.qq-upload-list').empty();
            $('#filename').val('');
            var regex = /^[\w.]{0,256}$/;
            if( regex.exec(fileName) == null){
                toastr.error('Error a nom de fitxer! Només s\'admeten lletres (majúscules i minúscules), números i el caràcter "_"');
                return false;
            }
            this.params.deletePrevious = true;
        },
        onComplete: function(id, fileName, responseJSON) {
            if(responseJSON.success) {
                $('#filename').val(responseJSON.filename);
                toastr.success('Fitxer carregat al servidor amb èxit!')
            } else {
                //alert('upload failed!');
                toastr.error('Error pujant fitxer!')
            }
        },
        template:'<div class="qq-uploader">' +
            '<div class="qq-upload-drop-area"><span>Importar shapefile (zip) ò tiff</span></div>' +
            '<div class="qq-upload-button ui-widget-content ui-button ui-corner-all ui-state-default">Importar shapefile (zip) ò tiff</div>' +
            '<ul class="qq-upload-list"></ul>' +
            '</div>',
        params: {
            'csrf_token': csrf_token,
            'csrf_name': 'csrfmiddlewaretoken',
            'csrf_xname': 'X-CSRFToken',
        }
    });

    $('#btnCreaCapa').click(function(){
        var errors = false;
        var filename = $('#filename').val();
        var nomCapa = $('#id_nomcapa').val();
        var errorMsg = "";
        if(filename == '' || filename == null){
            errorMsg += '<p>Cal seleccionar un fitxer shapefile comprimit en zip, o bé un ràster TIFF</p>';
            errors = true;
        }
        if(nomCapa == '' || nomCapa == null){
            errorMsg += '<p>Cal posar un nom a la capa (un títol)</p>';
            errors = true;
        }
        if(errors){
            toastr.error(errorMsg);
        }else{
            creacapawms(nomCapa,filename);
        }
    });

    var delete_capawmslocal = function(id){
        $.ajax({
            url: _delete_wms_url + id,
            method: "DELETE",
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                 toastr.success("Esborrat amb èxit!");
                 table.ajax.reload();
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error("Error esborrant");
            }
        });
    };

    var confirmDialog = function(message,id){
        $('<div></div>').appendTo('body')
            .html('<div><h6>'+message+'</h6></div>')
            .dialog({
                modal: true, title: 'Esborrant capa wms local...', zIndex: 10000, autoOpen: true,
                width: 'auto', resizable: false,
                buttons: {
                    Yes: function () {
                        delete_capawmslocal(id);
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

    $('#capeswmslocal tbody').on('click', 'td button.delete_button', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
        var id = row.data().id
        confirmDialog("S'esborrarà la capa local WMS, incloent la capa del servidor geoserver. Vols continuar?",id);
    });
});