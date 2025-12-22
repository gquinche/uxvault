Provide your Supabase credentials. In Streamlit Cloud, add them to secrets.toml:

[connections.supabase_connection]
url = "https://your-project.supabase.co"
key = "service_role_or_anon_key"
For local development you can use environment variables (SUPABASE_URL, SUPABASE_KEY) or pass the values directly during connection creation.

Create the cached connection in your app.

import streamlit as st
from st_supabase_connection import SupabaseConnection

st_supabase = st.connection(
    name="supabase_connection",
    type=SupabaseConnection,
    ttl=None,  # cache indefinitely; override when you need fresher data
)

# Example: list buckets without re-authenticating on every rerun
buckets = st_supabase.list_buckets()
st.write(buckets)
🧑‍🎓 Interactive tutorial
Open in Streamlit
Web capture_2-12-2023_124639_st-supabase-connection streamlit app

🤔 Why use this?
 Cache functionality to cache returned results. Save time and money on your API requests
 Same method names as the Supabase Python API. Minimum relearning required
 Exposes more storage methods than currently supported by the Supabase Python API. For example, update(), create_signed_upload_url(), and upload_to_signed_url()
 Handles common Supabase quirks—leading slashes are normalised, MIME types inferred, and downloads streamed in memory—so you spend less time on glue code.
 Less keystrokes required when integrating with your Streamlit app.
Examples with and without the connector
🛠️ Setup
Install st-supabase-connection
pip install st-supabase-connection
Set the SUPABASE_URL and SUPABASE_KEY Streamlit secrets as described here.
Note

For local development outside Streamlit, you can also set these as your environment variables (recommended), or pass these to the url and key args of st.connection().

🪄 Usage
Import
from st_supabase_connection import SupabaseConnection, execute_query
Initialize
st_supabase_client = st.connection(
    name="YOUR_CONNECTION_NAME",
    type=SupabaseConnection,
    ttl=None,
)
Use the connection to work with Storage, Database, and Auth in a cached, Streamlit-friendly way:

# Storage
file_name, mime, data = st_supabase.download("bucket", "path/to/report.csv", ttl=300)

# Database (leverages postgrest-py under the hood)
from st_supabase_connection import execute_query
users = execute_query(
    st_supabase.table("users").select("name, email").order("created_at", desc=True),
    ttl="15m",
)

# Auth (cached helper)
st_supabase.cached_sign_in_with_password({"email": email, "password": password})
👌 Supported methods
Storage
Database
Auth
📚 Examples
📦 Storage operations
List existing buckets
>>> st_supabase_client.list_buckets(ttl=None)
[
    SyncBucket(
        id="bucket1",
        name="bucket1",
        owner="",
        public=False,
        created_at=datetime.datetime(2023, 7, 31, 19, 56, 21, 518438, tzinfo=tzutc()),
        updated_at=datetime.datetime(2023, 7, 31, 19, 56, 21, 518438, tzinfo=tzutc()),
        file_size_limit=None,
        allowed_mime_types=None,
    ),
    SyncBucket(
        id="bucket2",
        name="bucket2",
        owner="",
        public=True,
        created_at=datetime.datetime(2023, 7, 31, 19, 56, 28, 203536, tzinfo=tzutc()),
        updated_at=datetime.datetime(2023, 7, 31, 19, 56, 28, 203536, tzinfo=tzutc()),
        file_size_limit=100,
        allowed_mime_types=["image/jpg", "image/png"],
    ),
]
Create a bucket
>>> st_supabase_client.create_bucket("new_bucket")
{'name': 'new_bucket'}
Get bucket details
>>> st_supabase_client.get_bucket("new_bucket")
SyncBucket(id='new_bucket', name='new_bucket', owner='', public=True, created_at=datetime.datetime(2023, 8, 2, 19, 41, 44, 810000, tzinfo=tzutc()), updated_at=datetime.datetime(2023, 8, 2, 19, 41, 44, 810000, tzinfo=tzutc()), file_size_limit=None, allowed_mime_types=None)
Update a bucket
>>> st_supabase_client.update_bucket(
      "new_bucket",
      file_size_limit=100,
      allowed_mime_types=["image/jpg", "image/png"],
      public=True,
    )
{'message': 'Successfully updated'}
Move files in a bucket
>>> st_supabase_client.move("new_bucket", "test.png", "folder1/new_test.png")
{'message': 'Successfully moved'}
List objects in a bucket
>>> st_supabase_client.list_objects("new_bucket", path="folder1", ttl=0)
[
    {
        "name": "new_test.png",
        "id": "e506920e-2834-440e-85f1-1d5476927582",
        "updated_at": "2023-08-02T19:53:22.53986+00:00",
        "created_at": "2023-08-02T19:52:20.404391+00:00",
        "last_accessed_at": "2023-08-02T19:53:21.833+00:00",
        "metadata": {
            "eTag": '"814a0034f5549e957ee61360d87457e5"',
            "size": 473831,
            "mimetype": "image/png",
            "cacheControl": "max-age=3600",
            "lastModified": "2023-08-02T19:53:23.000Z",
            "contentLength": 473831,
            "httpStatusCode": 200,
        },
    }
]
Empty a bucket
>>> st_supabase_client.empty_bucket("new_bucket")
{'message': 'Successfully emptied'}
Delete a bucket
>>> st_supabase_client.delete_bucket("new_bucket")
{'message': 'Successfully deleted'}
🗄️ Database operations
Simple query
>>> execute_query(st_supabase_client.table("countries").select("*"), ttl=0)
APIResponse(
    data=[
        {"id": 1, "name": "Afghanistan"},
        {"id": 2, "name": "Albania"},
        {"id": 3, "name": "Algeria"},
    ],
    count=None,
)
Query with join
>>> execute_query(
        st_supabase_client.table("users").select("name, teams(name)", count="exact"),
        ttl="1h",
    )

