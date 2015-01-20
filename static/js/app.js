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
	$("#app-list input[name=app]").click(function() {
		$(".app-selector").hide();
		$("#" + $(this).val()).show();
	});

	//post the form via ajax
	$("form#main-form").submit(function(event) {
		event.preventDefault();
		if ($("#app-list input[name=app]:checked").attr("value") == undefined) {
			$("#message-box").html(''+
				'<div data-alert class="alert-box alert">'+
					 'You have to select an app type'+
				 	 '<a href="#" class="close">&times;</a>'+
		    '</div>'+
		    '');
			$(document).foundation('alert');
			return false;
		} else if (document.getElementById('data-file').value == '' && document.getElementById('data-url').value == '') {
			$("#message-box").html(''+
				'<div data-alert class="alert-box alert">'+
					 'Bad request: No file attached.'+
				 	 '<a href="#" class="close">&times;</a>'+
		    '</div>'+
			'');
			$(document).foundation('alert');
			return false;
		} else if (document.getElementById('data-file').value != '' && document.getElementById('data-url').value != ''){
			$("#message-box").html(''+
				'<div data-alert class="alert-box alert">'+
					 'Bad request: You can only submit one data source.'+
				 	 '<a href="#" class="close">&times;</a>'+
		    '</div>'+
			'');
			$(document).foundation('alert');
			return false;
		}

  		var formData = new FormData($(this)[0]);
  		formData.append('appID', $('select[name=' + $("#app-list input[name=app]:checked").val() + '-app] option:selected').val());
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
				if (window.progressLevel < parseInt(data['progress']))
					window.progressLevel = parseInt(data['progress']);
				progressBar.css({ width: window.progressLevel+'%' });
				progressBar.text(data['state']);
				if (data['state'] == 'Done') {
					window.clearInterval(window.checkProgress);
		    		disableForm(false);	
				}
			});
        }

        window.progressLevel = 0;
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
				400: function(xhr) {
					if(xhr.responseText){ 
						errorText = xhr.responseText; 
					} else { 
						errorText = 'Bad request: No file attached or no data in file.'; 
					}
					$("#message-box").html(''+
	  					'<div data-alert class="alert-box alert">'+
	 						 errorText+
	  					 	 '<a href="#" class="close">&times;</a>'+
					    '</div>'+
				    '');
					$(document).foundation('alert');
					disableForm(false);
				},
				303: function(response) {
					$("#message-box").html(''+
						'<div data-alert class="alert-box warning">'+
								'File is being processed. This may take some time, please check ' +
								'<a href="' + response.responseText + '">here</a> for progress.' +
						 		'<a href="#" class="close">&times;</a>'+
					    '</div>'+
				    '');
				    $(document).foundation('warn');
		    		disableForm(false);
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
		var text_list = [];
		var image_list = [];
		var video_list = [];
		$.each( data, function( key, val ) {
			if (val.appTypeName == 'TextClicker' || val.appTypeName == 'Text Clicker')
				text_list.push( "<option value='" + val.clientAppID + "'>" + val.clientAppName + "</option>" );
			else if (val.appTypeName == 'ImageClicker' || val.appTypeName == 'Image Clicker')
				image_list.push( "<option value='" + val.clientAppID + "'>" + val.clientAppName + "</option>" );
			else if (val.appTypeName == 'VideoClicker' || val.appTypeName == 'Video Clicker')
				video_list.push( "<option value='" + val.clientAppID + "'>" + val.clientAppName + "</option>" );
		});
		$("#textclicker select").append(text_list);
		$("#imageclicker select").append(image_list);
		$("#videoclicker select").append(video_list);
	}).fail(function() {
		$("#app-list").parent().append("<b>Could not fetch app list</b>");
	});
}