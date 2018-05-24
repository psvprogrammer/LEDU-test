$(document).ready(function(){
    $('[data-toggle="popover"]').popover();
    // sort_events()
    vote_events();
});

function vote_events() {
    $("span.vote-star").each(function () {
        $(this).on('click', function (event) {
            var rate = $(this).attr('rate');
            var project_id = $(this).closest('div').attr('id').replace('vote-form_', '');
            send_vote(project_id, rate);
        });
    });
}


/** Sort event functions START **
function sort_events(){
    $('th[data="rate"]').click(function(){
        var sort = $(this).attr('sort');
        if (sort == 'asc'){
            $(this).attr('sort', 'desc');
        }
        else{
            $(this).attr('sort', 'asc');
        }

        rows = {};
        rates = {};
        $('#projects>tbody>tr').each(function (index, value) {
            rate = parseFloat($('#project_' + value.id + '_rate').text().trim());
            rows[index] = value;
            rates[index] = rate;
        });
        sorted_indxs = Object.keys(rates).sort(function(a,b){return rates[a]-rates[b]})
        if (sort == 'desc'){
            sorted_indxs = sorted_indxs.reverse();
        }
        var html_rows = '';
        for(var ind in sorted_indxs){
            html_rows += rows[ind].innerHTML;
        }
        $('#projects>tbody').replaceWith(html_rows);
    })
}
/** Sort event functions END **/


function send_vote(project_id, rate) {
    var vote_div = $('#vote-form_' + project_id).closest('tr');
    var data = {
        project_id: project_id,
        rate: rate,
    };
    ajaxPost('/ajax/vote/', data, function (content) {
        if (content.success){
            $('#vote-form_'+project_id+'>table>thead>tr>th').each(function () {
                $(this).find('span').removeClass('checked');
            });
            stars = vote_div.find('tr').first().children();
            rate = rate;
            for(var i = 0; i < 5; i++){
                if (i < rate){
                    stars[i].classList.add('checked');
                }
                else{
                    stars[i].classList.remove('checked');
                }
            }
        }
        else{
            // on false
            console.log(content);
        }
        show_popover(vote_div, content.popover);
    });
}



/*
* This function init and show default popover for element
* and freeze elem to prevent DB spam.
* Default delay is 3 sec.
* */
function show_popover(elem, content, freeze_elem) {
    if (!freeze_elem){
        freeze_elem = elem;
    }
    elem.popover({
        delay: { hide: 3000 },
        title: content.title,
        content: content.content,
        template: content.template,
        trigger: 'focus',
    });

    elem.popover('show');
    elem.popover('toggle');
    freeze_elem.prop('disabled', true);

    $(this).delay(1000).queue(function() {
        elem.popover('destroy');
        freeze_elem.prop('disabled', false);
        $(this).dequeue();
    });
}