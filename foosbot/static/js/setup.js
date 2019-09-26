$(document).ready(function () {
    
    $(document).on('click', '.edit_player', function (e) {
        var row = $(this).parent().parent();
        $('#player_id').val(row.find('.id').html())
        $('#player_fname').val(row.find('.fname').html())
        $('#player_lname').val(row.find('.lname').html())
        $('#player_photo').val(row.find('.photo').attr('src'))
        $('#player_rfid').val(row.find('.rfid').html())
        $('#modal_message').html('')
       
        $('#player_modal').modal('show');
    });

    $(document).on('click', '.remove_player', function (e) {
        if (confirm('Are you sure you want to delete a player?')){
            player_id = $(this).parent().parent().attr('id')
            deletePlayer(player_id)
        }
    });

    $('#remove_slack').click(function(e){
        if (confirm('Are you sure you want to remove slack integration?')){
            console.log('removeo')
            deleteSlack();
        }
    });

    $(document).on('click', '#id_new_player_button', function (e) {
        $('#player_id').val('')
        $('#player_fname').val('')
        $('#player_lname').val('')
        $('#player_photo').val('')
        $('#player_rfid').val('')
        $('#modal_message').html('')
    });

    data = {
        account_id: account_id,
        players: [
            { id: 1, fname: '', lname: '', photo: '', rfid: '' },
        ]
    }

    url = '/' + data.account_id + '/player'

    // The object is added to a Vue instance
    var vm = new
        Vue({
            el: '#app_players',
            delimiters: ['[[', ']]'],
            data: data,
        })

    function refresh() {
        $.ajax({
            url: url,
            type: "POST",
            data: JSON.stringify({ '': '' }),
            contentType: 'application/json',
            success: function (response) {
                r = JSON.parse(response)
                data.players = r.result;
            },
            error: function (jXHR, textStatus, errorThrown) {
                console.log(errorThrown);
            }
        });

    }

    refresh()

    $('#id_player_form').on('submit', function(e) {
        e.preventDefault();
        player_data = $(this).serializeArray()
        player_data = getFormData(player_data)
        post_data={action:'patch', player:player_data}
        $.ajax({
            url : url,
            type: "PATCH",
            data: JSON.stringify(post_data),
            contentType: 'application/json',
            success: function (response) {
                r = JSON.parse(response)
                if (r.status == 'success'){
                    refresh()
                    $('#player_modal').modal('hide');
                }else{
                    console.log(r.status)
                    $("#modal_message").html(r.status)
                }
                
            },
            error: function (jXHR, textStatus, errorThrown) {
                console.log(errorThrown);
            }
        });
    });

    function getFormData(unindexed_array){
        var indexed_array = {};
    
        $.map(unindexed_array, function(n, i){
            indexed_array[n['name']] = n['value'];
        });
    
        return indexed_array;
    }

    function deletePlayer(player_id){
        post_data={action:'delete', player:{id:player_id}}
        $.ajax({
            url : url,
            type: "PATCH",
            data: JSON.stringify(post_data),
            contentType: 'application/json',
            success: function (response) {
                r = JSON.parse(response)
                if (r.status == 'success'){
                    refresh()
                }
            },
            error: function (jXHR, textStatus, errorThrown) {
                console.log(errorThrown);
            }
        });
    }

    function deleteSlack(){
        post_data={action:'remove_slack'}
        $.ajax({
            url : '/'+account_id+'/remove_slack',
            type: "POST",
            data: JSON.stringify(post_data),
            contentType: 'application/json',
            success: function (response) {
                r = JSON.parse(response)
                if (r.status == 'success'){
                    location.reload();
                }else{
                    alert('Error occured removing slack.')
                }
            },
            error: function (jXHR, textStatus, errorThrown) {
                alert('Error occured communicating with server.')
            }
        });
    }


});    
// 	render_table(urls);



// function render_table(urls){
// 	var table_html = '';
// 	for (var i = 0; i < urls.length; i++) {
// 		table_html += `
// 			<tr>
// 			<td style = "width:24px"><span id = `+urls[i]['id']+` class = 'remove_page' style="cursor: pointer"> <i class="glyphicon glyphicon-trash pale"> </i> </span> </td>
// 			<td> <a href = "`+urls[i]['url']+`"> `+urls[i]['url']+` </a> </td>
// 			</tr>`;
//     }
// 	$('#id_pages_table').html(table_html);
// }