

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
   window.location.href = '/count/sales/list';
});


function convertFormToJSON(form) {
  return $(form)
    .serializeArray()
    .reduce(function (json, { name, value }) {
      json[name] = value;
      return json;
    }, {});
}


function get_charges_sales(){

    $('#search_inter_dates').click(function(event){
		event.preventDefault()
		initial_date = $('#id_init_date').val()
		final_date = $('#id_final_date').val()
		$.get('/count/sales/'+initial_date+'/'+final_date, function(data){
			$('#sales-list').html(data)
		})
	})
}



