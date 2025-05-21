<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>NagasakiWeather</title>
<style>
  body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #121212;
    color: #e0e0e0;
    margin: 2rem auto;
    padding: 1rem;
    border-radius: 8px;
  }

.current-date {
  text-align: center;
  margin-bottom: 1rem;
  font-size: 4rem;
  font-weight: bold;
  color: #90caf9;
}

.current-time {
  text-align: center;
  margin-bottom: 1rem;
  font-size: 6rem;
  font-weight: bold;
  color: white;
}
  h1 {
    text-align: center;
    margin-bottom: 1rem;
    color: #90caf9;
  }
  .forecast {
    display: flex;
    justify-content: space-between;
    padding: 1rem;
    background: #1e1e1e;
    border-radius: 6px;
    box-shadow: 0 0 10px #0d47a1;
    margin-bottom: 1rem;
  }
  .forecast div {
    flex: 1;
    text-align: center;
  }
  .icon {
    font-size: 3rem;
    margin-bottom: 0.5rem;
  }
  .desc {
    font-weight: 600;
    margin-bottom: 0.25rem;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    background-color: #121212;
    color: #eee;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  }

  th, td {
    padding: 12px 15px;
    border: 1px solid #333;
    text-align: center;
    white-space: nowrap;
  }

  th {
    background-color: #1f1f1f;
    font-weight: 600;
  }

  .pop {
    font-size: 3rem;
    color: #64b5f6;
    font-weight: bold;
    white-space: nowrap;
  }

  .time {
    font-size: 2rem;
  }

</style>
</head>
<body>

<div class="current-date" id="currentDate"></div>
<div class="current-time" id="currentTime"></div>
<h1>location：Nagasaki</h1>
<div class="temp-box" style="text-align: center; margin-top: 1rem;">
  <div style="font-size: 2rem; color: #ff5555;">
    ↑ MaxTemp: <span id="tempMax">-</span>℃
  </div>
  <div style="font-size: 2rem; color: #3399ff;margin-bottom:20px;">
    ↓ MinTemp: <span id="tempMin">-</span>℃
  </div>
</div>
<div style="text-align: center; margin: 2rem 0;">
  <iframe
    width="650"
    height="450"
    src="https://embed.windy.com/embed2.html?lat=32.7503&lon=129.8777&detailLat=32.7503&detailLon=129.8777&width=650&height=450&zoom=10&level=surface&overlay=rain&product=ecmwf&menu=&message=&marker=&calendar=now&pressure=&type=map&location=coordinates&detail=&metricWind=default&metricTemp=default&radarRange=-1"
    frameborder="0"
    style="border-radius: 8px; max-width: 100%;"
    allowfullscreen
  ></iframe>
</div>
<table>
<thead>
<tr>
    <th>Time</th>
    <th>Weather</th>
    <th>Precipitation probability</th>
</tr>
</thead>
<tbody id="forecastBody">
</tbody>
</table>
<div id="updated" style="font-size:0.8rem; color:#888; text-align:right; margin-top:0.5rem;"></div>

<script>
function updateCurrentTime() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const seconds = String(now.getSeconds()).padStart(2, '0');

  const formatteddate = `${year}.${month}.${day}`;
  const formattedtime = `${hours}:${minutes}:${seconds}`;

  document.getElementById('currentDate').textContent = formatteddate;
  document.getElementById('currentTime').textContent = formattedtime;
}

async function fetchWeather() {
  try {
    const res = await fetch('weather.php');
    const data = await res.json();

    if(data.error) {
      alert(data.error);
      return;
    }

    document.getElementById('tempMax').textContent = data.maxTemp;
    document.getElementById('tempMin').textContent = data.minTemp;

    const tbody = document.getElementById('forecastBody');
    tbody.innerHTML = '';

    data.forecasts.forEach(item => {
      const tr = document.createElement('tr');

      const tdTime = document.createElement('td');
      tdTime.textContent = item.time;
      tdTime.classList.add('time');

      const tdIcon = document.createElement('td');
      tdIcon.textContent = item.icon;
      tdIcon.classList.add('icon');

      const tdPop = document.createElement('td');
      tdPop.textContent = item.pop + '%';
      tdPop.classList.add('pop');

      tr.appendChild(tdTime);
      tr.appendChild(tdIcon);
      tr.appendChild(tdPop);

      tbody.appendChild(tr);
    });

    document.getElementById('updated').textContent = `Updated：${data.updated}`;

  } catch (e) {
    console.error(e);
    alert('気象情報の取得に失敗しました');
  }
}

updateCurrentTime();
fetchWeather();

setInterval(updateCurrentTime, 1000);
setInterval(fetchWeather, 5 * 60 * 1000);
</script>

</body>
</html>