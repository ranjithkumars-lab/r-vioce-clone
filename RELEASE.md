# Voice Studio Release Checklist

Use this checklist to ensure consistent and high-quality releases for Voice Studio.

## Pre-Release Preparation

- [ ] **License Verification**: Run a dependency check to ensure all new packages comply with the open-source license.
- [ ] **Security Scan**: Verify `bandit` and `npm audit` reports in GitHub Actions are clean.
- [ ] **Dependency Pinning**: Ensure `requirements.txt` and `package-lock.json` are strictly pinned. No floating versions.
- [ ] **Secrets Check**: Ensure no secrets, API keys, or internal IP addresses have leaked into the repository.
- [ ] **`.env.example`**: Verify that all new configuration variables are documented in `.env.example`.

## Testing

- [ ] **Backend Tests**: Run `pytest -v` locally and ensure 100% pass rate.
- [ ] **Frontend Tests**: Run `npm run test` locally and ensure UI components render correctly.
- [ ] **Docker Build**: Run `docker compose up --build` and verify the stack starts cleanly without errors.
- [ ] **End-to-End Test**: Generate a voice clone using the UI to verify the full API -> Queue -> Worker -> Engine -> UI pipeline.

## Documentation

- [ ] **Changelog**: Update `CHANGELOG.md` with all new features, bug fixes, and breaking changes.
- [ ] **README**: Update the benchmarking table in `README.md` if performance characteristics have changed.
- [ ] **API Docs**: Ensure `docs/api.md` reflects any newly added endpoints.

## Publishing

- [ ] **Version Bump**: Update version strings in `backend/app/main.py`, `frontend/package.json`, and `docker-compose.yml`.
- [ ] **Git Tag**: Create an annotated git tag (e.g., `git tag -a v1.0.0 -m "Release v1.0.0"`).
- [ ] **GitHub Release**: Push the tag (`git push origin v1.0.0`) and draft a GitHub Release with the compiled `CHANGELOG.md` notes.
- [ ] **Docker Hub**: Push the new versioned images to the container registry.
