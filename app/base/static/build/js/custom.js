

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
		autoclose: true,
		 orientation: 'auto top'
	});
	//autosize for textarea
	autosize($('textarea'));
 });