$(document).ready(function () {

    $('header a, .indicator a').on("click", function (e) {
        e.preventDefault();
    });

    $('.button_upload').on("click" , function () {
        $('.box-file').click();
    });

    $('input[type="file"]').change(function (e) {

        let lang = document.documentElement.lang;

        if (e.target.files.length === 0) {
		    if (lang == "uk") {
		        alert('🛑 Помилка: Файл не вибрано. Спробуй ще раз');
            } else if (lang == "ru") {
		        alert('🛑 Ошибка: Файл не выбран. Попробуй еще раз');
            } else {
		        alert('🛑 Error: No file selected. Try again');
            }
		    return;
	    }

        let file = e.target.files[0];
        if(file.size > 500*1024*1024) {
            if (lang == "uk") {
		        alert('🛑 Помилка: Файл більше 500 MB. Спробуй завантажити файл менше 500 MB');
            } else if (lang == "ru") {
		        alert('🛑 Ошибка: Файл больше 500 MB. Попробуй загрузить файл меньше 500 MB');
            } else {
		        alert('🛑 Error: Exceeded size 500 MB. Try uploading a file less than 500 MB in size');
            }
            return;
        }

        let fileName = file.name;
        let extension = fileName.slice((fileName.lastIndexOf(".") - 1 >>> 0) + 2).toLowerCase();
        const allowedExtensions = ['mp4', 'avi', 'webm', 'mkv', 'flv', 'mov', 'wmv', 'm4v', '3gp', 'ogv', 'ogg', 'vob'];

        if (!allowedExtensions.includes(extension)) {
            if (lang == "uk") {
		        alert('🛑 Помилка: Файл "' + fileName + '" в непідтримуваному форматі. Будь ласка, вибери ' +
                'підтримуване розширення:\n' + allowedExtensions);
            } else if (lang == "ru") {
		        alert('🛑 Ошибка: Файл "' + fileName + '" в неподдерживаемом формате. Пожалуйста, выбери ' +
                'поддерживаемое расширение:\n' + allowedExtensions);
            } else {
		        alert('🛑 Error: The file "' + fileName + '" does not an allowed extension. Please select a correct ' +
                'extension:\n' + allowedExtensions);
            }
        }
        else {
            let confirm_text_message = '🧐 Are you sure that you want to upload "' + fileName + '" file?';
            if (lang == "uk") {
		        confirm_text_message = '🧐 Ти впевнений, що хочеш завантажити файл "' + fileName + '"?';
            } else if (lang == "ru") {
		        confirm_text_message = '🧐 Ты уверен, что хочешь загрузить файл "' + fileName + '"?';
            }
            if (confirm(confirm_text_message)){
              $('.lds-roller').show();
              $('.submit_button').click();
            }
        }

    });

});