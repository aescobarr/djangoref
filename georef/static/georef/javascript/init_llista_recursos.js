$(document).ready(function() {
    var valorFiltre = getCookie('filtre_r');

    if(valorFiltre){
        crearTaulaFiltre(valorFiltre);
    }
    var layer_recursos = djangoRef.Map.getOverlayByHandle('recursos');
    filterCQL(valorFiltre,layer_recursos);

    var div = L.DomUtil.get('sidebar');
    L.DomEvent.on(div, 'mousewheel', L.DomEvent.stopPropagation);
    L.DomEvent.on(div, 'mousedown', L.DomEvent.stopPropagation);
    L.DomEvent.on(div, 'click', L.DomEvent.stopPropagation);
    L.DomEvent.on(div, 'dblclick', L.DomEvent.stopPropagation);
});
