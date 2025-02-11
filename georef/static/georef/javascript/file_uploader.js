(function(){
    
    if (typeof djangoRef.FileUploader === 'undefined') this.djangoRef.FileUploader = {};
    
    djangoRef.FileUploader.createFileUploader = function(options){
        options = options || {};
        options = $.extend({},
            {
                file_input_id: 'fileInput',
                message_id: 'message',
                _ajax_upload_url: '/ajax-upload',
                _import_shapefile_url: '/ajax-process-shapefile',                
            },
            options);
        
        var importa_shapefile = function(filepath){
            $.ajax({
                url: options._import_shapefile_url,
                data: 'path=' + encodeURI(filepath) + '&smp=f',
                //data: 'path=' + encodeURI(filepath),
                method: 'GET',
                beforeSend: function(xhr, settings) {
                    if (!csrfSafeMethod(settings.type)) {
                        var csrftoken = getCookie('csrftoken');
                        xhr.setRequestHeader('X-CSRFToken', csrftoken);
                    }
                },
                success: function( data, textStatus, jqXHR ) {
                    if(data.success){
                        toastr.success(gettext('Importació amb èxit!'));
                        options.internal_map.editableLayers.clearLayers();
                        var geoJson = JSON.parse(data.detail);
                        var geoJSONLayer = L.geoJson(geoJson);
                        geoJSONLayer.eachLayer(
                            function(l){
                                options.internal_map.editableLayers.addLayer(l);
                            }
                        );
                        if(options.internal_map.editableLayers.getBounds().isValid()){
                            options.internal_map.map.fitBounds(options.internal_map.editableLayers.getBounds());
                        }                        
                    }else{
                        toastr.error(gettext('Error important fitxer') + ':' + data.detail);    
                    }
                },
                error: function(jqXHR, textStatus, errorThrown){
                    toastr.error(gettext('Error important fitxer') + ':' + jqXHR.responseJSON.detail);
                }
            });
        };

        var uploadFile = function () {
            let fileInput = $('#' + options.file_input_id)[0];
        
            if (fileInput.files.length === 0) {
                alert("Please select a file.");
                return;
            }
        
            let file = fileInput.files[0];
            let formData = new FormData();
            formData.append("file", file);        
        
            $.ajax({
                url: options._ajax_upload_url,  // Make sure this variable is defined
                type: "POST",
                data: formData,
                processData: false,  // Prevent jQuery from processing the data
                contentType: false,  // Prevent jQuery from setting content type
                beforeSend: function(xhr, settings) {
                    if (!csrfSafeMethod(settings.type)) {
                        var csrftoken = getCookie('csrftoken');
                        xhr.setRequestHeader('X-CSRFToken', csrftoken);
                    }
                },            
                xhr: function () {
                    let xhr = new window.XMLHttpRequest();
                    xhr.upload.addEventListener("progress", function (event) {
                        if (event.lengthComputable) {
                            let percent = (event.loaded / event.total) * 100;
                            $("#progress-bar").css("width", percent + "%").text(Math.round(percent) + "%");
                            $("#progress-container").show();
                        }
                    }, false);
                    return xhr;
                },
                success: function (response) {
                    if (response.success) {
                        $("#" + options.message_id).html(`<p>File uploaded successfully: <a href="${response.file_url}" target="_blank">${response.file_url}</a></p>`);
                        let path = response.file_path;
                        importa_shapefile(path);
                    } else {
                        $("#" + options.message_id).html("<p>Upload failed!</p>");
                    }
                },
                error: function () {
                    $("#" +  + options.message_id).html("<p>An error occurred while uploading.</p>");
                }
            });
        };

        $('#' + options.file_input_id).on('change',function(e){
            uploadFile();        
        });
    }    

})();