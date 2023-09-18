from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core import ApiException


def main(param_dict):
    authenticator = IAMAuthenticator(param_dict["IAM_API_KEY"])
    service = CloudantV1(authenticator=authenticator)
    service.set_service_url(param_dict["COUCH_URL"])

    try:
        response = service.post_document(
            db="reviews",
            document=param_dict["review"],
        ).get_result()

        result = {
            "headers": {"Content-Type": "application/json"},
            "body": {"data": response},
        }
        return result

    except:
        return {"statusCode": 500, "message": "Something went wrong on the server"}
