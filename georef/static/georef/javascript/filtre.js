function crearTaulaFiltre(jsonStringFiltre){
    var taula = $('#taulafiltre')[0];
    while (1<taula.children.length){
        taula.removeChild(taula.lastChild);
    }
    var jsonFiltre = JSON.parse(jsonStringFiltre);
    var condicions = jsonFiltre.filtre;
    for (var i=0; i<condicions.length; i++){
        insertCondicioFiltre(condicions[i].operador,condicions[i].condicio,condicions[i].valor,condicions[i].not,i, condicions[i].extra);
        indexTaula++;
    }

}

function createSelect(valors,idselected,idselect,onchange){
    var htmlSelect = '<select class="input-field"';
    if(idselect!=null && idselect!=undefined)
        htmlSelect += " id='"+idselect+"'";
    if(idselect!=null && idselect!=undefined)
        htmlSelect += " onchange='"+onchange+"'";
    htmlSelect += ">";
    for(var i=0;i<valors.length;i++){
        if(idselected==valors[i].id)
            htmlSelect += "<option id='"+valors[i].id+"' selected='selected'>"+valors[i].value+"</option>";
        else
            htmlSelect += "<option id='"+valors[i].id+"'>"+valors[i].value+"</option>";
    }
    htmlSelect += "</select>";
    return htmlSelect;
}

function createValor(condicio,valor, extra){
    if('nom'==condicio){
        return "<input type='text' value='"+valor+"' />";
    }else if('tipus'==condicio){
        return createSelect(valorsTipus,valor);
    }else if('pais'==condicio){
        return createSelect(valorsPaisos,valor);
    }else if('aquatic'==condicio){
        return createSelect(valorsAquatic,valor);
    }else if('nomautor'==condicio){
        return createSelect(valorsAutors,valor);
    }else if('versio'==condicio){
        return createSelect(valorsVersio,valor);
    }else if('geografic'==condicio){
        return createImportCartoButton(valor);
    }else if('arbre'==condicio){
        return "<input data-extra='" + extra + "' class='arbre' type='text' value='"+valor+"' />";
    }else{
        return "<input type='text' value='"+valor+"' />";
    }
}

function createCheckNot(valueNot){
    var htmlChck = "<input type='checkbox' name='chcknot' />";
    if("S"==valueNot)
        htmlChck = "<input type='checkbox' name='chcknot' checked='checked' />";
    return htmlChck;
}

function clearFeaturesMapa(){
    djangoRef.Map.editableLayers.clearLayers();
}

function esborrarFilaFiltre(indexTaulaAEsborrar){
    var fila = document.getElementById("fila_"+indexTaulaAEsborrar);
    if($('#select_condicio_'+indexTaulaAEsborrar).val()=='Filtre geogràfic'){
        clearFeaturesMapa();
    }
    fila.parentNode.removeChild(fila);
}

function insertCondicioFiltre(operador,condicio,valor,not,indexTaulaNovaFila,extra){
    var taula = $("#taulafiltre")[0];
    var selectOperador = createSelect(valorsOperadors,operador,'select_operador_'+indexTaulaNovaFila);
    if(taula.children.length==1){
        //només hi ha els titols de les columnes
        selectOperador = "&nbsp;";
    }
    var selectCondicio = createSelect(valorsCondicions,condicio,'select_condicio_'+indexTaulaNovaFila,'javascript:canviCondicio('+indexTaulaNovaFila+');');
    var valorCondicio = createValor(condicio,valor, extra);
    var checkNot = createCheckNot(not);
    var botoEsborrar = '<button id="addCondicio" onclick="javascript:esborrarFilaFiltre('+indexTaulaNovaFila+');return false;" type="button" class="btn btn-danger">' + gettext('Esborrar') + '<i class="fa fa-times" aria-hidden="true"></i></button>';
    var fila = "<td>"+selectOperador+"</td>";
    fila += "<td>"+checkNot+"</td>";
    fila += "<td>"+selectCondicio+"</td>";
    fila += "<td id='value_"+indexTaulaNovaFila+"'>"+valorCondicio+"</td>";
    fila += "<td>"+botoEsborrar+"</td>";
    var newtr = document.createElement('tr');
    newtr.setAttribute('id','fila_'+indexTaulaNovaFila);
    newtr.setAttribute('name','trfiltre');
    newtr.innerHTML = fila;
    taula.appendChild(newtr);
    refreshAutocoComplete();
}

