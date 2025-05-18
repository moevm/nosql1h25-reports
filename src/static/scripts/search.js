$(document).ready(function () {
    const form = document.forms[0];
    const page = document.getElementById('page');

    function addWord(word, div) {
        $('<span />').addClass('container-word').text(word).click(e => e.target.remove()).appendTo(div);
    }

    $('input[type="hidden"]').each(function () {
        for (let chapter of $(this).val().split(' ')) {
            if (chapter.trim() !== '') addWord(chapter, $(this).siblings('.words-container'));
        }
    });

    form.addEventListener("submit", e => {
        e.preventDefault();

        $('.words-container').each(function () {
            const wordList = $(this).children().map(function () {
                return $(this).text();
            });
            $(this).siblings('input[type="hidden"]').val(wordList.get().join(' '));
        });

        const formData = new FormData(form);
        const params = new URLSearchParams();

        for (const [key, value] of formData.entries()) {
            if (value.trim() !== '') {
                params.append(key, value);
            }
        }

        if (params.toString() !== '') window.location.href = form.action + '?' + params.toString();
        else window.location.href = form.action;
    });
    form.addEventListener("reset", () => $('.words-container').children().replaceWith());
    $("#sort").change(() => form.dispatchEvent(new Event('submit')));
    $("#page").change(() => {
        const params = new URLSearchParams(window.location.search);
        params.set('page', page.value);
        window.location.href = form.action + '?' + params.toString();
    });

    $(".filter-box__add-word").click(function () {
        const input = $(this).siblings('input');
        const value = input.val();
        if (value.trim() !== '') {
            addWord(value, $(this).parent().siblings('.words-container'));
        }
        input.val('');
    });
});