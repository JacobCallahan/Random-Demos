$(document).ready(function () {
 
  $(".formSlider").change(function() {
     if (this.value == 31) {     
      $(".registerButton").hide();  $(".formSubmit").removeAttr("disabled");
       $(this).slideUp();
       $("#sliderLabel").slideUp();
     } else if (this.value == 1) {
       $(".signinButton").hide(); $(".formSubmit").removeAttr("disabled");
       $(this).slideUp();
       $("#sliderLabel").slideUp();
      $(".registerItem").attr('required', '');
      $(".registerItem").removeClass("registerItem");
     } else {    
       $("#sliderLabel").text('<---- Keep going ---->');
     }
  });  
  $("input").blur(function() {
    if (this.value == "") {
    	$(this).addClass('error');
    } else {
    	$(this).removeClass('error');
    }
  });
  $('#pass2').blur(function() {
    if (this.value != $('#pass1').val()) {
      $(this).addClass('error');
    } else {
    	$(this).removeClass('error');
    }
  });
});