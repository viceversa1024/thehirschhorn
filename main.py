import functions_framework
from lambda_function import lambda_handler


@functions_framework.http
def run(request):
    """
    This function is a wrapper for the AWS Lambda function to run in Google Cloud Functions.
    It takes the event and context from the Google Cloud Function and passes it to the AWS Lambda function.
    """
    # Call the lambda_handler function with the event and context
    print(request)
    my_cookie ="eyJraWQiOiJ3RmJUMElVdVdadk9BMkdNODBrOWYyUVhvdnFrXC81YUt1NWNVN1p6TmpJVT0iLCJhbGciOiJSUzI1NiJ9.eyJhdF9oYXNoIjoiZU03TXJtTkMyZV9RMVA1SG92Vy13USIsInN1YiI6Ijg0YjhjNDg4LWMwOTEtNzA3Yy1lMGFkLWRhNTY4N2NlNjA5MiIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV81cjMwSkZuQ2siLCJjb2duaXRvOnVzZXJuYW1lIjoiODRiOGM0ODgtYzA5MS03MDdjLWUwYWQtZGE1Njg3Y2U2MDkyIiwiYXVkIjoiN2NpN24wcDdvbDRlb2VlcDk2Z3BrbmRic3AiLCJldmVudF9pZCI6IjdjYWE0OTgwLTE1OTktNDFhNC1hMzg0LTVkMGZkNDk1YTY3ZCIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNzQ2NzczMjk0LCJleHAiOjE3NDY3NzY4OTQsImlhdCI6MTc0Njc3MzI5NCwianRpIjoiZGVlNjcyZmItNzM0Zi00YmMwLWIyZDEtMjkyZDllYzQ1N2E0IiwiZW1haWwiOiJ3YXRlcm1haEB1Y2kuZWR1In0.TsggKWHWnW5dJEZ_dMX4M5JUPj8CdEf6gVldCOC4txnYsoCSjOObFnxg08x61kcOX7-VjbAddeNu67fbuROZo424S5EUA6F0Ei4dhdI6wO2GfsZAHT6LaQC8g86b1L4R_4Y4R6kMQfP6OCvebSFaHPze2kWPiYMa_-JuhipOgtp7BfGjSEUTa7cfZ0naGvsb5wLLRXb8QFLJn8ZwJW3hhEiQHbKyvj0ggYQGFLXkMcOFILHKmzqxvH5E7XV-yB17PKPOg04pZDRGd1bby2H7jBv4leCgZle2O2vbyWEhWds18TCjr4WnfNRvxmcWTFyPYSowNSkIwfIQxwHdSSYKSQ"
    response = lambda_handler(
        {
            "httpMethod": request.method,
            "path": request.path,
            "headers": {
                "Cookie": f"keene_jwt={my_cookie}",
#                "Cookie": None,
            },
            "body": request.get_data(as_text=True),
        },
        None,
    )

    return (
        response["body"],
        response["statusCode"],
        response["headers"],
    )
