import httpx

def send_post_request(api_url, post_data, headers={}, timeout=300):
    headers = {"Content-Type": "application/json", **headers}

    try:
        response = httpx.post(api_url, headers=headers, json=post_data,
                                 timeout=timeout)

        if response.status_code in (200, 201, 204):
            data = response.json()
            return data
        else:
            return {"status": False, "messages": "Failed to do post request"}
    except Exception as e:
        return {"status": False, "resultDesc": f"{e}"}