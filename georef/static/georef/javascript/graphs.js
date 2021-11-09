$(document).ready(function() {

    var georeferenciadors = [];
    var toponims_georef = [];
    for (var i = 0; i < toponims_georeferenciador.length; i++){
        georeferenciadors.push(toponims_georeferenciador[i][1]);
        toponims_georef.push(toponims_georeferenciador[i][0]);
    }

    /*
    var paisos = [];
    var toponims_per_pais = [];

    for (var i = 0; i < toponims_pais.length; i++){
        paisos.push(toponims_pais[i][0]);
        toponims_per_pais.push(toponims_pais[i][1]);
    }
    */

    var tipus = [];
    var tipus_per_pais = [];
    for (var i = 0; i < toponims_tipus.length; i++){
        tipus.push(toponims_tipus[i][0]);
        tipus_per_pais.push(toponims_tipus[i][1]);
    }

    var pie_data = [];
    for (var i = 0; i < toponims_aquatic.length; i++){
        if(toponims_aquatic[i][0]=='S'){
            pie_data.push({ name: gettext('Aquàtic'), y: toponims_aquatic[i][1] })
        }else{
            pie_data.push({ name: gettext('Terrestre'), y: toponims_aquatic[i][1] })
        }
    }

    var recursos = [];
    var tipus_per_recurs = [];
    for (var i = 0; i < recursos_tipus.length; i++){
        recursos.push(recursos_tipus[i][0]);
        tipus_per_recurs.push(recursos_tipus[i][1]);
    }

    var spawn_pie = function(div_id, title, series_name, series_data){
        Highcharts.chart(div_id, {
            chart: {
                plotBackgroundColor: null,
                plotBorderWidth: null,
                plotShadow: false,
                type: 'pie'
            },
            title: {
                text: title
            },
            tooltip: {
                pointFormat: '{series.name}: <b>{point.y}</b>'
            },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: true,
                        format: '<b>{point.name}</b>: {point.y}',
                        style: {
                            color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                        }
                    }
                }
            },
            series: [{
                name: series_name,
                colorByPoint: true,
                data: series_data
            }]
        });
    }

    var spawn_chart = function(div_id,title,yaxis_title,series_name,cats,data, x_label_rotation, fontsize){
        Highcharts.chart(div_id, {
            chart: {
                type: 'column'
            },
            title: {
                text: title
            },
            xAxis: {
                categories: cats,
                crosshair: true,
                labels: {
                    rotation: x_label_rotation,
                    style: {
                        fontSize: fontsize
                    }
                }
            },
            yAxis: {
                type: 'logarithmic',
                //min: 0,
                title: {
                    text: yaxis_title
                }
            },
            tooltip: {
                headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                    '<td style="padding:0"><b>&nbsp;{point.y}</b></td></tr>',
                footerFormat: '</table>',
                shared: true,
                useHTML: true
            },
            plotOptions: {
                column: {
                    pointPadding: 0.2,
                    borderWidth: 0
                },
                /*series:{
                    dataLabels:{
                        enabled: true
                    }
                }*/
            },
            series: [{
                name: series_name,
                data: data,
                showInLegend: false
            }]
        });
    }

    /*
    spawn_chart('toponims_per_pais',gettext('Número de topònims per país'),gettext('Número de topònims'),gettext('Número de topònims'),paisos,toponims_per_pais,-85,'8px');
    spawn_chart('toponims_per_georeferenciador',gettext('Número de topònims per georeferenciador'),gettext('Número de topònims'),gettext('Número de topònims'),georeferenciadors,toponims_georef,-45,'12px');
    spawn_chart('toponims_per_tipus',gettext('Número de topònims per tipus'),gettext('Número de topònims'),gettext('Número de topònims'),tipus,tipus_per_pais,-45,'12px');
    spawn_pie('toponims_humitat',gettext('Número de topònims per aquàtic/terrestre'),gettext('Topònims'),pie_data);
    spawn_chart('recursos_tipus',gettext('Número de recursos georeferenciació per tipus'),gettext('Número de recursos'),gettext('Número de recursos'),recursos,tipus_per_recurs,-45,'12px');
    */

    spawn_chart('toponims_per_georeferenciador',gettext('Número de topònims per georeferenciador'),'','',georeferenciadors,toponims_georef,-45,'12px');
    spawn_chart('toponims_per_tipus',gettext('Número de topònims per tipus'),'','',tipus,tipus_per_pais,-45,'12px');
    spawn_pie('toponims_humitat',gettext('Número de topònims per aquàtic/terrestre'),'',pie_data);
    spawn_chart('recursos_tipus',gettext('Número de recursos georeferenciació per tipus'),'','',recursos,tipus_per_recurs,-45,'12px');


});
