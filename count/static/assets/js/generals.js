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


function get_charges_sales(username){

    $('#search_inter_dates').click(function(event){
		event.preventDefault()
		initial_date = $('#id_init_date').val()
		final_date = $('#id_final_date').val()

		if (username != ""){
            $.get('/count/sales/'+username+'/'+initial_date+'/'+final_date, function(data){
                $('#sales-list').html(data)
            })
		}else{
		    $.get('/count/sales/'+initial_date+'/'+final_date, function(data){
			    $('#sales-list').html(data)
		    })
		}

	})
}



$( function() {

    // There's the gallery and the trash
    var $gallery = $( "#gallery" ),
      $trash = $( "#trash" );

    // Let the gallery items be draggable
    $( "li", $gallery ).draggable({
      cancel: "a.ui-icon", // clicking an icon won't initiate dragging
      revert: "invalid", // when not dropped, the item will revert back to its initial position
      containment: "document",
      helper: "clone",
      cursor: "move"
    });

    // Let the trash be droppable, accepting the gallery items
    $trash.droppable({
      accept: "#gallery > li",
      classes: {
        "ui-droppable-active": "ui-state-highlight"
      },
      drop: function( event, ui ) {
        Add_platform( ui.draggable );
      }
    });

    // Let the gallery be droppable as well, accepting items from the trash
    $gallery.droppable({
      accept: "#trash li",
      classes: {
        "ui-droppable-active": "custom-state-active"
      },
      drop: function( event, ui ) {
        recycleImage( ui.draggable );
      }
    });

    // Image deletion function
    var recycle_icon = "<a href='link/to/recycle/script/when/we/have/js/off' title='Recycle this image' class='ui-icon ui-icon-refresh'>Recycle image</a>";

    function Add_platform( $item ) {
      $item.fadeOut(function() {
        var $list = $( "ul", $trash ).length ?
        $( "ul", $trash ) :
        $( "<ul class='gallery ui-helper-reset'/>" ).appendTo( $trash );

        $item.find( "a.ui-icon-trash" ).remove();
        $item.append( recycle_icon ).appendTo( $list ).fadeIn(function() {
          $item.animate({ width: "165px" })
          platform_name = $item.attr('platform_name')
          $("input[name='platforms'][value='"+platform_name+"']").prop("checked", true);
        });
      });
    }

    // Image recycle function
    var trash_icon = "<a href='link/to/trash/script/when/we/have/js/off' title='Delete this image' class='ui-icon ui-icon-trash'>Delete image</a>";
    function recycleImage( $item ) {
      $item.fadeOut(function() {
        $item
          .find( "a.ui-icon-refresh" )
            .remove()
          .end()
          .css( "width", "165px")
          .find( "img" )
            .css( "height", "150px" )
          .end()
          .appendTo( $gallery )
          .fadeIn();
         platform_name = $item.attr('platform_name')
         $("input[name='platforms'][value='"+platform_name+"']").prop("checked", false);

      });
    }

    // Image preview function, demonstrating the ui.dialog used as a modal window

    // Resolve the icons behavior with event delegation
    $( "ul.gallery > li" ).on( "click", function( event ) {
      var $item = $( this ),
        $target = $( event.target );
      if ( $target.is( "a.ui-icon-trash" ) ) {
        Add_platform( $item );
      } else if ( $target.is( "a.ui-icon-refresh" ) ) {
        recycleImage( $item );
      }
      return false;
    });
} );


$("#id_platform").on("change", function() {

      platform= $(this).val();
      $.get('/count/get-profiles-available/'+platform )
       .done(function( data ) {
           $('#profiles-content').html(data)
       });
})

$(".cut-profile").on("click", function() {

      id_profile = $(this).attr('id_profile');
      $.get('/count/reactivate-profile/'+id_profile )
       .done(function( data ) {
           alert(data)
           location.reload();
       });
})

$(".table-list_count").on("click", ".change-password" , function(){
    count_id = $(this).attr('id_count')
    $.get('/count/change-password/'+count_id)
      .done(function( data ) {
            $('.modal-body').html(data)
            $('.modal-title').text("Respuesta de la solicitud")
            $('.modal-footer').hide()
            $("#myModal").modal({
                show: true,
                escapeClose: false,
                clickClose: false
                })
            $('.change-pass').click(function(e){
              e.preventDefault()
              json = convertFormToJSON($('.change-password-form'))
              $.post('/count/change-password/'+count_id, json)
                .done(function( data ) {
                  $('.modal-body').html(data)
              })
            })
            $("#myModal").on('hide.bs.modal', function (e) {
              location.reload();
            });
        });

})

function send_message(data){

    $('body').on("click", ".send-message" , function(){

        $.ajax({
            url: '/count/send-whatsapp-message',
            type: "POST",
            dataType: "json",
            data: JSON.stringify(data),
            contentType: "application/json",
            success: function (response) {
            console.log(response)
                alert(response)
                window.location.href = "/user/list-customer";
            }
        });
        $("#myModal").on('hide.bs.modal', function (e) {
          location.reload();
        });
    });
}

function cancel_sale(){

     $('body').on("click", ".calcel-sale" , function(){

         sale_id= $(this).attr('sale');
         $.get('/count/sale/cancel-sale/'+sale_id)
            .done(function( data ) {
            alert(data)
            location.reload();
         });
      });

     $(".renew").click(function(e){
        e.preventDefault()
        $(".sales").submit()

     })
     $(".update").click(function(e){
        e.preventDefault()
        $(".customer").submit()
     })
}



function send_message_individual(data){

    $.ajax({
        url: '/count/send-whatsapp-message',
        type: "POST",
        dataType: "json",
        data: JSON.stringify(data),
        contentType: "application/json",
        success: function (response) {
            alert(response)
        }
    });



}