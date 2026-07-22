def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app_name"] == "Voice Studio"


def test_ready_check(client):
    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


def test_system_status(client):
    response = client.get("/api/v1/system/status")
    assert response.status_code == 200
    data = response.json()
    assert "cuda_status" in data
    assert "storage_base_dir" in data


def test_full_voice_and_audio_generation_pipeline(client, generate_sample_wav):
    wav_bytes = generate_sample_wav(duration_sec=3.0)

    # 1. Upload reference voice
    upload_res = client.post(
        "/api/v1/voices/upload",
        data={"name": "Pipeline Voice", "language": "en", "gender": "female", "engine": "f5tts"},
        files={"file": ("voice_ref.wav", wav_bytes, "audio/wav")},
    )
    assert upload_res.status_code == 201
    voice_id = upload_res.json()["voice"]["id"]

    # 2. Synthesize audio speech from text script via mock/f5tts engine
    gen_res = client.post(
        "/api/v1/audio/generate",
        json={
            "voice_id": voice_id,
            "text": "Today we are learning Model Context Protocol with Voice Studio.",
            "engine": "mock",
            "speed": 1.0,
        },
    )
    assert gen_res.status_code == 200
    gen_data = gen_res.json()
    assert gen_data["message"] == "Audio synthesized successfully."
    assert gen_data["data"]["voice_id"] == voice_id
    assert gen_data["data"]["duration"] > 0

    # 3. Query Audio History
    hist_res = client.get("/api/v1/audio/history")
    assert hist_res.status_code == 200
    hist_data = hist_res.json()
    assert hist_data["total"] == 1
    assert hist_data["history"][0]["voice_id"] == voice_id
