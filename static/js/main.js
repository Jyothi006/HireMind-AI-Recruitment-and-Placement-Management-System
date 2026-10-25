// HireMind Main JavaScript Helper
document.addEventListener('DOMContentLoaded', function() {
  // Auto dismiss bootstrap alerts after 5 seconds
  setTimeout(function() {
    let alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
      let bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    });
  }, 6000);
});
