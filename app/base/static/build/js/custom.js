// Money Format
 const money = new Intl.NumberFormat('en-US', {
	style: 'currency',
	currency: 'USD',
	minimumFractionDigits: 2
  })

  //Today date
  $( document ).ready(function() {
    $('.set-today').val(new Date().toISOString().split('T')[0]) 
});

//tooltip
$(function () {
     //Jquary validation form
	$.validate({
		lang: 'es',
		validateOnBlur : true,
		errorMessagePosition : 'top' 
  });
  	//bootstrap select 
	$('.select').selectpicker();
	//bootstrao date picker
	$('.mydatepicker').datepicker({
		format: "yyyy/mm/dd",
		autoclose: true,
        orientation: 'auto top'
    })

	//autosize for textarea
	autosize($('textarea'));

	//Tooltip
	$('[data-toggle="tooltip"]').tooltip({
		container: 'body'
	});

	//Popover
  $('[data-toggle="popover"]').popover();
  
})


