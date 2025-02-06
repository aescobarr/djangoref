$(document).ready(function() {
    table = $('#users_list').DataTable( {
        'ajax': {
            'url': _user_list_url,
            'dataType': 'json'
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
        'createdRow': function( row, data, dataIndex){
            if( data.user.is_active ==  false ){
                $(row).addClass('disabled');
            }
        },
        'columns': [
            { 'data': 'user.username' }
            ,{ 'data': 'user.first_name' }
            ,{ 'data': 'user.last_name' }
            ,{ 'data': 'user.email' }
            ,{ 'data': 'organization.name' }
        ],
        'columnDefs': [
            {
                'targets':0,
                'title': gettext('Usuari')
            },
            {
                'targets':1,
                'title': gettext('Nom')
            },
            {
                'targets':2,
                'title': gettext('1er cognom')
            },
            {
                'targets':3,
                'title': gettext('Correu-e')
            },
            {
                'targets':4,
                'title': gettext('Organització')
            },
            {
                'targets': 5,
                'data': null,
                'sortable': false,
                'defaultContent': '<button title="' + gettext('Esborrar usuari') + '" class="delete_button btn btn-danger"><i class="fa fa-times" aria-hidden="true"></i></button>'
            },
            {
                'targets': 6,
                'data': null,
                'sortable': false,
                'defaultContent': '<button title="' + gettext('Editar perfil') + '" class="edit_button btn btn-info"><i class="fa fa-pencil-square-o" aria-hidden="true"></i></button>'
            },
            {
                'targets': 7,
                'data': null,
                'sortable': false,
                'defaultContent': '<button title="' + gettext('Canviar password') + '" class="chgpsswd_button btn btn-danger"><i class="fa fa-asterisk"></i></button>'
            },
            {
                'targets': 8,
                'data': null,
                'sortable': false,
                'defaultContent': '<button title="' + gettext('Activar/Desactivar usuari') + '" class="lock_button btn btn-danger"><i class="fa fa-lock"></i></button>'
            }
        ]
    } );

    var perform_delete_check = function(id){
        var def = $.Deferred();
        $.ajax({
            url: check_delete_url + '?' + 'mfqn=auth.User&id=' + encodeURI(id) + "/",
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

    var delete_usuari = function(id){
        $.ajax({
            url: _user_delete_url + id + "/",
            method: 'DELETE',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                toastr.success(gettext('Usuari esborrat amb èxit!'));
                table.ajax.reload();
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error(gettext('Error esborrant'));
            }
        });
    };

    var lock_usuari = function(id, lock){
        var data = { 'id':id,'act': ( !lock==true ? '1':0 ) };
        var querystring = encodeQueryData(data);
        $.ajax({
            url: _user_lock_url + "?" + querystring,
            method: 'POST',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                if(lock==true){
                    toastr.success(gettext('Usuari bloquejat amb èxit!'));
                }else{
                    toastr.success(gettext('Usuari desbloquejat amb èxit!'));
                }
                table.ajax.reload();
            },
            error: function(jqXHR, textStatus, errorThrown){
                if(lock==true){
                    toastr.error(gettext('Error bloquejant'));
                }else{
                    toastr.error(gettext('Error desbloquejant'));
                }
            }
        });
    }

    var confirmDialog = function(message,id){
        perform_delete_check(id).then( function(info){
            if(info.n < 2){
                show_delete_dialog('<div class="warning_delete_body">' + message + '</div>' + '</br>' + '<div class="warning_delete_cascade_noc">' + info.message + '</div>', id);
            }else{
                show_delete_dialog('<div class="warning_delete_body">' + message + '</div>' + '</br>' + '<div class="warning_delete_cascade">' + gettext('Es produïran els esborrats en cascada següents') + ':</br>' + info.message + '</div>', id);
            }
        } );
    };


    var show_delete_dialog = function(message,id){
        $('<div></div>').appendTo('body')
        .html(message)
        .dialog({
            modal: true, title: gettext('Esborrant...'), zIndex: 10000, autoOpen: true,
            width: 'auto', resizable: false,
            buttons: {
                Yes: function () {
                    delete_usuari(id);
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

    var show_lock_dialog = function(id, lock){
        var message = '';
        var title = '';
        if(user_id == id){
            message = '<p class="error">*** ' + gettext('Atenció: Estàs a punt de desactivar el teu usuari! Quan tanquis la sessió actual no podràs tornar a fer login!') + ' ***</p>';
        }
        if(lock == true){
            message += "<p>" + gettext("Es desactivarà l'usuari. No podrà fer login a l'aplicació ni editar registres. Vols continuar?") + "</p>";
            title = gettext('Bloquejant...');
        }else{
            message += "<p>" + gettext("S'activarà l'usuari. Podrà tornar a loginar-se a l'aplicació i editar registres. Vols continuar?") + "</p>";
            title = gettext('Desbloquejant...');
        }
        $('<div></div>').appendTo('body')
        .html( message )
        .dialog({
            modal: true, title: title, zIndex: 10000, autoOpen: true,
            width: 'auto', resizable: false,
            buttons: {
                Yes: function () {
                    lock_usuari(id, lock);
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

    /*
    var confirmDialog = function(message,id){
        $('<div></div>').appendTo('body')
            .html('<div><h6>'+message+'</h6></div>')
            .dialog({
                modal: true, title: gettext('Esborrant usuari...'), zIndex: 10000, autoOpen: true,
                width: 'auto', resizable: false,
                buttons: {
                    Yes: function () {
                        delete_usuari(id);
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
    */

    $( '#addUser' ).click(function() {
        var url = _add_user_url;
        window.location.href = url;
    });

    $('#users_list tbody').on('click', 'td button.edit_button', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
        var id = row.data().user.id;
        url = '/user/profile/' + id + '/';
        window.location.href = url;
    });

    $('#users_list tbody').on('click', 'td button.chgpsswd_button', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
        var id = row.data().user.id;
        url = '/user/password/change/' + id;
        window.location.href = url;
    });

    $('#users_list tbody').on('click', 'td button.delete_button', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
        var id = row.data().user.id;
        confirmDialog(gettext("S'esborrarà l'usuari '") + row.data().user.first_name + " " + row.data().user.last_name + gettext("'! Segur que vols continuar?"),id);
    });

    $('#users_list tbody').on('click', 'td button.lock_button', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
        var id = row.data().user.id;
        var active = row.data().user.is_active;
        show_lock_dialog(id,active);
    });
});