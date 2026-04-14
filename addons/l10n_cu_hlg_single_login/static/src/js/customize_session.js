/*---------------------------------------------------------
 * OpenErp Session Expired
 *---------------------------------------------------------*/

$( document ).ready(function(){
	$(document).ajaxComplete(function( event, request, settings ) {
	  if(request.responseJSON && request.responseJSON.error && request.responseJSON.error.code === 100){
		setTimeout(function(){
			location.reload();
		}, 3000);

	  }
	});
}); 
