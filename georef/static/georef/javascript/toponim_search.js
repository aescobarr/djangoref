var first_copy = true;

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
        var headers = [
            'name',
            'lat',
            'long',
            'prec',
            'prec_calc'
        ];
        var values = [
            $('#val_nom').text(),
            $('#val_y').text(),
            $('#val_x').text(),
            $('#val_prec').text(),
            $('#val_prec_calc').text()
        ];
        var headers_str = headers.join(TAB);
        var values_str = values.join(TAB);
        text = headers_str + '\n' + values_str;
        //text = $('#val_nom').text() + TAB + ' lat:' + $('#val_y').text() + TAB + ' long:' + $('#val_x').text() + TAB + ' prec:' + $('#val_prec').text() + TAB + ' prec_calc:' + $('#val_prec_calc').text();
        //copyToClipboard(text);
        if(first_copy){
            navigator.clipboard.writeText(text);
            first_copy = false;
        }else{
            navigator.clipboard.writeText(values_str);
        }
        toastr.success("Resultats copiats al portapapers!");
    });
});
