$(document).ready(function() {
    var valorFiltre = getCookie('filtre_t');

    if(valorFiltre){
        crearTaulaFiltre(valorFiltre);
    }
    var layer_toponims = djangoRef.Map.getOverlayByHandle('toponims');
    filterCQL(valorFiltre,layer_toponims);

    /*var el = $('#sidebar');
    L.DomEvent.disableScrollPropagation(el);*/
    var div = L.DomUtil.get('sidebar');
    L.DomEvent.on(div, 'mousewheel', L.DomEvent.stopPropagation);
    L.DomEvent.on(div, 'mousedown', L.DomEvent.stopPropagation);
    L.DomEvent.on(div, 'click', L.DomEvent.stopPropagation);
    L.DomEvent.on(div, 'dblclick', L.DomEvent.stopPropagation);
});
