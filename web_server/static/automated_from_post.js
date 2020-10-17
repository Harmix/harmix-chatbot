function post(data) {

    // The rest of this code assumes you are not using a library.
    // It can be made less wordy if you use one.
    const form = document.createElement('form');
    const params = data.params;

    form.method = "post";
    form.action = data.path;

    params.forEach(function (arrayItem) {
        const hiddenField = document.createElement('input');
        hiddenField.type = 'hidden';

        hiddenField.name = arrayItem.name;
        hiddenField.value = arrayItem.value;

        form.appendChild(hiddenField);
    });

    document.body.appendChild(form);
    form.submit();
}