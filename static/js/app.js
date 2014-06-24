$(document).ready(
	function(){
		$.getJSON( "/getAppList", function( data ) {
		  var app_list = [];
		  $.each( data, function( key, val ) {
		    app_list.push( "<option value='"+val.appTypeName.replace(/ /g, "").toLocaleLowerCase()+"' appid='" + val.clientAppID + "'>" + val.appTypeName + "</option>" );
		   	choices = JSON.parse(val.choices);
		   	choice_list = [];
		   	$.each(choices, function(key2, val2){
		   		choice_list.push("<input value='"+val2.qa+"' id='"+key2+"' type='checkbox'><label for='"+key2+"'>"+val2.qa+"</label><br>")
		   	});
		   	$("#choice-list").append("<div class='app_choices' id='"+val.clientAppID+"_choices'></div>");
		   	$("#"+val.clientAppID+"_choices").hide();
		   	$("#"+val.clientAppID+"_choices").append(choice_list);
		  });
		  $("#app-list").append(app_list);
		}).fail(function() {
    		$("#app-list").parent().append("<b>Could not fetch app list</b>");
  		});

  		$("#app-list").change(function(){
  			$("#choice-list .app_choices").hide();
  			if ($("#app-list option:selected").attr('appid')){
  				$("#"+$("#app-list option:selected").attr('appid')+"_choices").show();
  			}
  		});
	}
	);