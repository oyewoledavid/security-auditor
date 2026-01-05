# Run the local development server
run:
	uvicorn app.main:app --reload

# Run tests
test:
	pytest -v

# Build and run Docker
docker-up:
	docker compose up --build

# Stop Docker and clean volumes
docker-down:
	docker compose down -v

# Clean up cache files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +