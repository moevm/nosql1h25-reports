$(document).ready(function () {
    const form = document.forms[0];

    form.addEventListener('submit', e => {
        e.preventDefault();

        document.body.style.cursor = 'wait';

        fetch(form.action, {
            method: form.method,
            body: new FormData(form),
        })
            .then(res => {
                document.body.style.cursor = 'default';
                if (res.ok) alert('Дамп успешно импортирован');
                else alert('Неправильный формат дампа');
            });
    });

    $('#dump').change(e => {
        form.dispatchEvent(new Event('submit'));

        e.target.value = '';
    });
});