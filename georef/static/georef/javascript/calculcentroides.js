$(document).ready(function() {

    var show_data = function(centroid_x,centroid_y,unc){
        $('#val_x').text(centroid_x);
        $('#val_x').toggle( "highlight" );
        $('#val_y').text(centroid_y);
        $('#val_y').toggle( "highlight" );
        $('#val_inc').text(unc);
        $('#val_inc').toggle( "highlight" );
    }

    var show_thinking = function(really){
        if(really && really == true){
            $('#label_x').addClass('asyncload');
            $('#label_y').addClass('asyncload');
            $('#label_inc').addClass('asyncload');
        }else{
            $('#label_x').removeClass('asyncload');
            $('#label_y').removeClass('asyncload');
            $('#label_inc').removeClass('asyncload');
        }
    }

    $( '#clipboard' ).click(function() {
        var text = '';
        var TAB = "\t";
        text = 'lat:' + $('#val_y').text()  + TAB +  ' long:' + $('#val_x').text()  + TAB +  ' prec:' + $('#val_inc').text();
        copyToClipboard(text);
        toastr.success(gettext("Resultats copiats al portapapers!"));
    });

    var computeCentroid = function(filename){
        $('#info_block').show();
        show_data('','','');
        show_thinking(true);
        $.ajax({
            url: _compute_centroid_url + encodeURI(filename),
            method: "POST",
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                 console.log(data);
                 show_data(data.detail.centroid_x, data.detail.centroid_y, data.detail.inc);
                 show_thinking(false);
            },
            error: function(jqXHR, textStatus, errorThrown){
                if(jqXHR.responseJSON){
                    toastr.error(gettext("Error calculant centroide - ") + jqXHR.responseJSON.detail);
                    console.log(jqXHR);
                }else{
                    toastr.error(gettext("Error inesperat. Si us plau comprova que l'estructura del fitxer zip és correcta."));
                }
                show_thinking(false);
            }
        });
    }

    var uploader = new qq.FileUploader({
        action: _ajax_upload_url,
        element: $('#fileuploader')[0],
        multiple: false,
        onSubmit: function(id, fileName){
            $('#filename').val('');
            this.params.deletePrevious = true;
        },
        onComplete: function(id, fileName, responseJSON) {
            if(responseJSON.success) {
                //$('#filename').val(responseJSON.filename);
                //toastr.success('Fitxer carregat al servidor amb èxit!')
                computeCentroid(responseJSON.filename);
            } else {
                toastr.error(gettext('Error pujant fitxer!'));
            }
        },
        template:'<div class="qq-uploader">' +
            '<div class="qq-upload-drop-area"><span>' + gettext('Importar shapefile (zip)') + '</span></div>' +
            '<div class="qq-upload-button ui-widget-content ui-button ui-corner-all ui-state-default">' + gettext('Importar shapefile (zip)') + '</div>' +
            '<ul class="qq-upload-list"></ul>' +
            '</div>',
        params: {
            'csrf_token': csrf_token,
            'csrf_name': 'csrfmiddlewaretoken',
            'csrf_xname': 'X-CSRFToken',
        }
    });

});
