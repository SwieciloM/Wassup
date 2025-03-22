document.addEventListener('DOMContentLoaded', function() {
  // Select all forms with the class "leave-form"
  var leaveForms = document.querySelectorAll('.delete-form');
  
  leaveForms.forEach(function(form) {
    form.addEventListener('submit', function(e) {
      if (!confirm('Are you sure you want to delete this room? All chat history will be lost permanently...')) {
        // If the user clicks Cancel, prevent the form from submitting
        e.preventDefault();
      }
    });
  });
});
  