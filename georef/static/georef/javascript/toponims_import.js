$(document).ready(function() {

    var import_csv = function(file){
        $.ajax({
            url: _import_csv_url + encodeURI(file),
            method: 'POST',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                //console.log(data.detail);
                processResponse(jqXHR.responseJSON);
                $('.qq-upload-list').empty();
            },
            error: function(jqXHR, textStatus, errorThrown){
                console.log(jqXHR.responseJSON);
                //toastr.error(jqXHR.responseJSON.detail);
                processResponse(jqXHR.responseJSON);
            }
        });
    }

    var uploader = new qq.FileUploader({
        action: _ajax_upload_url,
        element: $('#fileuploader')[0],
        multiple: false,
        onSubmit: function(id, fileName){
            $('#filename').val('');
            resetInterface();
            this.params.deletePrevious = true;
        },
        onComplete: function(id, fileName, responseJSON) {
            if(responseJSON.success) {
                //$('#filename').val(responseJSON.filename);
                //toastr.success('Fitxer carregat al servidor amb èxit!')
                //console.log(responseJSON.detail);
                import_csv(responseJSON.filename);
            } else {
                toastr.error('Error pujant fitxer!')
            }
        },
        template:'<div class="qq-uploader">' +
            '<div class="qq-upload-drop-area"><span>Pujar fitxer CSV</span></div>' +
            '<div class="qq-upload-button ui-widget-content ui-button ui-corner-all ui-state-default">Pujar fitxer CSV</div>' +
            '<ul class="qq-upload-list"></ul>' +
            '</div>',
        params: {
            'csrf_token': csrf_token,
            'csrf_name': 'csrfmiddlewaretoken',
            'csrf_xname': 'X-CSRFToken',
        }
    });

    $('#details').click(function(){
        //$('.persiana').toggle();
        if( $('.persiana').attr("style") == 'display: none;' ){
            $('.persiana').fadeIn( "slow", function(){});
        }else{
            $('.persiana').fadeOut( "slow", function(){});
        }
    });

    var processResponse = function(responseJSON){
        if(responseJSON.status=='KO'){
            var message = responseToHTML(responseJSON.detail);
            mostrarCaixaErrors(message);
        }else{
            buildTable(responseJSON);
        }
    };

    var resetInterface = function(){
        $("#errors").hide();
    }

    var mostrarCaixaErrors = function(text){
            var missatge = "<h3>El fitxer csv conté alguns errors. Cal arreglar-los i tornar-ho a intentar:</h3><ul>";
            missatge += "<li>"+text+"</li>";
            var caixa = $("#errors");
            //caixa.innerHTML = missatge+"</ul>";
            caixa.html(missatge+"</ul>");
            caixa.show();
            /*caixa.style.display = "block";
            caixa.style.visibility = "visible";*/
    };

    var responseToHTML = function(response){
        var html = new Array();
        if(typeof response == 'string'){
            html.push("<p><strong>Error general de fitxer:</strong></p>");
            html.push("<p>   * " + response + "</p>");
            return html.join("");
        }else{
            if(response.length == 1){
                html.push("<p><strong>S'ha produït un error:</strong></p>");
                html.push("<p>   * " + response[0] + "</p>");
                return html.join("");
            }else{
                for(var i=0; i < response.length; i++){
                    result = response[i];
                    if(result[0] == -1){
                        html.push("<p><strong>Error general de fitxer:</strong></p>");
                    }else{
                        html.push("<p><strong>Línia " + result[0] + " :</strong></p>");
                    }
                    for(var j=0; j < result[1].length; j++){
                        html.push("<p>   * " + result[1][j] + "</p>");
                    }
                }
                return html.join("");
            }
        }
    };

    var buildTable = function(responseJSON){
        var tbl_summary_body = "";
        var tbl_summary_head = "";
        var tbl_creats_body = "";
        var tbl_creats_head = "";
        var tbl_existents_body = "";
        var tbl_existents_head = "";
        var tbl_body = "";
        var tbl_head = "";
        var odd_even = false;

        tbl_summary_head = "<tr><th>Sumari de resultats importacio</th><th>&nbsp;</th></tr>"
        tbl_summary_body = "<tr><td>Número de topònims creats</td><td>" + responseJSON.results[0].numToponimsCreats + "</td></tr><tr><td>Topònims que ja existien</td><td>" + responseJSON.results[1].numToponimsJaExisteixen + "</td></tr>"
        $("#sumari thead").html(tbl_summary_head);
        $("#sumari tbody").html(tbl_summary_body);

        if(responseJSON.results[2].creats.length > 0){
            tbl_creats_head = "<tr><th>Topònims creats</th><th>&nbsp;</th></tr>";
            tbl_creats_head += "<tr><th>Nom del topònim</th><th>Enllaç al topònim</th></tr>";
            var creats_body_arr = new Array();
            for( var i = 0; i < responseJSON.results[2].creats.length; i++ ){
                var fila = "<tr class=\""+( odd_even ? "odd" : "even")+"\">" + "<td>" + responseJSON.results[2].creats[i].nom + "</td><td><a target=\"_blank\" href=\"/Zoologia/toponims/editartoponim.htm?idtoponim=" + responseJSON.results[2].creats[i].id + "\">Link</a></td></tr>";
                creats_body_arr.push(fila);
                odd_even = !odd_even;
            }
            tbl_creats_body = creats_body_arr.join("");
            $("#creats thead").html(tbl_creats_head);
            $("#creats tbody").html(tbl_creats_body);
        }else{
            $("#creats thead").html("");
            $("#creats tbody").html("");
        }

        if(responseJSON.results[3].existents.length > 0){
            tbl_existents_head = "<tr><th>Topònims que ja existien a la base de dades (no s'han importat)</th><th>&nbsp;</th></tr>";
            tbl_existents_head += "<tr><th>Nom del topònim</th><th>Enllaç al topònim</th></tr>";
            var existents_body_arr = new Array();
            odd_even = false;
            for( var i = 0; i < responseJSON.results[3].existents.length; i++ ){
                var fila = "<tr class=\""+( odd_even ? "odd" : "even")+"\">" + "<td>" + responseJSON.results[3].existents[i].nom + "</td><td><a target=\"_blank\" href=\"/toponims/update/" + responseJSON.results[3].existents[i].id + "/-1/\">Link</a></td></tr>";
                existents_body_arr.push(fila);
                odd_even = !odd_even;
            }
            tbl_existents_body = existents_body_arr.join("");
            $("#existents thead").html(tbl_existents_head);
            $("#existents tbody").html(tbl_existents_body);
        }else{
            $("#existents thead").html("");
            $("#existents tbody").html("");
        }

        $("#resultats tbody").html(tbl_body);
        $("#linkDescarrega").attr("href",responseJSON.fileLink);
        $("a#linkDescarrega").text('Descarrega fitxer csv de resum');
    };


});