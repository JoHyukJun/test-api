## RUN
```bash
docker-compose up --build
```


## TEST
### GET
- url: localhost:8000/api/v1
### POST
- 기간
```json
{
    "startdate": "2022-05-20",
    "enddate": "2022-06-10"
}
```
- 특정일
```json
{
    "startdate": "2022-05-20",
    "enddate": null
}
```