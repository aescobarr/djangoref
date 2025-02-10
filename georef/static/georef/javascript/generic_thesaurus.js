(function(){

    if (typeof(jQuery.fn.DataTable) == 'undefined') throw 'DataTables must be loaded';

    if (typeof djangoRef === 'undefined') this.djangoRef = {};

    if (typeof djangoRef.GenericThesaurus === 'undefined') this.djangoRef.GenericThesaurus = {};

    djangoRef.GenericThesaurus.table = null;

    djangoRef.GenericThesaurus.create = function(options){
        options = options || {};
        options = $.extend({},
        {
            column_name: gettext('Nom'),
            description_column_name: gettext('Descripció'),
            description_column: 'description'
        },
        options);

        //The instance label acts as a unique identifier for the local storage which holds the
        //table state. This identifier must be unique, and it's of the form  'DataTables_' + instance_label
        if (options.instance_label == null) throw 'Missing mandatory parameter instance_label';

        if (options.data_url == null) throw 'Missing mandatory parameter data_url';

        if (options.crud_url == null) throw 'Missing mandatory parameter crud_url';

        djangoRef.GenericThesaurus.table = $('#element_list').DataTable( {
            'ajax': {
                'url': options.data_url,
                'dataType': 'json'
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
                localStorage.setItem( 'DataTables_' + options.instance_label, JSON.stringify(data) );
            },
            stateLoadCallback: function(settings) {
                return JSON.parse( localStorage.getItem( 'DataTables_' + options.instance_label ) );
            },
            'columns': [
                { 'data': options.text_field_name },
                { 'data': options.description_column },
            ],
            'columnDefs': [
                {
                    'targets': 2,
                    'data': 'editable',
                    'sortable': false,
                    //'defaultContent': '<button class="delete_button btn btn-danger"><i class="fa fa-times" aria-hidden="true"></i></button>',
                    'render': function(value){
                        if(user_can_edit==true){
                            return '<button class="delete_button btn btn-danger"><i class="fa fa-times" aria-hidden="true"></i></button>';
                        }else{
                            return '&nbsp;';
                        }
                    }
                },
                {
                    'targets': 3,
                    'data': 'editable',
                    'sortable': false,
                    'defaultContent': '<button class="edit_button btn btn-info"><i class="fa fa-pencil-square-o" aria-hidden="true"></i></button>',
                    'render': function(value){
                        if(user_can_edit==true){
                            return '<button class="edit_button btn btn-info"><i class="fa fa-pencil-square-o" aria-hidden="true"></i></button>';
                        }else{
                            return '&nbsp;';
                        }
                    }
                },
                {
                    'targets':0,
                    'title': options.column_name
                },
                {
                    'targets':1,
                    'title': options.description_column_name
                }
            ]
        } );

        var do_update = function(){
            _update($('#name_update').val(),$('#id').val(),$('#description_update').val());
        }

        var update_text = gettext('Actualitzar');
        var cancel_text = gettext('Cancel·lar');

        var dialog_update = $( "#dialog-form-update" ).dialog({
            autoOpen: false,
            height: 400,
            width: 400,
            modal: true,
            buttons: [
                {text: update_text, click: do_update},
                {text: cancel_text, click: function() { dialog_update.dialog( "close" ); }}
            ],
            close: function() {
                form_update[ 0 ].reset();
            }
        });

        var form_update = dialog_update.find( "form" ).on( "submit", function( event ) {
            event.preventDefault();
        });


        //return djangoRef.GenericThesaurus.table;
        var _update = function(new_nom, id, description){
            $.ajax({
                url: options.crud_url + encodeURI(id) + '/',
                data: JSON.parse("{ \"" + options.text_field_name + "\":\"" + new_nom + "\",\"" + options.description_column + "\":\"" + description + "\" }"),
                method: 'PUT',
                beforeSend: function(xhr, settings) {
                    if (!csrfSafeMethod(settings.type)) {
                        var csrftoken = getCookie('csrftoken');
                        xhr.setRequestHeader('X-CSRFToken', csrftoken);
                    }
                },
                success: function( data, textStatus, jqXHR ) {
                    toastr.success(gettext('Actualitzat amb èxit!'));
                    dialog_update.dialog('close');
                    djangoRef.GenericThesaurus.table.ajax.reload();
                },
                error: function(jqXHR, textStatus, errorThrown){
                    toastr.error(gettext('Error actualitzant!'));
                }
            });
        }

        var do_add = function(){
            _add($('#name').val(), $('#description').val());
        };

        var btn_create = gettext('Crear');
        var cancel_text = gettext('Cancel·lar');

        var dialog_buttons = {};
        dialog_buttons[btn_create] = do_add;
        dialog_buttons[cancel_text] = function() { dialog_create.dialog( "close" ); }

        var dialog_create = $( "#dialog-form-create" ).dialog({
            autoOpen: false,
            height: 400,
            width: 400,
            modal: true,
            buttons: dialog_buttons,
            close: function() {
                form_create[ 0 ].reset();
            }
        });

        var form_create = dialog_create.find( "form" ).on( "submit", function( event ) {
            event.preventDefault();
        });

        var _add = function(nom, description){
            $.ajax({
                url: options.crud_url,
                data: JSON.parse("{ \"" + options.text_field_name + "\":\"" + nom + "\",\"" + options.description_column + "\":\"" + description + "\"}"),
                method: 'POST',
                beforeSend: function(xhr, settings) {
                    if (!csrfSafeMethod(settings.type)) {
                        var csrftoken = getCookie('csrftoken');
                        xhr.setRequestHeader('X-CSRFToken', csrftoken);
                    }
                },
                success: function( data, textStatus, jqXHR ) {
                    toastr.success(gettext('Afegit amb èxit!'));
                    dialog_create.dialog('close');
                    djangoRef.GenericThesaurus.table.ajax.reload();
                },
                error: function(jqXHR, textStatus, errorThrown){
                    toastr.error(gettext('Error afegint!'));
                }
            });
        }

        var _delete = function(id){
            $.ajax({
                url: options.crud_url + encodeURI(id) + '/',
                method: 'DELETE',
                beforeSend: function(xhr, settings) {
                    if (!csrfSafeMethod(settings.type)) {
                        var csrftoken = getCookie('csrftoken');
                        xhr.setRequestHeader('X-CSRFToken', csrftoken);
                    }
                },
                success: function( data, textStatus, jqXHR ) {
                    toastr.success(gettext('Esborrat amb èxit!'));
                    djangoRef.GenericThesaurus.table.ajax.reload();
                },
                error: function(jqXHR, textStatus, errorThrown){
                    toastr.error(gettext('Error esborrant!'));
                }
            });
        };

        var perform_delete_check = function(id){
            var def = $.Deferred();
            $.ajax({
                url: check_delete_url + '?' + 'mfqn=' + encodeURI(options.class_full_qualified_name) + '&id=' + encodeURI(id) + "/",
                method: 'GET',
                beforeSend: function(xhr, settings) {
                    if (!csrfSafeMethod(settings.type)) {
                        var csrftoken = getCookie('csrftoken');
                        xhr.setRequestHeader('X-CSRFToken', csrftoken);
                    }
                },
                success: function( data, textStatus, jqXHR ) {
                    def.resolve({ 'message': data.detail, 'n': data.to_delete_len});
                },
                error: function(jqXHR, textStatus, errorThrown){
                    def.reject({ 'message': textStatus, 'n': -1});
                }
            });
            return def.promise();
        }

        var show_delete_dialog = function(message,id){
            $('<div></div>').appendTo('body')
                .html(message)
                .dialog({
                    modal: true, title: gettext('Esborrant...'), zIndex: 10000, autoOpen: true,
                    width: 'auto', resizable: false,
                    buttons: {
                        Yes: function () {
                            _delete(id);
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
        }

        var confirmDialog = function(message,id){
            if(options.class_full_qualified_name){
                perform_delete_check(id).then( function(info){
                    if(info.n < 2){
                        show_delete_dialog('<div class="warning_delete_body">' + message + '</div>' + '</br>' + '<div class="warning_delete_cascade_noc">' + info.message + '</div>', id);
                    }else{
                        show_delete_dialog('<div class="warning_delete_body">' + message + '</div>' + '</br>' + '<div class="warning_delete_cascade">' + gettext('Es produïran els esborrats en cascada següents') + ':</br>' + info.message + '</div>', id);
                    }
                } );
            }else{
                show_delete_dialog('<div>' + message + '</div>', id);
            }
        };

        $( "#add" ).button().on( "click", function() {
            dialog_create.dialog( "open" );
        });

        $('#element_list tbody').on('click', 'td button.edit_button', function () {
            var tr = $(this).closest('tr');
            var row = djangoRef.GenericThesaurus.table.row( tr );
            var id = row.data().id;
            var name = row.data()[options.text_field_name];
            var description = row.data()[options.description_column];
            $('#id').val(id);
            $('#name_update').val(name);
            $('#description_update').val(description);
            dialog_update.dialog( "open" );
        });

        $('#element_list tbody').on('click', 'td button.delete_button', function () {
            var tr = $(this).closest('tr');
            var row = djangoRef.GenericThesaurus.table.row( tr );
            var id = row.data().id;
            confirmDialog(gettext("S'esborrarà '") + row.data()[options.text_field_name] + gettext("'! Segur que vols continuar?"),id);
        });

    }

})();
