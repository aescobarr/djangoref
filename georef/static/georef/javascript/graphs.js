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

    var estats = [];
    var toponims_per_estat = [];
    for (var i = 0; i < estats_count.length; i++){
        estats.push(estats_count[i][0]);
        toponims_per_estat.push(estats_count[i][1]);
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

    var spawn_chart_options = function(options){
        options = options || {};
        options = $.extend({},
        {
            'yaxis_title':'',
            'series_name': '',
            'x_label_rotation': -45,
            'fontsize': '12px',
            'type': 'column',
            'height': 400,
            'yaxistype': 'linear',
            'xaxistype': 'linear'
        },
        options);

        Highcharts.chart(options.div_id, {
            chart: {
                type: options.type,
                height: options.height
                //type: 'bar',
                //inverted: false,
                //
            },
            title: {
                text: options.title
            },
            xAxis: {
                type: options.xaxistype,
                categories: options.cats,
                crosshair: true,
                labels: {
                    rotation: options.x_label_rotation,
                    style: {
                        fontSize: options.fontsize
                    }
                }
            },
            yAxis: {
                type: options.yaxistype,
                //min: 0,
                title: {
                    text: options.yaxis_title
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
                name: options.series_name,
                data: options.data,
                showInLegend: false
            }]
        });
    }

    var options_toponims_per_georeferenciador = {
        'div_id': 'toponims_per_georeferenciador',
        'title': '',
        'cats': georeferenciadors,
        'data': toponims_georef
    }
    spawn_chart_options( options_toponims_per_georeferenciador );

    var options_toponims_per_tipus = {
        'div_id': 'toponims_per_tipus',
        'title': '',
        'cats': tipus,
        'data': tipus_per_pais,
        'type': 'bar',
        'height': 2200,
        'x_label_rotation': 0
    }
    spawn_chart_options( options_toponims_per_tipus );

    spawn_pie('toponims_humitat',gettext('Número de topònims per aquàtic/terrestre'),'',pie_data);

    var options_recursos_tipus = {
        'div_id': 'recursos_tipus',
        'title': '',
        'cats': recursos,
        'data': tipus_per_recurs
    }
    spawn_chart_options( options_recursos_tipus );

    var toponims_per_estat_options = {
        'div_id': 'toponims_estat_graph',
        'title': '',
        'cats': estats,
        'data': toponims_per_estat,
        'type': 'bar',
        'height': 2200,
        'x_label_rotation': 0,
        'yaxistype' : 'logarithmic',
        //'xaxistype' : 'logarithmic',
    }
    spawn_chart_options( toponims_per_estat_options );


});
