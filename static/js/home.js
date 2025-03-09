document.addEventListener('DOMContentLoaded', function() {
    // Select all forms with the class "leave-form"
    var leaveForms = document.querySelectorAll('.leave-form');
    
    leaveForms.forEach(function(form) {
      form.addEventListener('submit', function(e) {
        if (!confirm('Are you sure you want to leave this room?')) {
          // If the user clicks Cancel, prevent the form from submitting
          e.preventDefault();
        }
      });
    });
  });
  