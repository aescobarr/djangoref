(function(){

    if (typeof(L) == 'undefined' || typeof(L.map) == 'undefined') throw 'Leaflet map library must be loaded';

    if (typeof(L.gridLayer.googleMutant) == 'undefined') throw 'Google Mutant leaflet library must be loaded';

    if (typeof(L.control.coordinates) == 'undefined') throw 'Leaflet.Coordinates library must be loaded';

    if (typeof djangoRef === 'undefined') this.djangoRef = {};

    if (typeof djangoRef.Map === 'undefined') this.djangoRef.Map = {};

    var osmUrl='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
    var osmAttrib='Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors';

    djangoRef.Map.osm = new L.TileLayer(
        osmUrl,
        {minZoom: 2, maxZoom: 12, attribution: osmAttrib}
    );

    /*
    djangoRef.Map.roads = L.gridLayer.googleMutant({
        type: 'roadmap'
    });

    djangoRef.Map.satellite = L.gridLayer.googleMutant({
        type: 'satellite'
    });

    djangoRef.Map.terrain = L.gridLayer.googleMutant({
        type: 'terrain'
    });

    djangoRef.Map.hybrid = L.gridLayer.googleMutant({
        type: 'hybrid'
    });
    */

    djangoRef.Map.bing = L.tileLayer.bing(
        {
            'bingMapsKey':bing_key
        }
    );

    djangoRef.Map.bing_road = L.tileLayer.bing(
        {
            'bingMapsKey':bing_key,
            'imagerySet':'Road'
        }
    );

    djangoRef.Map.bing_road_dark = L.tileLayer.bing(
        {
            'bingMapsKey':bing_key,
            'imagerySet':'CanvasDark'
        }
    );

    djangoRef.Map.bing_aerial_labels = L.tileLayer.bing(
        {
            'bingMapsKey':bing_key,
            'imagerySet':'AerialWithLabels'
        }
    );

    djangoRef.Map.overlays = {};

    djangoRef.Map.map = null;

    djangoRef.Map.editableLayers = new L.FeatureGroup();

    djangoRef.Map.featureInfoFormatters = null;

    djangoRef.Map.currentlyEditing = false;

    djangoRef.Map.createMap = function(options) {
        options = options || {};
        options = $.extend({},
            {
                div: 'map',
                center: new L.LatLng(40.58, -3.25),
                zoom: 2,
                consultable: [],
                editable: false,
                overlays: [],
                show_coordinates: true,
                show_centroid_after_edit: false,
                attribution_position: 'bottomright',
                show_scale: 'true',
                highlight: false
            },
            options);

        var map;

        map = new L.Map(options.div,{attributionControl: false});

        L.control.attribution({
            position: options.attribution_position
        }).addTo(map);

        var baseMaps = [
            {
                groupName: 'Open Street Maps',
                expanded: false,
                layers: {
                    'Open Street Map': djangoRef.Map.osm
                }
            }
            ,{
                groupName: 'Microsoft Bing Maps',
                expanded: false,
                layers: {
                    'Aerial': djangoRef.Map.bing,
                    'Aerial+roads': djangoRef.Map.bing_aerial_labels,
                    'Roads': djangoRef.Map.bing_road,
                    'Roads dark': djangoRef.Map.bing_road_dark
                }
            }
        ];

        var overlays_control_config = options.overlays_control_config;

        var controlCapes_options = {
            container_width 	: '300px',
            container_height    : '500px',
            container_maxHeight : '500px',
            group_maxHeight     : '120px',
            exclusive       	: false
        };

        controlCapes_options = $.extend({}, controlCapes_options, options.controlcapes_options);

        if(options.formatters){
            djangoRef.Map.featureInfoFormatters = options.formatters;
        }

        if(options.show_coordinates){
            coordinates_options = {
                position:"bottomright",
                enableUserInput:false
            };
            coordinates_options = $.extend({}, coordinates_options, options.coordinates_options);
            //coordControl = L.control.coordinates({position:"bottomleft",enableUserInput:false});
            //coordControl = L.control.coordinates({position:"bottomright",enableUserInput:false});
            coordControl = L.control.coordinates(coordinates_options);
            map.addControl(coordControl);
        }

        if(options.show_scale){
            L.control.scale().addTo(map);
        }

        if(options.show_centroid_after_edit){
            djangoRef.Map.centroid = new L.geoJSON();
            map.addLayer(djangoRef.Map.centroid);
        }

        if(options.editable){

            var MyCustomMarker = L.Icon.extend({
                options: {
                    shadowUrl: null,
                    iconAnchor: new L.Point(12, 12),
                    iconSize: new L.Point(24, 24),
                    iconUrl: 'link/to/image.png'
                }
            });

            var draw_options = {
                position: 'topleft',
                draw: {
                    polyline: {
                        shapeOptions: {
                            color: '#f357a1',
                            weight: 10
                        }
                    },
                    polygon: {
                        allowIntersection: false, // Restricts shapes to simple polygons
                        drawError: {
                            color: '#e1e100', // Color the shape will turn when intersects
                            message: '<strong>Oh snap!<strong> you can\'t draw that!' // Message that will show when intersect
                        },
                        shapeOptions: {
                            color: '#da5d55'
                        }
                    },
                    circle: false, // Turns off this drawing tool
                    /*circle:{
                        shapeOptions: {
                            fill:true
                        }
                    },*/
                    rectangle: false,
                    /*rectangle: {
                        shapeOptions: {
                            clickable: false
                        }
                    },*/
                    /*marker: {
                        icon: new MyCustomMarker()
                    },*/
                    marker: {},
                    //marker: false,
                    circlemarker: false
                },
                edit: {
                    featureGroup: djangoRef.Map.editableLayers, //REQUIRED!!
                    remove: true
                }
            };

            var drawControl = new L.Control.Draw(draw_options);
            map.addControl(drawControl);
            map.addLayer(djangoRef.Map.editableLayers);

        }

        controlCapes = L.Control.styledLayerControl(baseMaps, overlays_control_config, controlCapes_options);
        map.addControl(controlCapes);
        controlCapes.selectLayer(djangoRef.Map.osm);

        map.setView(options.center,options.zoom);

        if(options.consultable && options.consultable.length > 0){
            map.on('click', function(evt){
                var param_layers = [];
                for(var i=0; i < options.consultable.length; i++){
                    //Just query currently active layers
                    activeLayers = djangoRef.Map.getActiveOverlays();
                    for(var j = 0; j < activeLayers.length; j++){
                        if( options.consultable[i].wmsParams.layers == activeLayers[j].options.layers ){
                            param_layers.push( options.consultable[i].wmsParams.layers );
                        }
                    }
                }
                if(param_layers.length > 0 && djangoRef.Map.currentlyEditing == false){
                    var querylayers = param_layers.join(',');
                    getFeatureInfo(evt,querylayers);
                }
            });
        }

        map.on(L.Draw.Event.DRAWSTART, function (e) {
            djangoRef.Map.currentlyEditing = true;
        });

        map.on(L.Draw.Event.DRAWSTOP, function (e) {
            djangoRef.Map.currentlyEditing = false;
        });

        map.on(L.Draw.Event.CREATED, function (e) {
            var type = e.layerType,layer = e.layer;
            djangoRef.Map.editableLayers.addLayer(layer);
            if(options.show_centroid_after_edit){
                djangoRef.Map.refreshCentroid();
            }
            djangoRef.Map.editableLayers.bringToFront();
        });

        map.on(L.Draw.Event.EDITED, function (e) {
            if(options.show_centroid_after_edit){
                djangoRef.Map.refreshCentroid();
            }
            djangoRef.Map.editableLayers.bringToFront();
        });

        map.on(L.Draw.Event.DELETED, function (e) {
            if(options.show_centroid_after_edit){
                djangoRef.Map.refreshCentroid();
                djangoRef.Map.centroid.clearLayers();
            }
            djangoRef.Map.editableLayers.bringToFront();
        });

        if(options.overlays && options.overlays.length > 0){
            register_overlays(options.overlays);
        }

        if(options.state){
            djangoRef.Map.setState(options.state);
        }

        if(options.highlight){
            var myStyle = {
                "color": "#ff7800",
                "weight": 5,
                "opacity": 0.65
            };
            var geojsonMarkerOptions = {
                radius: 8,
                fillColor: "#ff7800",
                color: "#000",
                weight: 1,
                opacity: 1,
                fillOpacity: 0.8
            };
            djangoRef.Map.highLightLayer = L.geoJSON(null,{
                    style: myStyle,
                    pointToLayer:
                        function (feature, latlng) {
                            return L.circleMarker(latlng, geojsonMarkerOptions);
                    }
                }
            );
            map.addLayer( djangoRef.Map.highLightLayer );
        }

        djangoRef.Map.map = map;

        return djangoRef.Map;
    };

    djangoRef.Map.highLightVersion = function(idversion){
        $.ajax({
            url: '/geojson_site_geom/?idtoponim=' + idversion,
            method: "GET",
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                if(djangoRef.Map.highLightLayer){
                    djangoRef.Map.highLightLayer.clearLayers();
                    djangoRef.Map.highLightLayer.addData(data.geometry);
                    djangoRef.Map.map.fitBounds([ [data.extent[1], data.extent[0]], [data.extent[3], data.extent[2]] ], { 'maxZoom': 11 });
                }
            },
            error: function(jqXHR, textStatus, errorThrown){
                console.log(textStatus);
            }
        });
    }

    djangoRef.Map.getCenter = function(){
        return djangoRef.Map.map.getCenter();
    };

    djangoRef.Map.getZoom = function(){
        return djangoRef.Map.map.getZoom();
    };

    djangoRef.Map.hasLayer = function(layer){
        return djangoRef.Map.map.hasLayer(layer);
    };

    djangoRef.Map.getDigitizedFeaturesJSON = function(){
        if(djangoRef.Map.editableLayers){
            var geoJson = djangoRef.Map.editableLayers.toGeoJSON();
            return geoJson;
        }
    }

    djangoRef.Map.getActiveOverlays = function(){
        var retVal = [];
        for(var k in djangoRef.Map.overlays){
            k_layer = djangoRef.Map.overlays[k];
            if(djangoRef.Map.map.hasLayer(k_layer)){
                retVal.push(k_layer);
            }
        }
        return retVal;
    };

    djangoRef.Map.getOverlayByHandle = function(handle){
        return djangoRef.Map.overlays[handle];
    };

    djangoRef.Map.addOverlay = function(layer,layer_handle){
        overlays[layer_handle] = layer;
    };

    djangoRef.Map.deselectAllOverlays = function(){
        for(var k in djangoRef.Map.overlays){
            k_layer = djangoRef.Map.overlays[k];
            controlCapes.unSelectLayer(k_layer);
        }
    };

    djangoRef.Map.setState = function(state){
        djangoRef.Map.deselectAllOverlays();
        if(state.overlays && state.overlays.length > 0){
            for(var i = 0; i < state.overlays.length; i++){
                controlCapes.selectLayer( djangoRef.Map.overlays[state.overlays[i]] );
            }
        }
        if(state.base){
            var l = eval(state.base);
            if(l == null){
                controlCapes.selectLayer(djangoRef.Map.osm);
            }else{
                controlCapes.selectLayer(eval(state.base));
            }
        }
    };

    djangoRef.Map.getState = function(){
        var overlay_list = [];
        var base_layer = null;
        for (var k in djangoRef.Map.overlays){
            if(djangoRef.Map.map && djangoRef.Map.map.hasLayer(djangoRef.Map.overlays[k])){
                overlay_list.push(k);
            }
        }
        var base_layers = ['djangoRef.Map.bing','djangoRef.Map.bing_road','djangoRef.Map.bing_road_dark','djangoRef.Map.bing_aerial_labels','djangoRef.Map.osm'];
        //var base_layers = ['djangoRef.Map.roads','djangoRef.Map.satellite','djangoRef.Map.terrain','djangoRef.Map.hybrid','djangoRef.Map.osm'];
        for( var i = 0; i < base_layers.length; i++){
            if(djangoRef.Map.map && djangoRef.Map.map.hasLayer(eval(base_layers[i]))){
                base_layer = base_layers[i];
            }
        }
        var state = {
            overlays : overlay_list,
            base: base_layer
        };

        return state;
    };

    djangoRef.Map.getCurrentCentroid = function(){
        var geoJson = djangoRef.Map.editableLayers.toGeoJSON();
        if (geoJson.features.length > 0){
            var centroid = turf.centroid(geoJson);
            var dist = getMaxDistanceMetersFromCentroidToDigitizedGeometry(centroid);
            var dist_km = dist / 1000;
            return { 'centroid' : centroid, 'radius': dist_km };
        }
        return null;
    };

    djangoRef.Map.refreshCentroid = function(radius_km){
        /*djangoRef.Map.centroid.clearLayers();
        var centroid_data = djangoRef.Map.getCurrentCentroid();
        if(centroid_data != null){
            var centroid = centroid_data.centroid;
            var dist_km;
            if(radius_km){
                dist_km = radius_km
            }else{
                dist_km = centroid_data.radius;
            }
            if(dist_km > 0){
                var circle = turf.circle(centroid,dist_km);
                djangoRef.Map.centroid.addData(circle);
            }
        }*/
        if( djangoRef.Map.getDigitizedFeaturesJSON().features.length > 0 ){
            $.ajax({
                url: '/compute_centroid',
                method: "POST",
                data: { "geom": JSON.stringify(djangoRef.Map.getDigitizedFeaturesJSON().features) },
                beforeSend: function(xhr, settings) {
                    if (!csrfSafeMethod(settings.type)) {
                        var csrftoken = getCookie('csrftoken');
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                },
                success: function( centroid_data, textStatus, jqXHR ) {
                    //console.log(data);
                    //def.resolve(data.detail);
                    djangoRef.Map.centroid.clearLayers();
                    if(centroid_data != null){
                        var centroid = centroid_data.detail.centroid;
                        var dist_km;
                        if(radius_km){
                            dist_km = radius_km
                        }else{
                            dist_km = centroid_data.detail.radius / 1000;
                        }
                        if(dist_km > 0){
                            //var circle = turf.circle(centroid,dist_km);
                            var circle = centroid_data.detail.mbc_wgs;
                            var point = turf.point( [centroid.geometry.coordinates[0], centroid.geometry.coordinates[1]] );
                            djangoRef.Map.centroid.addData(circle);
                            djangoRef.Map.centroid.addData(point);
                        }
                    }
                },
                error: function(jqXHR, textStatus, errorThrown){
                    console.log(textStatus);
                    //def.reject(textStatus);
                }
            });
        }
    };

    var register_overlays = function(overlays){
        for (var i = 0; i < overlays.length; i++){
            djangoRef.Map.overlays[overlays[i].name] = overlays[i].layer;
        }
    };

    var showGetFeatureInfo = function (err, latlng, content) {
        //if (err) { console.log(err); return; }
        // do nothing if there's an error
        // Otherwise show the content in a popup, or something.
        if(content){
            var html = "";
            if(djangoRef.Map.highLightLayer){
                djangoRef.Map.highLightLayer.clearLayers();
            }
            for (feature in content.features){
                var feature_formatter_name = content.features[feature].id.split('.')[0];
                if(djangoRef.Map.featureInfoFormatters && djangoRef.Map.featureInfoFormatters[feature_formatter_name]){
                    html = html + djangoRef.Map.featureInfoFormatters[feature_formatter_name](content.features[feature]);
                }else{
                    html = html + JSON.stringify(content.features[feature]);
                }
                if(djangoRef.Map.highLightLayer){
                    djangoRef.Map.highLightLayer.addData(content.features[feature].geometry);
                }
            }
            if(html != ""){
                html = '<div style="height:150px;overflow:auto;">' + html + '</div>';
                const popup = L.popup({ maxWidth: 800}).setLatLng(latlng).setContent(html);
                if(djangoRef.Map.highLightLayer){
                    popup.on('remove', function() {
                        djangoRef.Map.highLightLayer.clearLayers();
                    });
                }
                popup.openOn(djangoRef.Map.map);
            }
        }
    };

    var getFeatureInfo = function(evt,querylayers){
        // Make an AJAX request to the server and hope for the best
        var url = getFeatureInfoUrl(evt.latlng,querylayers);
        $.ajax({
            url: url,
            success: function (data, status, xhr) {
                //var err = typeof data === 'string' ? null : data;
                var err = null;
                showGetFeatureInfo(err, evt.latlng, data);
            },
            error: function (xhr, status, error) {
                showGetFeatureInfo(error);
            }
        });
    };

    var getFeatureInfoUrl = function(latlng,querylayers){
        var zoom = djangoRef.Map.map.getZoom();
        var point = djangoRef.Map.map.latLngToContainerPoint(latlng, zoom);
        var size = djangoRef.Map.map.getSize();

        var params = {
            request: 'GetFeatureInfo',
            service: 'WMS',
            srs: 'EPSG:4326',
            styles: '',
            transparent: true,
            version: '1.1.1',
            format: 'image/jpeg',
            bbox: djangoRef.Map.map.getBounds().toBBoxString(),
            height: size.y,
            width: size.x,
            layers: querylayers,
            query_layers: querylayers,
            //info_format: 'text/html',
            info_format: 'application/json',
            feature_count: 10
        };

        params[params.version === '1.3.0' ? 'i' : 'x'] = point.x;
        params[params.version === '1.3.0' ? 'j' : 'y'] = point.y;

        return wms_url + L.Util.getParamString(params, wms_url, true);
    };

    /*
    var refreshCentroid = function(){
        djangoRef.Map.centroid.clearLayers();
        var centroid_data = djangoRef.Map.getCurrentCentroid();
        if(centroid_data != null){
            var centroid = centroid_data.centroid;
            var dist_km = centroid_data.radius;
            var circle = turf.circle(centroid,dist_km);
            djangoRef.Map.centroid.addData(circle);
        }
    };
    */

    var getMaxDistanceMetersFromCentroidToDigitizedGeometry = function(point){
        var coordinates = [];
        var options = {units: 'kilometers'};
        var min_distance = 0;
        for (var i = 0; i < djangoRef.Map.editableLayers.getLayers().length; i++){
            var feature_coords = turf.coordAll(djangoRef.Map.editableLayers.getLayers()[i].toGeoJSON());
            for (var j = 0; j < feature_coords.length; j++){
                coordinates.push( feature_coords[j] );
            }
        }
        for( var i = 0; i < coordinates.length; i++){
            var to = turf.point(coordinates[i]);
            var distance_m = turf.distance(point,to,options) * 1000;
            if (distance_m > min_distance){
                min_distance = distance_m;
            }
        }
        return min_distance;
    }

})();
