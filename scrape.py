"""Ignore the code quality this a wip"""

import json
import subprocess
import requests
from db import get_db_connection


def clean_json(json_payload):
    """Clean the json payload using the text-bison model"""
    tries = 0

    def inner_clean_json():
        nonlocal tries

        print(f"tries: {tries}")
        if tries > 3:
            return json_payload
        try:
            url = "https://us-central1-aiplatform.googleapis.com/v1/projects/nexscript-ai/locations/us-central1/publishers/google/models/text-bison:predict"

            reponse_format = str(
                {
                    "uid": "PERSON's UID or ID",
                    "full_name": "PERSON's full name cleaned to international standards",
                    "phone_number": "PERSON's phone number cleaned to international standards using e164 ditch the '+' character",
                    "email": "PERSON's email",
                    "school": "Expand the abbreviation and misspellings to the full school name cleaned to international standards remove uneccessary words or remarks",
                    "location": "PERSON's general location cleaned to international standards",
                    "lat": "If it has location or school it MUST have lat and lng MUST BE A NUMBER use the location and school to find the general latitude of the location or school",
                    "lng": "If it has location or school it MUST have lat and lng MUST BE A NUMBER use the location and school to find the general longitude of the location or school",
                }
            )
            payload = str(
                {
                    "instances": [
                        {
                            "prompt": f"""The response MUST be in straight json and MUST use SINGLE QUOTES and MUST not have mark down formatting, each school or location has lat and lng you must find them at all costs. {str(json_payload)} only provided the json if it is clean just output the json as is. Try to provide the exact lattitude and longitude of the location or school the response should be in this format:  {reponse_format}"""
                        }
                    ],
                    "parameters": {
                        "temperature": 0.8,
                        "maxOutputTokens": 256,
                        "topP": 0.5,
                        "topK": 3,
                    },
                }
            )
            # use the cli gcloud auth print-access-token to get the auth token

            auth_token = (
                subprocess.run(
                    ["gcloud", "auth", "print-access-token"],
                    capture_output=True,
                    check=True,
                )
                .stdout.decode("utf-8")
                .strip()
            )

            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json; charset=utf-8",
            }

            response = requests.request(
                "POST",
                url,
                data=payload,
                headers=headers,
                timeout=60,
            )

            if response.status_code != 200:
                print(f"An error occurred: {response.text}")
                tries += 1
                inner_clean_json()

            return json.loads(
                response.json()["predictions"][0]["content"]
                .replace("'", '"')
                .replace("None", "null")
            )

        except Exception as e:
            print(f"An error occurred: {e}")
            return json_payload

    return inner_clean_json()


