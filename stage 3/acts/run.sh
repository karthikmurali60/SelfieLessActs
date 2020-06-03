#!/bin/bash
docker build -t acts:latest .
docker run -d -p 8000:80 -v acts:/app/some acts:latest
