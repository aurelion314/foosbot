$(document).ready(function () {

data = {
    account_id:100,
    players:[
        {id: 1, fname: 'Test', lname: 'McTesterson', photo:'', rfid:''},
    ]
}

url = '/'+data.account_id+'/player'

// The object is added to a Vue instance
var vm = new
Vue({
    el: '#app_players',
    delimiters: ['[[', ']]'],
    data: data
})

function refresh(){
    $.ajax({
        url : url,
        type: "POST",
        data: JSON.stringify({'':''}),
        contentType: 'application/json',
        success: function (response) {
            r = JSON.parse(response)
            console.log(response);
            data.players = r.result;
        },
        error: function (jXHR, textStatus, errorThrown) {
            console.log(errorThrown);
        }
    });
}

refresh()


});
// 	render_table(urls);

//     $('#id_new_page_form').on('submit', function(e) {
//         e.preventDefault();
//         data = $(this).serializeArray()
//         data = data.reduce(function(m,o){ m[o.name] = o.value; return m;}, {});
//         $.ajax({
//             url : $(this).attr('action') || window.location.pathname,
//             type: "POST",
//             data: JSON.stringify(data),
//             contentType: 'application/json',
//             success: function (response) {
//                 console.log(response);
//                 urls.push({"url":data.url, "id":response});
//                 render_table(urls);
//             },
//             error: function (jXHR, textStatus, errorThrown) {
//                 console.log(errorThrown);
//             }
//         });
//     });

//     $('body').on('click', '.remove_page', function(e) {
//     	e.preventDefault();
//     	console.log(this)
//         data = {"action": "remove_page", "id":this.id}
//         $.ajax({
//             url : '/setup_edit',
//             type: "POST",
//             data: JSON.stringify(data),
//             contentType: 'application/json',
//             success: function (response) {
//                 console.log(response);
                
//                 for (var i = 0; i < urls.length; i++) {
//                 	if (urls[i].id == data.id)
//                		urls.splice(i,1);
//                 }
                
//                 render_table(urls);
//             },
//             error: function (jXHR, textStatus, errorThrown) {
//                 alert(errorThrown);
//             }
//         });
//     });
// });

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