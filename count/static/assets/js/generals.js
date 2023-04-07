$(document).ready(function() {

    $('select').select2();
    $('.select2-selection').css('height','43px')

    $('body').on("submit", "form" , function(event){
            $(this).find('input[type="submit"]').prop("disabled", true)
    })

    $('.table-normal').DataTable( {
          responsive: true,
          ordering: false,
          language: {
            processing:     "Procesamiento en courso...",
            search:         "Buscar&nbsp;:",
            lengthMenu:     "Mostrar _MENU_ &eacute;l&eacute;mentos",
            info:           "Mostrar de elelemento _START_ al _END_,     Total _TOTAL_ ",
            infoEmpty:      "Visualización del elemento 0 a 0 de 0 artículos",
            infoFiltered:   "(filtrados _MAX_ elementos del total)",
            infoPostFix:    "",
            loadingRecords: "Procesamiento en curso...",
            zeroRecords:    "No hay elementos para mostrar",
            emptyTable:     "No se encotraron elementos",
            paginate: {
                first:      "Primera",
                previous:   "Anterior",
                next:       "Próxima",
                last:       "Ültima"
            },
            aria: {
                sortAscending:  ": activar para ordenar la columna en orden ascendente",
                sortDescending: ": activar para ordenar la columna en orden descendente"
            }
        }
    });

    $("#myModal").on("click", ".close-modal", function () {
       window.location.href = ‘https://ExampleURL.com/’;
    });

})

 $(".sale").on("click", function(event) {

      event.preventDefault()
      form = $('form')
      const json = convertFormToJSON(form);
      $.post('/count/sale/{{ customer.id }}',json)
       .done(function( data ) {

          if (data != "{}"){
               $('.modal-title').html("Compra Exitosa")
               $('#modal-body').html(data)
               $('.modal-footer').html('<button type="button" class="close-modal btn btn-lg btn-secondary btn-block" data-dismiss="modal">Aceptar</button>')
               $("#myModal").modal({show: true})
          }else{
              alert("Datos de conexión inválidos")

          }
      });

  })

