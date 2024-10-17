var error_item_template = function(message){
    return `<li>${message}</li>`;
}

function single_similar_item_template(item){
    return `<li><a target="_blank" href="/toponims/update/${ item.toponim_id }/-1/">${ item.nom }</a></li>`;
}
