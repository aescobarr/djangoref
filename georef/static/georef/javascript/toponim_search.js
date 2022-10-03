$(document).ready(function() {
    $( '#autoc_toponim' ).autocomplete({
        source: function(request,response){
            $.getJSON( _toponim_search_url + '?term=' + request.term, function(data){
                response($.map(data.results, function(item){
                    return {
                        label: item.nom_str
                        ,value: item.nom_str
                        ,coord_x: item.coordenada_x_centroide
                        ,coord_y: item.coordenada_y_centroide
                        ,precisio: item.precisio
                        ,precisio_calc: item.precisio_calc
                        ,id: item.id
                        //,json: item.json
                    };
                }));
            });
        },
        minLength: 2,
        select: function( event, ui ) {
            var listname = ui.item.label;
            $('#autoc_toponim').val(listname);
            $('#val_nom').text(ui.item.label);
            $('#val_y').text(ui.item.coord_y);
            $('#val_x').text(ui.item.coord_x);
            $('#val_prec').text(ui.item.precisio);
            $('#val_prec_calc').text(ui.item.precisio_calc);
            return false;
        }
    });

    $( '#clipboard' ).click(function() {
        var text = '';
        var TAB = "\t";
        text = $('#val_nom').text() + TAB + ' lat:' + $('#val_y').text() + TAB + ' long:' + $('#val_x').text() + TAB + ' prec:' + $('#val_prec').text();
        copyToClipboard(text);
        toastr.success("Resultats copiats al portapapers!");
    });
});
