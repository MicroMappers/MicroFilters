function generateUUID() {
    var d = new Date().getTime();
    var uuid = 'xxxxxxxxxxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x7|0x8)).toString(16);
    });
    return uuid;
};

function disableForm(state){
	$("form#main-form").find(":input:not(:hidden)").attr('disabled', state)
}

$(document).ready(function() {
	// getAppList();
	//post the form via ajax
	$("form#main-form").submit(function(event) {
		event.preventDefault();
		if ($("#app-list option:selected").attr("value") == 'none') {
			$("#message-box").html(''+
				'<div data-alert class="alert-box alert">'+
					 'You have to select an app type'+
				 	 '<a href="#" class="close">&times;</a>'+
		    '</div>'+
		    '');
			$(document).foundation('alert');
			return false;
		} else if (document.getElementById('data-file').value == '') {
			$("#message-box").html(''+
				'<div data-alert class="alert-box alert">'+
					 'Bad request: No file attached.'+
				 	 '<a href="#" class="close">&times;</a>'+
		    '</div>'+
			'');
			$(document).foundation('alert');
			return false;
		}

  		var formData = new FormData($(this)[0]);
  		disableForm(true);
        var uuid = generateUUID();
        //append the progress bar to the UI
        $('#message-box').html(''+
            '<div class="progress success">'+
                '<span class="meter" style="width: 0%"></span>'+
            '</div>');
        var progressBar = $('.meter');

        function updateProgressInfo() { 
			$.getJSON('/uploadProgress/'+uuid, function(data) { 
				console.log(data);
				progressBar.css({ width: parseInt(data['progress'])+'%' });
				progressBar.text(data['state']);
				if (data['state'] == 'Done')
					window.clearInterval(window.checkProgress);
			});
        }
        
        window.checkProgress = window.setInterval(updateProgressInfo, 1000);
		$.ajax({
			url: '/download/?X-Progress-ID='+uuid,
			type: 'POST',
			data: formData,
			async: true,
			cache: false,
			contentType: false,
			processData: false,
			statusCode: {
				400: function() {
						$("#message-box").html(''+
	  					'<div data-alert class="alert-box alert">'+
	 						 'Bad request: No file attached.'+
	  					 	 '<a href="#" class="close">&times;</a>'+
					    '</div>'+
					    '');
						$(document).foundation('alert');
				}
			},
			success: function(response) {
				$("#message-box").html(''+
					'<div data-alert class="alert-box success">'+
						 'File was processed successfully'+
					 	 '<a href="#" class="close">&times;</a>'+
				    '</div>'+
			    '');
			    $(document).foundation('alert');
	    		disableForm(false);
			}
		});
	});//end submit
});//end document ready

// function getAppList() {
	// $.getJSON( "/getAppList", function( data ) {
	// 	var app_list = [];
	// 	$.each( data, function( key, val ) {
	// 		app_list.push( "<li><input type='radio' name='app' value='"+val.appTypeName.replace(/ /g, "").toLocaleLowerCase()+"' appid='" + val.clientAppID + "'>" + val.appTypeName + "</input></li>" );
	// 		choices = JSON.parse(val.choices);
	// 		choice_list = [];
	// 		$.each(choices, function(key2, val2){
	// 			choice_list.push("<li><input value='"+val2.qa+"' id='"+key2+"' type='checkbox'><label for='"+key2+"'>"+val2.qa+"</label></li>")
	// 		});
	// 		$("#choice-list").append("<li class='app_choices' id='"+val.clientAppID+"_choices'><ul></ul></li>");
	// 		$("#"+val.clientAppID+"_choices").hide();
	// 		$("#"+val.clientAppID+"_choices").append(choice_list);
	// 	});
	// 	$("#app-list").append(app_list);

	// 	//populate app list
	//     $("#app-list input[name=app]").on("click", function() {
	// 		$("#choice-list .app_choices").hide();
	//       	if ($("#app-list input:checked").attr('appid'))
	//       		$("#"+$("#app-list input:checked").attr('appid')+"_choices").show();
	//     });
	// }).fail(function() {
	// 	$("#app-list").parent().append("<b>Could not fetch app list</b>");
	// });
// }