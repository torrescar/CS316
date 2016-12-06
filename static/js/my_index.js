$(function(){
	$('#btnSearch').click(function(){
		
		$.ajax({
			url: '/search2',
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
			url: '/rate',
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