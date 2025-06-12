# weather-forecast ENGLISH
This is simply a program for obtaining data from [*Openweather.org*](https://openweathermap.org/) and [*wolfx.jp*](https://wolfx.jp/apidoc_en) json data. <br>
*Check out the preprocess.py in src dir*

To access only the preprocessed data from the json file for air_pollution, quake and typhoon. <br>
Author: D.J.Q.GOH (Daniel Jia Qin Goh)
- Run flask on http://localhost:5000
    ```bash
    message: "Flask server is running"
    ```
- Obtain the json data 
    ```bash 
    http://10.90.211.150:5000/api/air_pollution
    http://10.90.211.150:5000/api/quake
    http://10.90.211.150:5000/api/typhoon_predict
    ```

!!! / Important Notes:
When there are no typhoon present in the premesis, no data will be projected in ```typhoon_predict.json```.

Below is the mock parameter of the data for ```typhoon_predict.json
```json
[
  {
    "time": "2025-06-01 12:00:00",
    "wind_speed": 32.5,
    "wind_gust": 45.0,
    "pressure": 980,
    "temp": 27.3,
    "humidity": 88,
    "weather_main": "Rain",
    "weather_description": "heavy intensity rain",
    "rain_mm": 25.4
  },
  {
    "time": "2025-06-01 15:00:00",
    "wind_speed": 28.7,
    "wind_gust": 40.2,
    "pressure": 985,
    "temp": 26.1,
    "humidity": 90,
    "weather_main": "Clouds",
    "weather_description": "overcast clouds",
    "rain_mm": 10.0
  }
]
```

<br>

---

<br>

# weather-forecast 日本語版

これは [*Openweather.org*](https://openweathermap.org/) および [*wolfx.jp*](https://wolfx.jp/apidoc_en) のJSONデータからデータを取得するためのプログラムです。<br>
*srcディレクトリ内の preprocess.py をご確認ください*

大気汚染、地震、台風のプリプロセス済みデータのみをJSONファイルから取得できます。<br>
著者: D.J.Q.GOH (Daniel Jia Qin Goh)

- Flaskを http://localhost:5000 で実行
    ```bash
    message: "Flask server is running"
    ```
- JSONデータの取得
    ```bash 
    http://10.90.211.150:5000/api/air_pollution
    http://10.90.211.150:5000/api/quake
    http://10.90.211.150:5000/api/typhoon_predict
    ```

!!! / 重要な注意事項:
台風が存在しない場合、```typhoon_predict.json``` にはデータが表示されません。

以下は ```typhoon_predict.json``` のモックパラメータ例です。
```json
[
  {
    "time": "2025-06-01 12:00:00",
    "wind_speed": 32.5,
    "wind_gust": 45.0,
    "pressure": 980,
    "temp": 27.3,
    "humidity": 88,
    "weather_main": "Rain",
    "weather_description": "heavy intensity rain",
    "rain_mm": 25.4
  },
  {
    "time": "2025-06-01 15:00:00",
    "wind_speed": 28.7,
    "wind_gust": 40.2,
    "pressure": 985,
    "temp": 26.1,
    "humidity": 90,
    "weather_main": "Clouds",
    "weather_description": "overcast clouds",
    "rain_mm": 10.0
  }
]
```

--- 

Problem Encounter 
+ Workflow build up in Github Action 