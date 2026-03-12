// Mostrar/ocultar contraseña
document.getElementById('togglePassword').addEventListener('click', function(){
    const password = document.getElementById('password');
    const showPassword = password.type === 'text';
    password.type = showPassword ? 'password' : 'text';
    this.textContent = showPassword ? 'Mostrar' : 'Ocultar';
    this.setAttribute('aria-pressed', String(!showPassword))
});

// Validacion de formulario
document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault(); // evitar recarga para demo; quita para enviar por formulario clásico
    const errorEl = document.getElementById('error');
    errorEl.style.display = 'none';
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;

    if (!username || !password) {
        errorEl.textContent = 'Por favor, completa todos los campos.';
        errorEl.style.display = 'block';
        return;
    }

    // autenticacion

    try {
        const response = await fetch('http://127.0.0.1:5000/loginJs', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            credentials: 'include',
            body: JSON.stringify({username, password})
        });
        console.log('fetch status', response.status);
        const text = await response.text();
        console.log('fetch body row login:', text);
        let data;
        try{ data = JSON.parse(text); } catch{ data = null; }
        if (!response.ok) {
            errorEl.textContent = (data && data.message) || 'Error en el servidor.';
            errorEl.style.display = '';
            return; 
        }
        // éxito: redirigir a la app
        if (data && data.success){
            if (data.role === 'student'){
                const redirectTo = (data.redirect || 'http://127.0.0.1:5000/appStudent');
                window.location.href = redirectTo; 
            } else if (data.role === 'teacher'){
                const redirectTo = (data.redirect || 'http://127.0.0.1:5000/appTeacher');
                window.location.href = redirectTo;
            } else if (data.role === 'administrator'){
                const redirectTo = (data.redirect || 'http://127.0.0.1:5000/appAdministrator');
                window.location.href = redirectTo;
            }
            
        }
        
    } catch (error) {
        errorEl.textContent = 'Error de red. Intentalo nuevamente.';
        errorEl.style.display = 'block';
        console.error('Error de red:', error);
    }
});