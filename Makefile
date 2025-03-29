run-dev:
	ENV=development fastapi dev main.py

run-prod:
	ENV=production fastapi build main.py
