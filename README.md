# disCarbon Emission API

An API to provide carbon emission estimates for flights, events and other activities.

## Development
### Running Natively

Assuming pyenv is used to manage virtual environments:
```
pyenv virtualenv 3.10 310-discarbon-emission-api
pyenv shell 310-discarbon-emission-api
pip install -r requirements.txt
uvicorn app.main:emission_api --reload
```

### Running in a Docker Container

```
docker build -t discarbon-emission-api .
docker run -it --init -p 8000:8000 -e PORT=8000 discarbon-emission-api
```

### Test in browser

Read the doc; http://127.0.0.1:8000/docs

Try an endpoint: http://127.0.0.1:8000/emissions/travel/planeByIATA/ZRH/ABZ/economy