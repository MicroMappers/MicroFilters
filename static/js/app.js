$(document).ready(
	function(){
		$.getJSON( "/getAppList", function( data ) {
		  var items = [];
		  $.each( data, function( key, val ) {
		    items.push( "<option id='" + val.clientAppID + "'>" + val.appTypeName + "</option>" );
		    console.log(val);

		  });
		  $("#app-list").append(items);
		}).fail(function() {
    		$("#app-list").parent().append("<b>Could not fetch app list</b>");
  		});
	}
	);