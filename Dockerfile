# Use Python 3.11 slim on Debian Bookworm
FROM python:3.11-slim-bookworm

# -------- Install system dependencies --------
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# -------- Set default metadata environment variables --------
ENV DEFAULT_AUTHOR="Vist our Telegram channel @Dramafilez"
ENV DEFAULT_TITLE="Encoded by @Dramafilez"
ENV DEFAULT_VIDEO_TITLE="Vist our Telegram channel @Dramafilez"
ENV DEFAULT_AUDIO_TITLE="@Dramafilez"
ENV DEFAULT_SUBTITLE_TITLE="@Dramafilez"

# -------- Set working directory --------
WORKDIR /app

# -------- Copy dependencies and install --------
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# -------- Copy bot code --------
COPY . .

# -------- Run the bot --------
CMD ["python", "bot.py"]
