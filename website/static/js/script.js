ymaps.ready(init);
let myMap;
let clickCoords;
var alertDiv = document.getElementById('alert-div');
var alertSpan = document.getElementById('alert-span');
function init() {
    myMap = new ymaps.Map("map", {
        center: [56.86125593217464,35.91491223044557], 
        zoom: 13,
        controls: ['geolocationControl']
    }, {
        // Зададим ограниченную область прямоугольником, 
        // примерно описывающим Санкт-Петербург.
        restrictMapArea: [
            [56.7106070575507,35.481058444937915],
            [57.00026552161211,36.30091318126605]
        ]
    });

    document.getElementById('addMarkerBtn').addEventListener('click', () => {
        myMap.events.add('click', onMapClick);
    });

    navigator.geolocation.getCurrentPosition(function (position) {
        var userCoords = [position.coords.latitude, position.coords.longitude];
        myMap.setCenter(userCoords, 12); // Центрирование карты на местоположении пользователя и установка масштаба

        // Создание круга вокруг текущего местоположения пользователя
        var userLocationCircle = new ymaps.Circle([
            userCoords, // Координаты центра круга
            5 // Радиус круга в метрах
        ], {
            balloonContent: "Вы здесь"
        }, {
            fillColor: "#1E90FF88", // Цвет заливки: синий с прозрачностью
            strokeColor: "#1E90FF", // Цвет границы: синий
            strokeOpacity: 0.8, // Прозрачность границы
            strokeWidth: 2 // Ширина границы
        });

        myMap.geoObjects.add(userLocationCircle);

    }, function (error) {
        console.error("Ошибка при получении местоположения: ", error);
    });

    updateMarkers();
    setInterval(updateMarkers, 60000); // Обновление каждые 60 секунд
    // Скрытие загрузочного экрана после загрузки карты
    document.getElementById('loading-screen').style.display = 'none';

    // Добавляем обработчики событий только один раз
    document.getElementById('confirmYes').addEventListener('click', onConfirmYes);
    document.getElementById('confirmNo').addEventListener('click', onConfirmNo);
}

function onMapClick(e) {
    clickCoords = e.get('coords');
    canAddMarker();
    myMap.events.remove('click', onMapClick);
}