function refreshAutocoComplete(){
    $('#taulafiltre').find("input.arbre").autocomplete({
        source: function(request,response){
            $.getJSON( '/api_internal/toponimparesearch/?term=' + request.term, function(data){
                response($.map(data.results, function(item){
                    return {
                        label: item.nom_str
                        ,value: item.nom
                        ,id: item.id
                    };
                }));
            });
        },
        minLength: 2,
        select: function( event, ui ) {
            var arbreid = ui.item.id + '$' + ui.item.value;
            $(this).attr('data-extra', arbreid);
            $(this).val(ui.item.label);
            return false;
        }
    });
}

function afegirCondicioFiltre(){
    insertCondicioFiltre("and", "", "", "N", indexTaula,"");
    indexTaula++;
    refreshAutocoComplete();
}

function canviCondicio(indexTaulaFila){
    var select = document.getElementById('select_condicio_'+indexTaulaFila);
    var indexSelect = select.selectedIndex;
    var valueCondicio = select.options[indexSelect].id;
    var tdValue = document.getElementById('value_'+indexTaulaFila);
    var valorCondicio = createValor(valueCondicio,"", "");
    tdValue.innerHTML = valorCondicio;
    refreshAutocoComplete();
}

function mostrarGeoJSON(valor){
    var wkt = new Wkt.Wkt();
    wkt.read(valor);
    var geoJSONLayer = L.geoJson(wkt.toJson());
    geoJSONLayer.eachLayer(
        function(l){
            djangoRef.Map.editableLayers.addLayer(l);
        }
    );
}

function centrarMapaADigitalitzacio(valor){
    map.map.fitBounds(djangoRef.Map.editableLayers.getBounds());
}

function createImportCartoButton(valor){
    var boto = gettext('Cal digitalitzar una geometria sobre el mapa');
    if(valor!=null && ''!=valor){
        mostrarGeoJSON(valor);
        centrarMapaADigitalitzacio();
        //filtarCQLMapa(valor);
    }
    return boto;
}

function extreureJSONDeFiltre(){
    var json = '{"filtre":['
    var trs = document.getElementsByName("trfiltre");
    var tr;
    var tds;
    var fila;
    var jsonTD;
    for(var i=0;i<trs.length;i++){
        fila = '{';
        tr = trs[i];
        jsonTD = extreureOperadorJSON(tr.children[0]);
        fila += jsonTD + ',';
        jsonTD = extreureNotJSON(tr.children[1]);
        fila += jsonTD + ',';
        jsonTD = extreureCondicioJSON(tr.children[2]);
        fila += jsonTD + ',';
        jsonTD = extreureValorJSON(tr.children[2],tr.children[3]);
        fila += jsonTD;
        fila += '}';
        json += fila;
        if(i+1<trs.length)
            json+=',';
    }
    json += ']}';
    return json;
}

function extreureIdSelect(td){
    var select = td.children[0];
    var index = select.selectedIndex;
    var option = select.options[index];
    return option.id;
}

function extreureValorSelect(td){
    var select = td.children[0];
    var index = select.selectedIndex;
    var option = select.options[index];
    return option.text;
}

function getWKTDeObjectesDigitalitzats(){
    var geoJSON = djangoRef.Map.editableLayers.toGeoJSON();
    var wkts = [];
    var accum;
    //var wkt = new Wkt.Wkt();
    for(var i=0; i<geoJSON.features.length; i++){
        geometry_n = geoJSON.features[i];
        //wkt.read( JSON.stringify(geometry_n) );
        var wkt = new Wkt.Wkt(JSON.stringify(geometry_n));
        wkts.push(wkt);
        //wkt.merge( new Wkt.Wkt(JSON.stringify(geometry_n)) );
    }
    for(var i = 0; i < wkts.length; i++){
        if(i == 0){
            accum = wkts[0];
        }else{
            if (i + 1 > wkts.length ){
                return accum.write();
            }else{
                accum = accum.merge(wkts[i]);
            }
        }
    }
    if(accum){
        return accum.write();
    }else{
        return '';
    }
}

