

 $(document).ready(function () {
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
		autoclose: true
	});
	//autosize for textarea
	autosize($('textarea'));
 });