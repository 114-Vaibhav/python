const stream = document.getElementById('stream');
const chartTempCanvas = document.getElementById('chartTemp');
const chartVibrationCanvas = document.getElementById('chartVibration');
const tempThresh = 100;
const VibThresh = 0.5;
let dataPoints = [];

const notyf = new Notyf({
    duration: 10000,
    position: { x: 'right', y: 'bottom' },
    dismissible: true,
    ripple: true,
    types: [
        {
            type: 'temp',
            background: 'linear-gradient(to right, #ff5f6d, #ffc371)',
            icon: false
        },
        {
            type: 'vib',
            background: 'linear-gradient(to right, #d88329, #a8e063)',
            icon: false
        }
    ]
});


function showAlert(type, message) {
    notyf.open({
        type: type,
        message: message
    });
}


const tempChart = new Chart(chartTempCanvas, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Temperature (°F)',
            data: [],
            borderColor: 'red',
            backgroundColor: 'rgba(255,0,0,0.2)',
            fill: true,
        }]
    },
    options: {
        animation: true,
        responsive: true,
        scales: {
            x: { title: { display: true, text: 'Time' } },
            y: { title: { display: true, text: 'Temp (°F)' } }
        }
    }
});


const vibrationChart = new Chart(chartVibrationCanvas, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Vibration',
            data: [],
            borderColor: 'blue',
            backgroundColor: 'rgba(0,0,255,0.2)',
            fill: true,
        }]
    },
    options: {
        animation: false,
        responsive: true,
        scales: {
            x: { title: { display: true, text: 'Time' } },
            y: { title: { display: true, text: 'Vibration' } }
        }
    }
});


const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = function (event) {
    const sensorData = JSON.parse(event.data);
    dataPoints.push(sensorData);

    if (dataPoints.length > 30) {
        dataPoints.shift();
    }
    console.log(sensorData);
    stream.innerHTML = `Temp: ${sensorData.temp} °F, Vibration: ${sensorData.vibration}, Time: ${sensorData.timestamp}`;
    if (sensorData.temp > tempThresh) {
        showAlert('temp', `Temperature exceeded 100°F (${sensorData.temp} °F)`);
    }
    if (sensorData.vibration > VibThresh)
        showAlert('vib', `Vibration exceeded 0.5 (${sensorData.vibration})`);

    tempChart.data.labels = dataPoints.map(d => d.timestamp);
    tempChart.data.datasets[0].data = dataPoints.map(d => d.temp);
    tempChart.update('none');

    vibrationChart.data.labels = dataPoints.map(d => d.timestamp);
    vibrationChart.data.datasets[0].data = dataPoints.map(d => d.vibration);
    vibrationChart.update('none');
};