function addMarker(lat, lon, comment) {
    fetch(`/add_marker/?lat=${lat}&lon=${lon}&comment=${encodeURIComponent(comment)}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateMarkers();
                document.getElementById('container').classList.remove('transparent');
                document.getElementById('container').style.backgroundColor = 'black';
            } else if (data.status === 'error') {
                alertDiv.style.display = 'flex';
                alertDiv.innerHTML = `<span id="alert-span" class="fs-5 fw-bold text-center py-2">${data.message}</span>` // Показываем сообщение об ошибке, если метку нельзя добавить
                function Hide() {
                    alertDiv.style.display = 'none';
                }
                setTimeout(Hide, 5000);
            }
        })
        .catch(error => {
            console.error('Ошибка при добавлении метки:', error);
        });
}
function canAddMarker() {
    fetch('/can_add_marker/')
    .then(response => response.json())
    .then(data =>{
        if(data.status === 'error') {
            alertDiv.style.display = 'flex';
            alertDiv.innerHTML = `<span id="alert-span" class="fs-5 fw-bold text-center py-2">${data.message}</span>`
            function Hide() {
                alertDiv.style.display = 'none';
            }
            setTimeout(Hide, 5000);
            document.getElementById('container').classList.remove('transparent');
            document.getElementById('container').style.backgroundColor = 'black'
        }
        if(data.status === 'success') {
            showConfirmationModal();
        }
    })
}

function showConfirmationModal() {
    const modal = document.getElementById('confirmationModal');
    modal.style.display = 'block';
}

function onConfirmYes() {
    const modal = document.getElementById('confirmationModal');
    modal.style.display = 'none';
    const comment = document.getElementById('markerComment').value;
    addMarker(clickCoords[0], clickCoords[1], comment);
}

function onConfirmNo() {
    const modal = document.getElementById('confirmationModal');
    modal.style.display = 'none';
    document.getElementById('container').classList.remove('transparent');
    document.getElementById('container').style.backgroundColor = 'black';
}

function shareOnTelegram() {
    // URL мини-приложения, которое вы хотите поделиться
    const appUrl = "https://t.me/DpsNet_bot/DPS_NET";

    // Текст сообщения, которое будет отправлено
    const message = encodeURIComponent("Посмотри это мини-приложение: ");

    // Ссылка для открытия Telegram
    const telegramUrl = `https://t.me/share/url?url=${appUrl}&text=${message}`;

    // Открываем ссылку в новой вкладке
    window.open(telegramUrl, "_blank");
}

function updateMarkers() {
    fetch('/get_markers/')
        .then(response => response.json())
        .then(data => {
            myMap.geoObjects.removeAll(); // Удаляем все существующие метки

            var svgIcon = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path fill="#ff0000" d="M280 24c0-13.3-10.7-24-24-24s-24 10.7-24 24l0 80c0 13.3 10.7 24 24 24s24-10.7 24-24l0-80zM185.8 224l140.3 0c6.8 0 12.8 4.3 15.1 10.6L360.3 288l-208.6 0 19.1-53.4c2.3-6.4 8.3-10.6 15.1-10.6zm-75.3-10.9L82.2 292.4C62.1 300.9 48 320.8 48 344l0 40 0 64 0 32c0 17.7 14.3 32 32 32l16 0c17.7 0 32-14.3 32-32l0-32 256 0 0 32c0 17.7 14.3 32 32 32l16 0c17.7 0 32-14.3 32-32l0-32 0-64 0-40c0-23.2-14.1-43.1-34.2-51.6l-28.3-79.3C390.1 181.3 360 160 326.2 160l-140.3 0c-33.8 0-64 21.3-75.3 53.1zM128 344a24 24 0 1 1 0 48 24 24 0 1 1 0-48zm232 24a24 24 0 1 1 48 0 24 24 0 1 1 -48 0zM39 39c-9.4 9.4-9.4 24.6 0 33.9l48 48c9.4 9.4 24.6 9.4 33.9 0s9.4-24.6 0-33.9L73 39c-9.4-9.4-24.6-9.4-33.9 0zm400 0L391 87c-9.4 9.4-9.4 24.6 0 33.9s24.6 9.4 33.9 0l48-48c9.4-9.4 9.4-24.6 0-33.9s-24.6-9.4-33.9 0z"/></svg>`;

            data.markers.forEach(marker => {
                const placemark = new ymaps.Placemark([marker.lat, marker.lon], {}, {
                    iconLayout: 'default#imageWithContent',
                    iconImageHref: 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgIcon),
                    iconImageSize: [32, 32],
                    iconImageOffset: [-16, -16]
                });

                placemark.events.add('click', function () {
                    showMarkerModal(marker.id, marker.lat, marker.lon, marker.created_at, marker.username, marker.comment);
                });

                myMap.geoObjects.add(placemark);
            });

            document.getElementById('dps-quant').textContent = data.active_markers_count; // Обновляем количество активных меток
        });
}

function showMarkerModal(id, lat, lon, createdAt, username, comment) {
    // Преобразуем ISO дату в объект Date
    const date = new Date(createdAt);
    // Форматируем время в формат "часы:минуты"
    const formattedTime = date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });

    document.getElementById('markerCreatedAt').textContent = formattedTime; // Устанавливаем отформатированное время
    document.getElementById('markerUsername').textContent = username; // Устанавливаем имя пользователя
    document.getElementById('markerCommentDisplay').textContent = comment || 'Нет комментариев'; // Показать комментарий
    document.getElementById('extendMarkerBtn').onclick = () => extendMarker(id);
    document.getElementById('deleteMarkerBtn').onclick = () => deleteMarker(id);
    const markerModal = new bootstrap.Modal(document.getElementById('markerModal'));
    markerModal.show();
}
function extendMarker(id) {
    fetch(`/extend_marker/${id}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrf-token]').content
        }
    })
    .then(() => {
        updateMarkers();
        // Получаем экземпляр модального окна и закрываем его
        const markerModal = bootstrap.Modal.getInstance(document.getElementById('markerModal'));
        markerModal.hide();
    });
}

function deleteMarker(id) {
    fetch(`/delete_marker/${id}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrf-token]').content
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            if (data.deleted) {
                updateMarkers();
            } 
            else{
                if (data.message){
                    alertDiv.style.display = 'flex';
                    alertDiv.innerHTML = `<span id="alert-span" class="fs-5 fw-bold text-center py-2">${data.message}</span>` // Показываем сообщение об ошибке, если метку нельзя добавить
                    function Hide() {
                        alertDiv.style.display = 'none';
                    }
                    setTimeout(Hide, 5000);
                }
                    
            }
            
        }
        const markerModal = bootstrap.Modal.getInstance(document.getElementById('markerModal'));
        markerModal.hide();
    });
}

function getProfile() {
    fetch('/profile/')
    .then(response => response.json())
    .then(data =>{
        console.log(data);
        if(data.status === 'success') {
            var username = document.getElementById('user-username');
            var active_markers_count = document.getElementById('active-markers');
            console.log(data.username);
            username.innerHTML = `<span class="fs-4" style="color: black;">${data.first_name} ${data.last_name}</span>`
            active_markers_count.innerHTML = `<span class="fs-4 ms-1"  style="color: white;">Активных меток: ${data.active_markers_count}</span><i class="fa-solid fa-map-pin fa-2x ms-2" style="color: #c80e0e;"></i>`
        }
    })
}