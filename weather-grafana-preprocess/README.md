# Weather Grafana Preprocess

This project is designed to fetch weather data from a JSON API, process it to extract specific areas and temperature data, and save the result to a JSON file. The project utilizes Docker to containerize the application and includes a cron job to schedule the execution of the data processing script every hour.

## Project Structure

```
weather-grafana-preprocess
├── src
│   └── preprocess.py        # Python script for fetching and processing weather data
├── docker-compose.yml       # Docker Compose configuration for the application
├── Dockerfile               # Dockerfile for building the application image
├── cronjob                  # Cron job configuration for scheduling the script
└── README.md                # Documentation for the project
```

## Setup Instructions

1. **Clone the Repository**
   Clone this repository to your local machine.

   ```bash
   git clone <repository-url>
   cd weather-grafana-preprocess
   ```

2. **Build the Docker Image**
   Use the following command to build the Docker image defined in the `Dockerfile`.

   ```bash
   docker-compose build
   ```

3. **Run the Application**
   Start the application using Docker Compose. This will also start the cron job that executes the script every hour.

   ```bash
   docker-compose up
   ```

## Usage

The `preprocess.py` script will automatically fetch the weather data and save the processed results to `nagasaki_temps.json` every hour. You can check the output file in the designated volume or directory specified in the Docker configuration.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.