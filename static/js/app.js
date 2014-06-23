$(document).ready(
	function(){
		$.getJSON( "/getAppList", function( data ) {
		  var items = [];
		  $.each( data, function( key, val ) {
		    items.push( "<option id='" + val.clientAppID + "'>" + val.appTypeName + "</option>" );
		    console.log(val);

		  });
		  $("#app-list").append(items);
		});
	}
	);