def main():
    total_page_count = 0
    page = 1
    count = 0
    conn = get_db_connection()
    if conn is not None:
        cur = conn.cursor()
        try:
            url = "https://hackclub.slack.com/api/search.modules.people"

            querystring = {
                "_x_id": "b16c11eb-1703041582.518",
                "_x_csid": "y6NZM1UMLL8",
                "slack_route": "T0266FRGM",
                "_x_version_ts": "1703037446",
                "_x_frontend_build_type": "current",
                "_x_desktop_ia": "4",
                "_x_gantry": "true",
                "fp": "21",
            }

            custom_fields = {"School": "Xf0DMGGW01", "Location": "Xf01S5PAG9HQ"}

            headers = {
                "authority": "hackclub.slack.com",
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.7",
                "content-type": "multipart/form-data; boundary=---011000010111000001101001",
                "cookie": "b=32fca4965e4c29eb7aa084a34095252f; lc=1703030633; shown_ssb_redirect_page=1; shown_download_ssb_modal=1; show_download_ssb_banner=1; no_download_ssb_banner=1; tz=-360; x=32fca4965e4c29eb7aa084a34095252f.1703041384; web_cache_last_updateda359014c7ed6cd624afc77b9bfc2cad4=1703041473335; d-s=1703041488; d=xoxd-pIcEnJ0Gyq6dCMIWdWmZrcg5GCjLeTRVC5zR2sOhlmrm%2FB93MbXWIjrAOGpiwHUvlkSmHcUe%2FTqs1uV3S4V8WEDIv7A%2Baau95ud9c55pOjD%2FLrc3VTBZJIVGPby5HvVL3Cw39HU57ScCUG4mJfpslWAJZl%2Bw6xMGlrUUA0%2FKiu5HA%2BjV5C0X8eDhCOFqQ8kikkmZ7xc%3D; uc=xoxd-%2BQ1TO7yVP3F%2B1JVYHJZTMuhDBRpBJLdYyX%2FuG6zmSULIbZ%2FscTI1Nh7473Fb00cpupLKEIdyiKLtOLs%2Bp1HNUiNyAfIui62fgvlY5rLz8EyjE%2BPyWQ3M8xQ0%2FCB6yihPgKyr%2BAI9b2NDR7Y6ubB1bt8BgdlnZxfnHWW6u2zAVsFKvlyEplJ7%2FdbeWKmfCB5zIngU2HY%3D",
                "origin": "https://app.slack.com",
                "sec-ch-ua-mobile": "?0",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "sec-gpc": "1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            }

            while True:
                if page > total_page_count and total_page_count != 0:
                    print("Done!")
                    break
                print(f"Page {page}")
                payload = f'-----011000010111000001101001\r\nContent-Disposition: form-data; name="token"\r\n\r\nxoxc-2210535565-6371193022706-6364557383558-4548f1788c415f6aa3b99acbc92ae6d6b02ffd43dc41ff20a7fb03e92cc1c7df\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name="query"\r\n\r\n\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name="module"\r\n\r\npeople\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name="page"\r\n\r\n{page}\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name="sort"\r\n\r\nreccomended\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name="count"\r\n\r\n100\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name="browse"\r\n\r\nstandard\r\n-----011000010111000001101001--\r\n'

                response = requests.request(
                    "POST",
                    url,
                    data=payload,
                    headers=headers,
                    params=querystring,
                    timeout=60,
                )
                if total_page_count == 0:
                    total_page_count = response.json()["pagination"]["page_count"]
                items = response.json()["items"]

                for item in items:
                    # make sure the profile has either a school or location
                    count += 1
                    print("User: ", count)
                    profile = item["profile"]
                    fields = profile["fields"]
                    # see if the fields is not an empty dict
                    print(profile)

                    json_payload = {
                        "uid": item["id"],
                        "full_name": profile["real_name"],
                        "phone_number": profile["phone"],
                        "email": profile["email"],
                        "school": fields[custom_fields["School"]]["value"]
                        if custom_fields["School"] in fields
                        else None,
                        "location": fields[custom_fields["Location"]]["value"]
                        if custom_fields["Location"] in fields
                        else None,
                        "lat": None,
                        "lng": None,
                    }

                    json_payload = clean_json(json_payload)
                    print(json_payload)
                    print(
                        "Inserting into database",
                        profile["title"],
                        profile["image_512"],
                    )

                    conn.execute(
                        """
                    INSERT INTO public.people (uid, full_name, phone_number, email, school, location, lat, lng, geom, title, profile_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s, %s)
                    ON CONFLICT (uid) DO UPDATE
                    SET full_name = EXCLUDED.full_name,
                        phone_number = EXCLUDED.phone_number,
                        email = EXCLUDED.email,
                        school = EXCLUDED.school,
                        location = EXCLUDED.location,
                        lat = EXCLUDED.lat,
                        lng = EXCLUDED.lng,
                        geom = ST_SetSRID(ST_MakePoint(EXCLUDED.lng, EXCLUDED.lat), 4326),
                        title = EXCLUDED.title,
                        profile_url = EXCLUDED.profile_url
                    """,
                        (
                            json_payload["uid"],
                            json_payload["full_name"],
                            json_payload["phone_number"],
                            json_payload["email"],
                            json_payload["school"],
                            json_payload["location"],
                            json_payload["lat"],
                            json_payload["lng"],
                            json_payload[
                                "lng"
                            ],  # Assuming lng is still used here for ST_MakePoint
                            json_payload[
                                "lat"
                            ],  # Assuming lat is still used here for ST_MakePoint
                            profile["title"],
                            profile["image_512"],
                        ),
                    )

                    conn.commit()

                page += 1

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            cur.close()
            conn.close()


if __name__ == "__main__":
    main()
