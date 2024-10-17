var counter = 0;
var tree;
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



var validate_form = function(){
    var valid = true;
    var errors = [];
    if( $('#id_nom').val() == '' ){
        valid = false;
        const choose_name = gettext("Cal triar un nom per al topònim");
        errors.push(choose_name);
    }
    if( $('#id_idtipustoponim').val() == '' ){
        valid = false;
        const choose_type = gettext("Cal triar el tipus de topònim del desplegable")
        errors.push(choose_type);
    }
    if ( validate_toponim_create() == false ){
        valid = false;
        const select_parent = gettext("Cal seleccionar un pare per al topònim");
        errors.push(select_parent);
    }

    $('#error_list').empty();
    const root = $('#error_list');
    for(var i = 0; i < errors.length; i++){
        root.append(error_item_template(errors[i]));
    }

    return valid;
}

var validate_toponim_create = function(){
    var top_selected = get_top_selected_node('#jstree');
    var checked = get_undetermined_nodes('#jstree');
    if (top_selected == null){
        //toastr.error("Cal seleccionar un pare per al topònim")
        return false;
    }
    return true;
}

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

var process_selection_data_for_ariadna = function(data){
    var text_path = data.instance.get_path(data.node,false,false);
    var text_path_clean = [];
    for(var i = 0; i < text_path.length; i++){
        text_path_clean.push( text_path[i].split(' - ')[0] );
    }
    var path = data.instance.get_path(data.node,false,true);
    var new_data = [];
    for(var i = 0; i < text_path_clean.length; i++){
        new_data.push( path[i] + '$' + text_path_clean[i] );
    }
    return new_data;
}

var create_tree = function(){
     return $('#jstree')
        .on('loaded.jstree', function(event, data) {
            if(node_list != null && node_list.length>1 && node_list[0]!='1'){
                data.instance.load_node(node_list[0],node_load_callback);
            }else{
                data.instance.select_node(node_list[0]);
            }
        })
        .on('changed.jstree', function (e, data) {
            if(data.instance.get_top_selected()[0]==null){
                init_ariadna([]);
            }else{
                var new_data = process_selection_data_for_ariadna(data);
                init_ariadna(new_data);
            }
        })
        .on('select_node.jstree', function (e, data) {
            $('#id_idpare').val(data.instance.get_top_selected()[0]);
            $('#seleccio').empty();
            $('#seleccio').append('Seleccionat: ' + data.node.text);
            var new_data = process_selection_data_for_ariadna(data);
            init_ariadna(new_data);
        })
        .on('deselect_node.jstree', function (e, data) {
            if(data.instance.get_top_selected().length > 1){
                //top_selected_node = "";
                $('#id_idpare').val('');
                $('#seleccio').empty();
                $('#seleccio').append('Seleccionat: cap');
                init_ariadna([]);
            }else{
                $('#id_idpare').val(data.instance.get_top_selected()[0]);
                $('#seleccio').empty();
                //$('#seleccio').append('Seleccionat: ' + data.node.text);
                $('#seleccio').append('Seleccionat: cap');
                init_ariadna([]);
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
                        if (node.id === '#'){
                            return '/toponimstree/';
                        }else{
                            return '/toponimstree/?id=' + node.id;
                        }
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
}

var reload_tree = function(node_list_full){
    node_list = [];
    for(var i = 0; i < node_list_full.length; i++){
        node_list.push(node_list_full[i].split('$')[0]);
    }
    var node_ini = "1";
    tree.jstree("destroy");
    counter = 0;
    tree = create_tree();
}

$(document).ready(function() {
    tree = create_tree();

    $( '#autoc_tree' ).autocomplete({
        source: function(request,response){
            $.getJSON( _toponim_node_search_url + '?term=' + request.term, function(data){
                response($.map(data, function(item){
                    return {
                        label: item.nom,
                        value: item.id,
                        node_list: item.node_list
                    };
                }));
            });
        },
        minLength: 3,
        select: function( event, ui ) {
            var listname = ui.item.label;
            $( '#autoc_tree' ).val(listname);
            reload_tree( ui.item.node_list );
            init_ariadna( ui.item.node_list );
            return false;
        }
    });

    function reset_similar_list(){
        $('#similar_list').empty();
    }

    function init_single_items(data){
        reset_similar_list();
        const root = $('#similar_list');
        for(var i = 0; i < data.length; i++){
            root.append(single_similar_item_template(data[i]));
        }
    }

    function check_name(name){
        $.ajax({
            url: _ajax_check_name + "?q=" +  encodeURIComponent(name),
            type: "GET",
            headers: { "X-CSRFToken": csrf_token },
            dataType: "json",
            success: function(data) {
                if(data.length==0){
                    $('#site_form').submit();
                }else{
                    init_single_items(data);
                    $( "#dialog-confirm" ).dialog({
                      resizable: false,
                      height: "auto",
                      width: 400,
                      modal: true,
                      buttons: [
                        {
                            text: gettext("Sí, crear topònim"),
                            click: function(){
                                $( this ).dialog( "close" );
                                $('#site_form').submit();
                            }
                        },
                        {
                            text: gettext("Cancel·lar"),
                            click: function(){
                                $( this ).dialog( "close" );
                            }
                        }
                      ]
                    });
                }
            },
            error: function(jqXHR, textStatus, errorThrown){
                //alert(jqXHR.responseJSON.message);
            },
            cache: false
        });
    }

    $('#create_site').on('click',function(e){
        e.preventDefault();
        if(validate_form()==false){
            $( "#dialog-error" ).dialog({
                      resizable: false,
                      height: "auto",
                      width: 400,
                      modal: true,
                      buttons: [
                        {
                            text: gettext("Ok"),
                            click: function(){
                                $( this ).dialog( "close" );
                            }
                        }
                      ]
                    });
        }else{
            check_name($('#id_nom').val());
        }
    });
});
