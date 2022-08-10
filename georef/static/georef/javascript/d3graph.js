var treePlugin;
$(document).ready(function() {

    function requestInitialRootData() {
        var id = '';
        var deferred = $.Deferred();
        $.ajax({
            url: '/statedata/?id=' + id,
            method: 'GET',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                deferred.resolve(data);
            },
            error: function(jqXHR, textStatus, errorThrown){
                deferred.reject(error);
            }
        });
        return deferred.promise();
    }

    function requestDirectChildrenData(id) {
        var deferred = $.Deferred();
        $.ajax({
            url: '/statedata/?id=' + id,
            method: 'GET',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                deferred.resolve(data);
            },
            error: function(jqXHR, textStatus, errorThrown){
                deferred.reject(error);
            }
        });
        return deferred.promise();
    }

    var initialRootDataRequestPromise = requestInitialRootData();
    initialRootDataRequestPromise.then(function(result) {
        var treePlugin = new d3.mitchTree.boxedTree()
            .setIsFlatData(true)
            .setData(result)
            .setElement(document.getElementById("visualisation"))
            .setIdAccessor(function(data) {
                return data.id;
            })
            .setParentIdAccessor(function(data) {
                return data.parentId;
            })
            .setBodyDisplayTextAccessor(function(data) {
                return data.name;
            })
            .setTitleDisplayTextAccessor(function(data) {
                return data.value;
            })
            .getNodeSettings()
					.setSizingMode('nodesize')
					.setVerticalSpacing(25)
					.setHorizontalSpacing(50)
					.back()
            .getLoadOnDemandSettings()
                .setLoadChildrenMethod(function(data, processData) {
                    var nodeIdToLoadChildrenFor = this.getId(data);
                    requestDirectChildrenData(nodeIdToLoadChildrenFor).then(function(result) {
                        processData(result);
                    }, function() {
                        throw arguments;
                    });
                })
                .setHasChildrenMethod(function(data) {
                    return data.value > 0;
                })
                .back()
            .initialize();
    });

    /*
    var set_loading = function(){
        $('#state_list').addClass('asyncload');
        $('#state_list').prop('disabled', true);
    }

    var finished_loading = function(){
        $('#state_list').removeClass('asyncload');
        $('#state_list').prop('disabled', false);
    }

    var load_state_data = function(id){
        set_loading();
        $.ajax({
            url: '/statedata/?id=' + id,
            method: 'GET',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                finished_loading();
                treePlugin = new d3.mitchTree.boxedTree()
                .setIsFlatData(true)
                .setData(data)
                .setElement(document.getElementById("visualisation"))
                .setIdAccessor(function(data) {
                    return data.id;
                })
                .setParentIdAccessor(function(data) {
                    return data.parentId;
                })
                .setBodyDisplayTextAccessor(function(data) {
                    return data.name;
                })
                .setTitleDisplayTextAccessor(function(data) {
                    return data.value;
                })
                .getNodeSettings()
					.setSizingMode('nodesize')
					.setVerticalSpacing(25)
					.setHorizontalSpacing(50)
					.back()
                .initialize();
            },
            error: function(jqXHR, textStatus, errorThrown){
                finished_loading();
                toastr.error("Error carregant dades");
            }
        });
    };

    $('#state_list').change(function(e){
        //console.log($(this).val());
        var id = $(this).val();
        load_state_data(id);
    });
    */


});
