var table_items;

var validate_table = function(){
    //error conditions
    // separator with text
    // link without text or link (non-separator)
    // repeated order
    // blank order
    var tabledata = table_items.getData();
    var errors = [];
    for(var i=0; i < tabledata.length; i++){
        var row = tabledata[i];
        var fila = i + 1;
        if(row.is_separator){
            if (row.link != "" || row.title != ""){
                errors.push(gettext("L'item està marcat com a separador però té titol i link, fila - ") + fila);
            }
        }else{
            if (row.link == "" || row.title == ""){
                errors.push(gettext("L'item no és un separador i no té títol o link i són obligatoris, fila - ") + fila);
            }
        }
        if(row.order == ''){
            errors.push(gettext("Ordre en blanc a la fila - ") + fila);
        }
    }
    return errors;
}

var get_new_order = function(){
    var new_order = 0;
    var numbers = [];
    for(var i=0; i < table_items.getData().length; i++){
        var tr = table_items.getData()[i];
        if( tr.order != "" ){
            var on_table = parseInt(tr.order);
            numbers.push(on_table);
        }
    }
    if( numbers.length == 0 ){
        return 1;
    }
    var max = Math.max(...numbers);
    return max+1;
}

    var load_data = function(){
        $.ajax({
            url: _data_url + "?lang=" + locale,
            method: 'GET',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                //toastr.success(gettext('Element de menú creat amb èxit!'));
                // reload preview
                console.log(data.results);
                table_items.setData(data.results);
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error(jqXHR.responseJSON.detail);
            }
        });
    }

    var save_table = function(){
        $.ajax({
            url: _data_save_url,
            data: JSON.stringify(table_items.getData()),
            contentType : 'application/json',
            method: 'POST',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                toastr.success(gettext("Taula desada amb èxit!"));
                load_data();
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error(gettext("S'ha produït un error desant"));
            }
        });
    }

$(document).ready(function() {

    var tabledata = [];

    var editCheck = function(cell){
        //cell - the cell component for the editable cell
        //get row data
        var data = cell.getRow().getData();
        //return data.is_separator == false; // only allow the name cell to be edited if the age is over 18
        if (!data.is_separator){
            return true;
        }else{
            return false;
        }
    }

    table_items = new Tabulator("#menuitems",
    {
 	    height: 400, // set height of table (in CSS or here), this enables the Virtual DOM and improves render speed dramatically (can be any valid css height value)
 	    data: tabledata, //assign data to table
 	    //layout:"fitColumns", //fit columns to width of table (optional)
 	    initialSort: [
 	        {column: "order", dir: "asc"}
 	    ],
 	    columns:[ //Define Table Columns
	 	    {title:gettext("Ordre"), field:"order", editor:"input", validator:"integer", headerSort:false, sorter:"number", width:60 },
	 	    {title:gettext("Separador?"), field:"is_separator", hozAlign:"center", formatter:"tickCross", editor:true, headerSort:false},
	 	    {title:gettext("Text de l'item de menu"), field:"title", editor:"input", headerSort:false, editable:editCheck  },
	 	    {title:gettext("Enllaç"), field:"link", editor:"input", headerSort:false, editable:editCheck },
	 	    {title:gettext("Obrir en finestra exterior"), field:"open_in_outside_tab", width:90,  hozAlign:"center", formatter:"tickCross", editor:true, headerSort:false, editable:editCheck, width:200},
	 	    {formatter:"buttonCross", align:"center", cellClick:function(e, cell){ if(confirm(gettext("Eliminar fila?"))){ cell.getRow().delete(); }}, headerSort:false}
 	    ],
    });


    $("#add").on('click', function(e){
        var this_order = get_new_order();
        table_items.addData([{order:this_order,title:"",link:"",open_in_outside_tab:true, is_separator:false, language:locale}], false);
        return false;
    });

    $("#save").on('click', function(e){
        var errors = validate_table();
        if(errors.length > 0){
            var messages = [];
            for(var i = 0; i < errors.length; i ++){
                messages.push("<i>" + errors[i] + "</i>");
                $("#errors").html( messages.join("") );
            }
            $("#errors_panel").show();
        }else{
            $("#errors").html( "" );
            $("#errors_panel").hide();
            save_table();
        }
        return false;
    });

    $("#undo").on('click', function(e){
        $("#errors").html( "" );
        $("#errors_panel").hide();
        load_data();
        return false;
    });

    load_data();

});
