$('#login-form').submit(function(event){
    event.preventDefault()
    var postval={}
    postval.username = $('#username').val()
    postval.password = $('#password').val()
    $.post('/login', postval, function(response){
        response = JSON.parse(response)
        console.log(response)
        if (response.status == 'success'){
            window.location = response.account_id + '/setup';
        }else{
            $('#message').html('Login Failed')
        }
    });
});