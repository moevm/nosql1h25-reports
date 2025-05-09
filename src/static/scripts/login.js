$(document).ready(function () {
    const form = document.forms[0];

    form.addEventListener('submit', e => {
        e.preventDefault();

        fetch(form.action, {
            method: form.method,
            body: new FormData(form),
        })
            .then(res => {
                if (res.redirected) window.location = res.url;
                else alert('Неправильный пароль администратора');
            });
    });
});