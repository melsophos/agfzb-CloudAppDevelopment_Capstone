"""IBM Cloud Function that gets all reviews for a dealership

Returns:
    List: List of reviews for the given dealership
"""

from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_cloud_sdk_core import ApiException
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


def main(param_dict):
    dealer_id = param_dict.get("dealerId", None)

    authenticator = IAMAuthenticator(param_dict["IAM_API_KEY"])
    service = CloudantV1(authenticator=authenticator)
    service.set_service_url(param_dict["COUCH_URL"])

    selector = {}

    if dealer_id is not None and dealer_id != "":
        selector = {"dealership": {"$eq": int(dealer_id)}}

    try:
        response = service.post_find(
            db="reviews",
            selector=selector,
        ).get_result()

        result = {
            "headers": {"Content-Type": "application/json"},
            "body": {"data": response["docs"]},
        }

        return result

    except:
        return {"statusCode": 500, "message": "Something went wrong on the server"}
