# UptimeRobot Monitor Dashboard

A beautiful web dashboard to monitor your UptimeRobot monitors with real-time status updates and performance metrics.

## Features

- 🟢 Green-themed modern UI
- 📊 Real-time monitor status
- 📈 24-hour and 7-day uptime statistics
- 🔄 Auto-refresh every 60 seconds
- 🐳 Docker Compose support
- 📱 Responsive design

## Quick Start

### Using Docker Compose

1. Make sure Docker and Docker Compose are installed
2. Run the following command:
```bash
docker-compose up -d
```

3. Open your browser and navigate to `http://localhost:8090`

### Using Docker

1. Build the image:
```bash
docker build -t uptimerobot-panel .
```

2. Run the container:
```bash
docker run -d -p 8090:8090 -e UPTIMEROBOT_API_KEY=ur2774746-bf6e7863549xxxxxxxxx uptimerobot-panel
```

### Manual Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to `http://localhost:8090`

## Configuration

To change the API key or port, edit the `docker-compose.yml` file or set environment variables:

- `UPTIMEROBOT_API_KEY`: Your UptimeRobot API key

## API Endpoints

- `GET /`: Main dashboard page
- `GET /api/monitors`: JSON API endpoint for monitor data

## Features

The dashboard displays:
- Total number of monitors
- Number of monitors UP
- Number of monitors DOWN
- Each monitor's name, URL, type, and status
- 24-hour uptime percentage
- 7-day uptime percentage
- Response times
- Visual progress bars for uptime statistics

## Troubleshooting

If you encounter any issues:

1. Check if the API key is correct
2. Verify your UptimeRobot account has the monitors
3. Check the container logs: `docker-compose logs`
4. Ensure port 8090 is not already in use

## License

MIT

