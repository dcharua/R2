// Money Format
 const money = new Intl.NumberFormat('en-US', {
	style: 'currency',
	currency: 'USD',
	minimumFractionDigits: 2
  })

  //Today date
  $( document ).ready(function() {
     let today = new Date();
     var date = today.toJSON().slice(0, 10); 
     var nDate = date.slice(0, 4) + '/'  
                       + date.slice(5, 7) + '/'  
                       + date.slice(8, 10);

   // $('.set-today').val(nDate) 
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


