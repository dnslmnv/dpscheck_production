ymaps.ready(init);
let myMap;
let clickCoords;

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
    showConfirmationModal();
    myMap.events.remove('click', onMapClick);
}

function addMarker(lat, lon, comment) {
    fetch(`/add_marker/?lat=${lat}&lon=${lon}&comment=${encodeURIComponent(comment)}`)
        .then(() => {
            updateMarkers();
            document.getElementById('container').classList.remove('transparent');
            document.getElementById('container').style.backgroundColor = 'black';
        });
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

function showMarkerModal(id, lat, lon, createdAt, username,comment) {
    document.getElementById('markerLat').textContent = lat;
    document.getElementById('markerLon').textContent = lon;
    document.getElementById('markerCreatedAt').textContent = createdAt;
    document.getElementById('markerUsername').textContent = username; // Set the username
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
        });
}

function deleteMarker(id) {
    fetch(`/delete_marker/${id}/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrf-token]').content
        }
    })
        .then(() => {
            updateMarkers();
        });
}