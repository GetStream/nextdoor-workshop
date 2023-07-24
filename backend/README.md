# Backend

This is a simple Python/Flask HTTP server that shows these integration points with Stream Chat API:

- Token Generation
- Channel creation
- Message creation
- Webhook handling

## Live version

A version of this API is up and running on `https://flask.gtstrm.com/` to make it simpler for frontend developers to get their integration up and running.

## Postman / Examples

The simplest way to play with the endpoints is to import [postman collection](https://github.com/GetStream/nextdoor-workshop/blob/main/backend/Next%20Door%20-%20Workshop.postman_collection.json) in the Postman application.

## Setup

To run this locally you need to have a recent version of Python and install the dependencies listed in the `requirements.txt` file.

A simple way to do this is to create a virtualenv and install all deps there:

```commandline
virtualenv .

source bin/activate

pip install -r requirements.txt
```

**Setup API credentials**

Credentials are loaded using dotenv, you can use the `.env.example` file as template and place the Stream API creds in there

```commandline
cp .env.example .env
```

After this you can run the Flask app locally with:

```commandline
python -m flask run
```

## Configuration

The live version of this backend is configured with the credentials from the Stream app used for this workshop (see top-level Readme).

## Token generation

The `generate_token` handler generates a valid user token to connect and authenticate to Stream Chat. 
In a real application the `user_id` is either validated or comes from the auth session, in this simple app we simply generate a valid token.

## Syncing channels and messages

The `app.py` exposes two endpoints that insert channels and messages to Stream Chat. This is a good starting point to implement
dual-write and send all new channels and messages to Stream.

To keep things simple we expose this from an HTTP endpoint and only support creation of messages and channels. 
As a next step, you want this code to run directly on your backend and also support message and channel deletion.  

## Webhook handler

Webhooks are very convenient to sync the primary chat with data created directly to Stream Chat. In this codebase we only have boilerplate code
that gets the JSON body and validates it.

Relevant documentation about webhook events can be found [here](https://getstream.io/chat/docs/python/webhooks_overview/?language=python)

Webhook payloads from Stream include a signature header that can be verified using the shared API Secret
further hardening can be achieved by exposing this service to Stream static list of public IPs
the allow list is documented [here](https://getstream.io/chat/docs/python/webhooks_overview/?language=python)

Note: Webhook requests are logged and visible from Stream Dashboard [here](https://dashboard.getstream.io/app/1258553/chat/webhookpushlogs).
