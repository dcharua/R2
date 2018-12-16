/*
global
alertify: false
*/

/**
 * Create a new account.
 */
$('document').ready(function(){
  $('body').css('background-color', '#434343');
});
function signup() { // eslint-disable-line no-unused-vars
  if ($('#create-user-form').parsley().validate()) {
    $.ajax({
      type: 'POST',
      url: '/create_user',
      dataType: 'json',
      data: $('#create-user-form').serialize(),
      success: function(result) {
        if (result == 'duplicate') {
          const message = 'El usuario ya existe';
          alertify.notify(message, 'error', 5);
        } else {
          alertify.notify('Nuevo Usuario Creado.', 'success', 5);
          document.getElementById('login-button').click();
        }
      },
    });
  }
}

function register(){
  $("#login").css('display', 'none');
  $("#register").css('display', 'block');
}

function login(){
  $("#register").css('display', 'none');
  $("#login").css('display', 'block');
}
