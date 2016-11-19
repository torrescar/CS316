$(function(){
	$('#btnSearch').click(function(){
		
		$.ajax({
			url: '/showSearch',
			data: $('form').serialize(),
			type: 'GET',
			success: function(response){
				console.log(response);
			},
			error: function(error){
				console.log(error);
			}
		});
	});
});

$(function(){
	$('#btnRate').click(function(){
		
		$.ajax({
			url: '/showRate',
			data: $('form').serialize(),
			type: 'GET',
			success: function(response){
				console.log(response);
			},
			error: function(error){
				console.log(error);
			}
		});
	});
});