APIResponse(
    data=[
        {"name": "Kiran", "teams": [{"name": "Green"}, {"name": "Blue"}]},
        {"name": "Evan", "teams": [{"name": "Blue"}]},
    ],
    count=2,
)
Filter through foreign tables
>>> execute_query(
        st_supabase_client.table("cities").select("name, countries(*)", count="exact").eq("countries.name", "Curaçao"),
        ttl=None,
    )

APIResponse(
    data=[
        {
            "name": "Kralendijk",
            "countries": {
                "id": 2,
                "name": "Curaçao",
                "iso2": "CW",
                "iso3": "CUW",
                "local_name": None,
                "continent": None,
            },
        },
        {"name": "Willemstad", "countries": None},
    ],
    count=2,
)
Insert rows
>>> execute_query(
        st_supabase_client.table("countries").insert(
            [{"name": "Wakanda", "iso2": "WK"}, {"name": "Wadiya", "iso2": "WD"}], count="None"
        ),
        ttl=0,
    )

APIResponse(
    data=[
        {
            "id": 250,
            "name": "Wakanda",
            "iso2": "WK",
            "iso3": None,
            "local_name": None,
            "continent": None,
        },
        {
            "id": 251,
            "name": "Wadiya",
            "iso2": "WD",
            "iso3": None,
            "local_name": None,
            "continent": None,
        },
    ],
    count=None,
)
🔒 Auth operations
Note

If the call is valid, all Supabase Auth methods return the same response structure:

