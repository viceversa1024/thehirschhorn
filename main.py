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
    my_cookie = "eyJraWQiOiJ3RmJUMElVdVdadk9BMkdNODBrOWYyUVhvdnFrXC81YUt1NWNVN1p6TmpJVT0iLCJhbGciOiJSUzI1NiJ9.eyJhdF9oYXNoIjoiR2VmcHVMUDktZUVrRFJaQTdnUHp6dyIsInN1YiI6Ijg0YjhjNDg4LWMwOTEtNzA3Yy1lMGFkLWRhNTY4N2NlNjA5MiIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV81cjMwSkZuQ2siLCJjb2duaXRvOnVzZXJuYW1lIjoiODRiOGM0ODgtYzA5MS03MDdjLWUwYWQtZGE1Njg3Y2U2MDkyIiwiYXVkIjoiN2NpN24wcDdvbDRlb2VlcDk2Z3BrbmRic3AiLCJldmVudF9pZCI6IjQ2N2E5MWFiLWU0NWUtNGM5OC1hMzQ0LTFkMzA1OWFiMGI2YSIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNzQ2ODIxMjYzLCJleHAiOjE3NDY4MjQ4NjMsImlhdCI6MTc0NjgyMTI2MywianRpIjoiZWJmNWZmMmUtY2JjYS00YWU0LWJlNDAtNzNmYzk5NzMxNWExIiwiZW1haWwiOiJ3YXRlcm1haEB1Y2kuZWR1In0.o9SWqPvmA04xG0sk8tzjdYOyDLyz8XbhQQ7phAr4FM08VZ1MwG_n70Y0utoV6klJBkeSLE8T7Ab6Mt7vokPv0Ie7dVTTG_vNEDu19yVt0GFm2fnRRVuUSgoxFPybhMgN6JbBJAf7eAJbDEObCDiMt3firqG87EiNL8HWkOm_xVGZDgB6XEOyy3kDCEVZCl6HpK0yM24Y3EAsleXaQ7YQnZKgNdyr03H_Guu11V0V8bvmhdo88UOFIiNxWoEkIcEG_DY5RoMrz5I8Kf9zcNHXNXkRn93yulBKUIQUugsG5XYP99y8_97oc8zR-qHn9y1t4tJm4aB8MrymemjCXE5Kwg"
    response = lambda_handler(
        {
            "httpMethod": request.method,
            "path": request.path,
            "headers": {
                "cookie": f"keene_jwt={my_cookie}",
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
