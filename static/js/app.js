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
	getAppList();
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
  		formData.append('appID', $(this).find("#app-list option:selected").attr("appid"));
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

function getAppList() {
	$.getJSON( "/getAppList", function( data ) {
		var app_list = [];
		$.each( data, function( key, val ) {
			if (val.clientAppName == 'TextClicker' || val.clientAppName == 'Text Clicker' || val.clientAppName == 'ImageClicker' || val.clientAppName == 'Image Clicker' || val.clientAppName == 'VideoClicker' || val.clientAppName == 'Video Clicker')
				var appTypeText = '';
			else
				var appTypeText = ' [' + val.appTypeName + ']';
			app_list.push( "<option value='"+val.appTypeName.replace(/ /g, "").toLocaleLowerCase()+"' appid='" + val.clientAppID + "'>" + val.clientAppName + appTypeText + "</option>" );
		});
		$("#app-list select").append(app_list);
	}).fail(function() {
		$("#app-list").parent().append("<b>Could not fetch app list</b>");
	});
}