{
  "user": {
    "id": "e1f550fd-9cd1-44e4-bbe4-c04e91cf5544",
    "app_metadata": {
      "provider": "email",
      "providers": ["email"]
    },
    "user_metadata": {
      "attribution": "I made it :)",
      "fname": "Siddhant"
    },
    "aud": "authenticated",
    "confirmation_sent_at": null,
    "recovery_sent_at": null,
    "email_change_sent_at": null,
    "new_email": null,
    "invited_at": null,
    "action_link": null,
    "email": "test.user@abc.com",
    "phone": "",
    "created_at": "datetime.datetime(2023, 10, 8, 20, 26, 30, 365359, tzinfo=datetime.timezone.utc)",
    "confirmed_at": null,
    "email_confirmed_at": "datetime.datetime(2023, 10, 8, 20, 26, 30, 373966, tzinfo=datetime.timezone.utc)",
    "phone_confirmed_at": null,
    "last_sign_in_at": "datetime.datetime(2023, 10, 8, 20, 26, 30, 377070, tzinfo=datetime.timezone.utc)",
    "role": "authenticated",
    "updated_at": "datetime.datetime(2023, 10, 8, 20, 26, 30, 381584, tzinfo=datetime.timezone.utc)",
    "identities": [
      {
        "id": "e1f550fd-9cd1-44e4-bbe4-c04e91cf5544",
        "user_id": "e1f550fd-9cd1-44e4-bbe4-c04e91cf5544",
        "identity_data": {
          "email": "siddhant.sadangi@gmail.com",
          "sub": "e1f550fd-9cd1-44e4-bbe4-c04e91cf5544"
        },
        "provider": "email",
        "created_at": "datetime.datetime(2023, 10, 8, 20, 26, 30, 370040, tzinfo=datetime.timezone.utc)",
        "last_sign_in_at": "datetime.datetime(2023, 10, 8, 20, 26, 30, 370002, tzinfo=datetime.timezone.utc)",
        "updated_at": "datetime.datetime(2023, 10, 8, 20, 26, 30, 370040, tzinfo=datetime.timezone.utc)"
      }
    ],
    "factors": null
  },
  "session": {
    "provider_token": null,
    "provider_refresh_token": null,
    "access_token": "***",
    "refresh_token": "***",
    "expires_in": 3600,
    "expires_at": 1696800390,
    "token_type": "bearer",
    "user": {
      "id": "e1f550fd-9cd1-44e4-bbe4-c04e91cf5544",
      "app_metadata": {
        "provider": "email",
        "providers": ["email"]
      },
      "user_metadata": {
        "attribution": "I made it :)",
        "fname": "Siddhant"
      },
      "aud": "authenticated",
      "confirmation_sent_at": null,
      "recovery_sent_at": null,
      "email_change_sent_at": null,
      "new_email": null,
      "invited_at": null,
      "action_link": null,
      "email": "test.user@abc.com",
      "phone": "",
      "created_at": "datetime.datetime(2023, 10, 8, 20, 26, 30, 365359, tzinfo=datetime.timezone.utc)",
      "confirmed_at": null,
      "email_confirmed_at": "datetime.datetime(2023, 10, 8, 20, 26, 30, 373966, tzinfo=datetime.timezone.utc)",
      "phone_confirmed_at": null,
      "last_sign_in_at": "datetime.datetime(2023, 10, 8, 20, 26, 30, 377070, tzinfo=datetime.timezone.utc)",
      "role": "authenticated",
      "updated_at": "datetime.datetime(2023, 10, 8, 20, 26, 30, 381584, tzinfo=datetime.timezone.utc)",
      "identities": [
        {
          "id": "e1f550fd-9cd1-44e4-bbe4-c04e91cf5544",
          "user_id": "e1f550fd-9cd1-44e4-bbe4-c04e91cf5544",
          "identity_data": {
            "email": "siddhant.sadangi@gmail.com",
            "sub": "e1f550fd-9cd1-44e4-bbe4-c04e91cf5544"
          },
          "provider": "email",
          "created_at": "datetime.datetime(2023, 10, 8, 20, 26, 30, 370040, tzinfo=datetime.timezone.utc)",
          "last_sign_in_at": "datetime.datetime(2023, 10, 8, 20, 26, 30, 370002, tzinfo=datetime.timezone.utc)",
          "updated_at": "datetime.datetime(2023, 10, 8, 20, 26, 30, 370040, tzinfo=datetime.timezone.utc)"
        }
      ],
      "factors": null
    }
  }
}
Create new user
st_supabase_client.auth.sign_up(
    dict(
        email='test.user@abc.com',
        password='***',
        options=dict(
            data=dict(
                fname='Siddhant',
                attribution='I made it :)',
            )
        )
    )
)
Sign in with password
SupabaseConnection() offers a cached version of sign_in_with_password() for faster, request-free sign-ins.

st_supabase_client.cached_sign_in_with_password(dict(email='test.user@abc.com', password='***'))
Retrieve session
st_supabase_client.auth.get_session()
Retrieve user
st_supabase_client.auth.get_user()
Sign out
st_supabase_client.auth.sign_out()
Note

Check the Supabase Python API reference for more examples.

⭐ Explore all options in a demo app