$(document).ready(function() {
    table = $('#toponimsfilter_list').DataTable( {
        "ajax": {
            "url": _filtrestoponims_list_url,
            "dataType": 'json'
            ,"data": function(d){
                d.filtrejson = '{"filtre":[{"modul":"TOPONIMS"}]}';
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
            { "data": "nomfiltre" }
            ,{ "data": "description" }
            //,{ "data": "button_delete" }
        ],
        "columnDefs": [
            {
                "targets":0,
                "title": gettext("Nom del filtre")
            },
            {
                "targets":1,
                "title": gettext("Descripció"),
                "render": function(value){
                    var retVal = "";
                    retVal += '<span class="label label-warning">' + value + '</span><br>';
                    return retVal;
                },
                "sortable": false
            },
            {
                'targets': 2,
                'data': 'editable',
                'sortable': false,
                'render': function(value){
                    if(value==true){
                        return "<button class=\"delete_button btn btn-danger\">" + gettext('Esborrar') + "</button>";
                    }else{
                        return '&nbsp;';
                    }
                }
            }
        ]
    } );

    var delete_toponimfilter = function(id){
        $.ajax({
            url: _toponimsfilter_delete_url + id + "/",
            method: "DELETE",
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                 toastr.success(gettext("Esborrat amb èxit!"));
                 table.ajax.reload();
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error(gettext("Error esborrant"));
            }
        });
    };

    var confirmDialog = function(message,id){
        $('<div></div>').appendTo('body')
            .html('<div><h6>'+message+'</h6></div>')
            .dialog({
                modal: true, title: gettext('Esborrant filtre de topònims...'), zIndex: 10000, autoOpen: true,
                width: 'auto', resizable: false,
                buttons: {
                    Yes: function () {
                        delete_toponimfilter(id);
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

    $('#toponimsfilter_list tbody').on('click', 'td button.delete_button', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
        var id = row.data().idfiltre
        //alert(id);
        confirmDialog(gettext("Segur que vols esborrar?"),id);
    });

});