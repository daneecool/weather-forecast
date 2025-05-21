<?php
header('Content-Type: application/json; charset=UTF-8');

$url = 'https://www.jma.go.jp/bosai/forecast/data/forecast/420000.json';

$json = file_get_contents($url);
if (!$json) {
    echo json_encode(['error' => '気象データの取得に失敗しました']);
    exit;
}

$data = json_decode($json, true);
if (!$data) {
    echo json_encode(['error' => 'JSONの解析に失敗しました']);
    exit;
}

$forecast = $data[0];
$timeSeries = $forecast['timeSeries'];

$weatherTimeDefines = $timeSeries[0]['timeDefines'];
$areasWeather = $timeSeries[0]['areas'][0];
$weathers = $areasWeather['weathers'];

$popTimeDefines = $timeSeries[1]['timeDefines'];
$areasPop = $timeSeries[1]['areas'][0];
$pops = $areasPop['pops'];

// Get and sort Nagasaki temps, then pick min and max
$minTemp = '-';
$maxTemp = '-';
foreach ($timeSeries[2]['areas'] as $area) {
    if (isset($area['area']['name']) && $area['area']['name'] === '長崎') {
        // Filter out empty values and convert to integers
        $temps = array_filter($area['temps'], fn($v) => $v !== '');
        $temps = array_map('intval', $temps);
        if (count($temps) > 0) {
            sort($temps);
            $minTemp = $temps[0];
            $maxTemp = $temps[count($temps) - 1];
        }
        break;
    }
}

date_default_timezone_set('Asia/Tokyo');
$now = new DateTime('now');

function get6HourIndex(DateTime $dt, array $weatherTimeDefines) {
    $hour = (int)$dt->format('H');
    if ($hour < 6) {
        $targetHour = 0;
    } elseif ($hour < 12) {
        $targetHour = 6;
    } elseif ($hour < 18) {
        $targetHour = 12;
    } else {
        $targetHour = 18;
    }
    $targetDateStr = $dt->format('Y-m-d') . sprintf('T%02d:00:00+09:00', $targetHour);
    foreach ($weatherTimeDefines as $index => $wtStr) {
        if ($wtStr === $targetDateStr) {
            return $index;
        }
    }
    return 0;
}

$indexesToShow = [];
foreach ($popTimeDefines as $i => $timeStr) {
    $dt = new DateTime($timeStr);
    if ($dt >= $now) {
        $indexesToShow[] = $i;
    }
}
if (count($indexesToShow) === 0) {
    $total = count($popTimeDefines);
    $start = max(0, $total - 10);
    $indexesToShow = range($start, $total - 1);
} else {
    $indexesToShow = array_slice($indexesToShow, 0, 10);
}

function getWeatherIcon($weather) {
    $map = [
        '晴れ' => '☀️',
        'くもり' => '☁️',
        '雨' => '🌧️',
        '雪' => '❄️',
        '雷' => '⚡',
        '霧' => '🌫️',
        '霰' => '🌨️',
    ];
    foreach ($map as $key => $icon) {
        if (mb_strpos($weather, $key) !== false) {
            return $icon;
        }
    }
    return '❓';
}

$result = [
    'maxTemp' => $maxTemp,
    'minTemp' => $minTemp,
    'forecasts' => [],
    'updated' => date('Y.m.d H:i:s'),
];

foreach ($indexesToShow as $i) {
    $dt = new DateTime($popTimeDefines[$i]);
    $timeStr = $dt->format('H:i');
    $pop = $pops[$i] ?? '-';
    $weatherIndex = get6HourIndex($dt, $weatherTimeDefines);
    $weather = isset($weathers[$weatherIndex]) ? $weathers[$weatherIndex] : '-';
    $icon = getWeatherIcon($weather);

    $result['forecasts'][] = [
        'time' => $timeStr,
        'weather' => $weather,
        'icon' => $icon,
        'pop' => $pop,
    ];
}

echo json_encode($result, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