function getGeoJSONDeObjectesDigitalitzats(){
    return JSON.stringify(djangoRef.Map.editableLayers.toGeoJSON());
}

function extreureValorJSON(tdCondicio,tdValor){
    var json = '"valor":"';
    var idCondicio = extreureIdSelect(tdCondicio);
    if('nom'==idCondicio){
        var inputTxt = tdValor.children[0];
        var txt = inputTxt.value;
        json = '"valor":"'+txt+'"';
    }else if('arbre'==idCondicio){
        var inputTxt = tdValor.children[0];
        var txt = inputTxt.value;
        var extra = inputTxt.getAttribute('data-extra');
        json = '"valor":"'+txt+'","extra":"' + extra + '"';
    }else if('tipus'==idCondicio || 'pais'==idCondicio || 'aquatic'==idCondicio || 'nomautor'==idCondicio || 'versio'==idCondicio){
        var idValor = extreureIdSelect(tdValor);
        var etiquetaValor = extreureValorSelect(tdValor);
        json = '"valor":"'+idValor+'","text_valor":"'+ etiquetaValor +'"';
    }else if('geografic'==idCondicio){
        //var idValor = getGeoJSONDeObjectesDigitalitzats();
        var idValor = getWKTDeObjectesDigitalitzats();
        json = '"valor":"'+idValor+'"';
    }else{
        json = '"valor":""';
    }
    return json;
}

function extreureCondicioJSON(td){
    var select = td.children[0];
    var index = select.selectedIndex;
    var option = select.options[index];
    var json = '"condicio":"'+option.id+'"';
    return json;
}

function extreureOperadorJSON(td){
    var operador = "";
    if(td.children.length>0){
        var select = td.children[0];
        var index = select.selectedIndex;
        var option = select.options[index];
        operador = option.id;
    }
    var json = '"operador":"'+operador+'"';
    return json;
}

function extreureNotJSON(td){
    var chck = td.children[0];
    var not = "N";
    if(chck.checked)
        not = "S";
    var json = '"not":"'+not+'"';
    return json;
}

$( '#addCondicio' ).click(function() {
    afegirCondicioFiltre();
});

function clearTaula(idtaula){
    $('#' + idtaula).find('tr[id*="fila_"]').remove();
}

function filterMap(){
    var valorJson = extreureJSONDeFiltre();
    setCookie('filtre_t',valorJson,1);
    var valorOrg = getCookie('torg' + current_user_id);
    if(valorOrg != ''){
        //Append org filter
        var filtreJson = JSON.parse(valorJson);
        if ( filtreJson.filtre.length > 0 ){
            filtreJson.filtre.push( { "condicio":"org", "not":"", "operador":"and", "text_valor":"", "valor":valorOrg } );
        }else{
            filtreJson.filtre.push( { "condicio":"org", "not":"", "operador":"", "text_valor":"", "valor":valorOrg } );
        }
        valorJson = JSON.stringify(filtreJson);
    }
    var activeOverlays = djangoRef.Map.getActiveOverlays();
    for(var i = 0; i < activeOverlays.length; i++){
        var layer = activeOverlays[i];
        filterCQL(valorJson,layer);
    }
}

function filter(){
    filterMap();
    table.ajax.reload();
}

function filterCQL(valorJson,layer){
    var cql = transformarJSONACQL(valorJson);
    if(cql == null){
        layer.setParams({cql_filter:'1=1'});
    }else{
        var cql_filter_text = new OpenLayers.Format.CQL().write(cql);
        //toastr.info(cql_filter_text);
        layer.setParams({cql_filter:cql_filter_text});
    }

}
