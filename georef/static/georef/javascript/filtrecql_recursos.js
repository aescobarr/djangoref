function transformarJSONACQL(jsonStringFiltre){
    var filtre = null;
    if(jsonStringFiltre != ''){
        var jsonFiltre = JSON.parse(jsonStringFiltre);
        var condicions = jsonFiltre.filtre;
        for (var i=0; i<condicions.length; i++){
            filtre = transformarCondicioFiltreJSONACQL(filtre,condicions[i].operador,condicions[i].condicio,condicions[i].valor,condicions[i].not);

        }
    }
    return filtre;
}

function transformarNotCQL(filtre){
    var filtreNou = new OpenLayers.Filter.Logical({
        type: OpenLayers.Filter.Logical.NOT,
        filters: [filtre] });
    return filtreNou;
}

function transformarCondicioTipusACQL(idtipus){
    var filtre = new OpenLayers.Filter.Comparison({
        type: OpenLayers.Filter.Comparison.EQUAL_TO,
        property: "idsuport",
        value: idtipus
    });
    return filtre;
}

function transformarCondicioParaulaClauACQL(idtipus){
    var filtre = new OpenLayers.Filter.Comparison({
        type: OpenLayers.Filter.Comparison.LIKE,
        property: "paraulaclau",
        value: idtipus
    });
    return filtre;
}

function transformarCondicioPartNomACQL(partnomrecurs){
    var filtre = new OpenLayers.Filter.Comparison({
        type: OpenLayers.Filter.Comparison.LIKE,
        property: 'nom',
        value: '%'+partnomrecurs+'%'
    });
    return filtre;
}

function transformarCondicioGeograficACQL(geometria){
    var filtre = new OpenLayers.Filter.Spatial({
        type: OpenLayers.Filter.Spatial.WITHIN,
        property: 'carto_epsg23031',
        value: geometria
    });
    return filtre;
}

function transformarCondicioAcronimACQL(partnomtoponim){
    var filtre = new OpenLayers.Filter.Comparison({
        type: OpenLayers.Filter.Comparison.LIKE,
        property: "acronim",
        value: "%"+partnomtoponim+"%"
    });
    return filtre;
}




function transformarCondicioFiltreJSONACQL(filtreAnterior,operador,condicio,valor,not){
    var filtre,filtreNou;

    if('nom'==condicio){
        if('S'==not){
            filtreNou = transformarNotCQL(transformarCondicioPartNomACQL(valor));
        }else{
            filtreNou = transformarCondicioPartNomACQL(valor);
        }
    }else if('tipus'==condicio){
        if('S'==not){
            filtreNou = transformarNotCQL(transformarCondicioTipusACQL(valor));
        }else{
            filtreNou = transformarCondicioTipusACQL(valor);
        }
    }else if('paraulaclau'==condicio){
        if('S'==not){
            filtreNou = transformarNotCQL(transformarCondicioParaulaClauACQL(valor));
        }else{
            filtreNou = transformarCondicioParaulaClauACQL(valor);
        }
    }else if('acronim'==condicio){
        if('S'==not){
            filtreNou = transformarNotCQL(transformarCondicioAcronimACQL(valor));
        }else{
            filtreNou = transformarCondicioAcronimACQL(valor);
        }
    }else if('geografic'==condicio || 'geografic_geo'==condicio){
        var wktReader = new OpenLayers.Format.WKT();
        var features = wktReader.read(valor);
        var elem;
        var filtreGeoNou,filtreGeoTotal;
        elem = features.geometry;
        elemFiltre = elem.clone();
        if('S'==not){
            filtreGeoNou = transformarNotCQL(transformarCondicioGeograficACQL(elemFiltre));
        }else{
            filtreGeoNou = transformarCondicioGeograficACQL(elemFiltre);
        }
        if(filtreGeoTotal!=null){
            filtreGeoTotal = new OpenLayers.Filter.Logical({
                type: OpenLayers.Filter.Logical.OR,
                filters: [filtreGeoTotal,filtreGeoNou]
            });
        }else{
            filtreGeoTotal = filtreGeoNou;
        }
        filtreNou = filtreGeoTotal;
    }

    if(filtreAnterior!=null && 'and'==operador){
        filtre = new OpenLayers.Filter.Logical({
            type: OpenLayers.Filter.Logical.AND,
            filters: [filtreAnterior,filtreNou]
        });
    }else if(filtreAnterior!=null && 'or'==operador){
        filtre = new OpenLayers.Filter.Logical({
            type: OpenLayers.Filter.Logical.OR,
            filters: [filtreAnterior,filtreNou]
        });
    }else{
        filtre = filtreNou;
    }
    return filtre;
}
