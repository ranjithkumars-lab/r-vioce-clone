import time


def test_enqueue_and_poll_job(client, generate_sample_wav):
    wav_bytes = generate_sample_wav(duration_sec=3.0)

    # 1. Upload reference voice
    upload_res = client.post(
        "/api/v1/voices/upload",
        data={"name": "Async Job Voice", "language": "en", "gender": "male", "engine": "mock"},
        files={"file": ("job_ref.wav", wav_bytes, "audio/wav")},
    )
    assert upload_res.status_code == 201
    voice_id = upload_res.json()["voice"]["id"]

    # 2. Enqueue async job
    enqueue_res = client.post(
        "/api/v1/jobs/enqueue",
        json={
            "voice_id": voice_id,
            "text": "Testing background queue worker daemon in Voice Studio.",
            "engine": "mock",
            "speed": 1.0,
        },
    )
    assert enqueue_res.status_code == 202
    job_id = enqueue_res.json()["job_id"]

    # 3. Poll job status until COMPLETED
    attempts = 0
    while attempts < 20:
        poll_res = client.get(f"/api/v1/jobs/{job_id}")
        assert poll_res.status_code == 200
        poll_data = poll_res.json()
        if poll_data["status"] == "COMPLETED":
            assert poll_data["progress_percentage"] == 100
            assert poll_data["output_url"] is not None
            break
        time.sleep(0.1)
        attempts += 1
