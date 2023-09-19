from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages

from datetime import datetime
import logging
import json

from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request

# Get an instance of a logger
logger = logging.getLogger(__name__)


# it is necessary to add .json
# see https://www.coursera.org/learn/ibm-cloud-native-full-stack-development-capstone/discussions/forums/ksOomD8oEeulfwrcHhaEnw/threads/EpNy8CF0Ee6fqw5g8_UaQQ/replies/0eY7KyF5Ee6qcgp0u5G9Fw/comments/Gq11LiP8Ee6kKxILEyYEPw
DEALER_URL = "https://us-south.functions.appdomain.cloud/api/v1/web/fae4e951-4cc0-43f5-a106-8eea510e9b6c/dealership-package/get-dealership.json"
GET_REVIEW_URL = "https://us-south.functions.appdomain.cloud/api/v1/web/fae4e951-4cc0-43f5-a106-8eea510e9b6c/dealership-package/get-review.json"
POST_REVIEW_URL = "https://us-south.functions.appdomain.cloud/api/v1/web/fae4e951-4cc0-43f5-a106-8eea510e9b6c/dealership-package/post-review.json"


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, "djangoapp/about.html", context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, "djangoapp/contact.html", context)


# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}

    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST["username"]
        password = request.POST["psw"]

        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)

        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)

    return redirect("djangoapp:index")


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    context = {}

    logout(request)

    return redirect("djangoapp:index")


# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}

    # If it is a GET request, just render the registration page
    if request.method == "GET":
        return render(request, "djangoapp/registration.html", context)

    # If it is a POST request
    elif request.method == "POST":
        # Get user information from request.POST
        username = request.POST["username"]
        password = request.POST["psw"]
        first_name = request.POST["firstname"]
        last_name = request.POST["lastname"]
        user_exist = False

        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))

        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password,
            )

            # Login the user
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, "djangoapp/registration.html", context)


# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}

    if request.method == "GET":
        dealerships = get_dealers_from_cf(DEALER_URL)
        # Concat all dealer's short name
        dealer_names = " ".join([dealer.short_name for dealer in dealerships])

        # return HttpResponse(dealer_names)

        context["dealer_names"] = dealer_names

        return render(request, "djangoapp/index.html", context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}

    if request.method == "GET":
        dealer_details = get_dealers_from_cf(DEALER_URL, dealerId=dealer_id)[0]
        context["dealer_details"] = dealer_details
        print(dealer_details)

        reviews_list = get_dealer_reviews_from_cf(GET_REVIEW_URL, dealer_id)

        # if "message" in reviews_list[0]:
        #     context["message"] = "No reviews found"
        # else:
        context["reviews_list"] = reviews_list

        return render(request, "djangoapp/dealer_details.html", context)


# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    context = {}
    review = {}
    json_payload = {}
    user = request.user

    if user:
        if request.method == "GET":
            dealer_details = get_dealers_from_cf(DEALER_URL, dealerId=dealer_id)[0]
            cars = CarModel.objects.filter(dealerId=dealer_id)
            context["cars"] = cars
            context["dealer"] = dealer_details

            return render(request, "djangoapp/add_review.html", context)

        if request.method == "POST":
            review["id"] = 1
            review["dealership"] = dealer_id
            review["name"] = user.first_name

            # TODO: check the different fields
            review["purchase"] = request.POST["purchasecheck"] == "on"
            review["review"] = request.POST["content"]
            review["purchase_date"] = request.POST["purchasedate"]

            car_details = request.POST["car"]
            car_info = car_details.split("-")
            review["car_make"] = car_info[0]
            review["car_model"] = car_info[1]
            review["car_year"] = car_info[2]

            review["time"] = datetime.utcnow().isoformat()

            json_payload["review"] = review
            response = post_request(POST_REVIEW_URL, json_payload)

            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
