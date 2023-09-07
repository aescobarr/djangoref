function transformarJSONACQL(jsonStringFiltre){
    var filtre = null;
    if(jsonStringFiltre != ''){
        var jsonFiltre = JSON.parse(jsonStringFiltre);
        var condicions = jsonFiltre.filtre;
        for (var i=0; i<condicions.length; i++){
            filtre = transformarCondicioFiltreJSONACQL(filtre,condicions[i].operador,condicions[i].condicio,condicions[i].valor,condicions[i].not,condicions[i].extra);

        }
    }
    return filtre;
}

function transformarCondicioPaisACQL(idpais){
    var filtre = new OpenLayers.Filter.Comparison({
        type: OpenLayers.Filter.Comparison.EQUAL_TO,
        property: 'idpais',
        value: idpais
    });
    return filtre;
}

function transformarCondicioVersioACQL(idversio){
    var filtre = new OpenLayers.Filter.Comparison({
        type: OpenLayers.Filter.Comparison.EQUAL_TO,
        property: 'idq',
        value: idversio
    });
    return filtre;
}

function transformarCondicioOrgACQL(idorg){
    var filtre = new OpenLayers.Filter.Comparison({
        type: OpenLayers.Filter.Comparison.EQUAL_TO,
        property: 'idorg',
        value: parseInt(idorg)
    });
    return filtre;
}

function transformarCondicioTipusACQL(idtipus){
    var filtre = new OpenLayers.Filter.Comparison({
        type: OpenLayers.Filter.Comparison.EQUAL_TO,
        property: 'idtipustoponim',
        value: idtipus
    });
    return filtre;
}

function transformarNotCQL(filtre){
    var filtreNou = new OpenLayers.Filter.Logical({
        type: OpenLayers.Filter.Logical.NOT,
        filters: [filtre] });
    return filtreNou;
}

function transformarCondicioNomAutorACQL(idautor){
    var filtre = new OpenLayers.Filter.Comparison({
        type: OpenLayers.Filter.Comparison.EQUAL_TO,
        property: 'iduser',
        value: idautor
    });
    return filtre;
}

function transformarCondicioPartNomACQL(partnomtoponim){
    var filtre = new OpenLayers.Filter.Comparison({
        type: OpenLayers.Filter.Comparison.LIKE,
        property: 'nomtoponim',
        value: '%'+partnomtoponim+'%'
    });
    return filtre;
}

function transformarCondicioArbreACQL(idarbre){
    var filtre = new OpenLayers.Filter.Comparison({
        type: OpenLayers.Filter.Comparison.LIKE,
        property: 'denormalized_toponimtree',
        value: '%'+idarbre+'%'
    });
    return filtre;
}

function transformarCondicioAquaticACQL(idaquatic){
    var filtre = new OpenLayers.Filter.Comparison({
        type: OpenLayers.Filter.Comparison.EQUAL_TO,
        property: 'aquatic',
        value: idaquatic
    });
    return filtre;
}

function transformarCondicioGeograficACQL(geometria){
    var filtre = new OpenLayers.Filter.Spatial({
        type: OpenLayers.Filter.Spatial.INTERSECTS,
        property: 'carto_epsg23031_cql',
        value: geometria
    });
    return filtre;
}


function transformarCondicioFiltreJSONACQL(filtreAnterior,operador,condicio,valor,not,extra){
    var filtre,filtreNou;

    if('nom'==condicio){
        if('S'==not){
            filtreNou = transformarNotCQL(transformarCondicioPartNomACQL(valor));
        }else{
            filtreNou = transformarCondicioPartNomACQL(valor);
        }
    }else if('nomautor'==condicio){
        if('S'==not){
            filtreNou = transformarNotCQL(transformarCondicioNomAutorACQL(valor));
        }else{
            filtreNou = transformarCondicioNomAutorACQL(valor);
        }
    }else if('arbre'==condicio){
        if('S'==not){
            filtreNou = transformarNotCQL(transformarCondicioArbreACQL(extra));
        }else{
            filtreNou = transformarCondicioArbreACQL(extra);
        }
    }else if('org'==condicio){
        filtreNou = transformarCondicioOrgACQL(valor);
    }else if('tipus'==condicio){
        if('S'==not){
            filtreNou = transformarNotCQL(transformarCondicioTipusACQL(valor));
        }else{
            filtreNou = transformarCondicioTipusACQL(valor);
        }
    }else if('pais'==condicio){
        if('S'==not){
            filtreNou = transformarNotCQL(transformarCondicioPaisACQL(valor));
        }else{
            filtreNou = transformarCondicioPaisACQL(valor);
        }
    }else if('aquatic'==condicio){
        if('S'==not){
            filtreNou = transformarNotCQL(transformarCondicioAquaticACQL(valor));
        }else{
            filtreNou = transformarCondicioAquaticACQL(valor);
        }
    }else if('versio'==condicio){
        if('S'==not){
            filtreNou = transformarNotCQL(transformarCondicioVersioACQL(valor));
        }else{
            filtreNou = transformarCondicioVersioACQL(valor);
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
