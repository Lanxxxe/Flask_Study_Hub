let password = document.getElementById('password');
let checkbox = document.getElementById('see-password');

checkbox.addEventListener('change', function() {
    password.type = this.checked ? 'text' : 'password';
})