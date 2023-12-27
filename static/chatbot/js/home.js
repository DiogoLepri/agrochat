$(document).ready(function(){
    $('#agrochat-button').on('click', function(e) {
        // Se o usuário estiver autenticado, simplesmente siga o comportamento padrão.
        if ($(this).data('authenticated') === "true") {
            return true;
        }

        // Previna o comportamento padrão para usuários não autenticados.
        e.preventDefault();

        $.ajax({
            url: '/chatbot',
            type: 'GET',
            dataType: 'json',
            success: function(data) {
                // Redireciona o usuário autenticado
                window.location.href = "/chatbot";
            },
            error: function(jqXHR, textStatus, errorThrown) {
                if (jqXHR.status == 401) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Erro',
                        text: jqXHR.responseJSON.error
                    });
                } else {
                    console.error("Ocorreu um erro ao verificar se o usuário está logado:", textStatus, errorThrown);
                }
            }
        });
    });
});