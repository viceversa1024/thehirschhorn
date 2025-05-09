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
    my_cookie = "eyJraWQiOiJ3RmJUMElVdVdadk9BMkdNODBrOWYyUVhvdnFrXC81YUt1NWNVN1p6TmpJVT0iLCJhbGciOiJSUzI1NiJ9.eyJhdF9oYXNoIjoiak5zMkU2R1JWZUo5VTR0V0hxZlRTUSIsInN1YiI6Ijg0YjhjNDg4LWMwOTEtNzA3Yy1lMGFkLWRhNTY4N2NlNjA5MiIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV81cjMwSkZuQ2siLCJjb2duaXRvOnVzZXJuYW1lIjoiODRiOGM0ODgtYzA5MS03MDdjLWUwYWQtZGE1Njg3Y2U2MDkyIiwiYXVkIjoiN2NpN24wcDdvbDRlb2VlcDk2Z3BrbmRic3AiLCJldmVudF9pZCI6IjQ5NTk2NDEwLWRkY2QtNDFmZC05NjY5LWYzZjZmZTUxZjUwNyIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNzQ2ODE1MDYyLCJleHAiOjE3NDY4MTg2NjIsImlhdCI6MTc0NjgxNTA2MiwianRpIjoiNmVlNWI0NDctY2FkYy00ZGYwLWJkMDUtZDI5ZDYwOTlkYjNhIiwiZW1haWwiOiJ3YXRlcm1haEB1Y2kuZWR1In0.fFL7T1XfV9Lpo1yA4txojvJkZMVYnjlhqf5yQRKbdkfhrAVK0qFi4PZUn2KplHB25qrm7EooF9kjosXBbu52Nz3aG053Yb1eay6Pp7EM8IQXS3WtO-klYGU2cLWxDd2z7-iNg13j9a8WeGAbBGJCytMqONXtRanizjHRJitft4W3FOOoVyDom9RQpIcK2s18-o8QyLl78SDE-t-uBNdv_3o6L_QvnVQjoVPlD5U0HL3QM-34EXth7bYfWuOAeH183sXWWamd7DY1bt9OVvMpProBBuJfzzBoPiRecjI_voETgkonbkzbqbLXaCFPqFAN1ihgb1c4C-6X7xyA77vQxQ"
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
