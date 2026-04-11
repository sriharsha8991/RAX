"""Full navigation test: Register -> Login -> Create Job -> Upload Resume -> 
List Candidates -> Get Analysis -> Generate Feedback"""
import asyncio
import json
import urllib.request
import urllib.error
import os, sys

BASE = "http://localhost:8001"

def api(method, path, body=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req)
        return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())

def upload_file(path, files_data, token):
    """Multipart upload for resume file."""
    import io
    boundary = "----WebKitFormBoundary7MA4YWxk"
    body = b""
    for field_name, (filename, content, content_type) in files_data.items():
        body += f"--{boundary}\r\n".encode()
        body += f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'.encode()
        body += f"Content-Type: {content_type}\r\n\r\n".encode()
        body += content + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    
    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Authorization": f"Bearer {token}"
    }
    req = urllib.request.Request(f"{BASE}{path}", data=body, headers=headers, method="POST")
    try:
        resp = urllib.request.urlopen(req)
        return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())

def main():
    results = []
    
    # 1. Register
    print("=" * 60)
    print("STEP 1: Register")
    status, data = api("POST", "/api/auth/register", {
        "email": "nav_test@rax.dev",
        "password": "Navigate123!",
        "full_name": "Navigation Tester"
    })
    print(f"  Status: {status}")
    print(f"  Response: {json.dumps(data, indent=2)[:200]}")
    results.append(("Register", status, status == 201))
    
    # 2. Login
    print("\n" + "=" * 60)
    print("STEP 2: Login")
    status, data = api("POST", "/api/auth/login", {
        "email": "nav_test@rax.dev",
        "password": "Navigate123!"
    })
    print(f"  Status: {status}")
    token = data.get("access_token", "")
    print(f"  Token: {token[:30]}..." if token else f"  Response: {data}")
    results.append(("Login", status, status == 200))
    
    # 3. Get current user
    print("\n" + "=" * 60)
    print("STEP 3: Get Current User (/api/auth/me)")
    status, data = api("GET", "/api/auth/me", token=token)
    print(f"  Status: {status}")
    print(f"  Response: {json.dumps(data, indent=2)[:200]}")
    user_id = data.get("id", "")
    results.append(("Get Me", status, status == 200))
    
    # 4. Create Job
    print("\n" + "=" * 60)
    print("STEP 4: Create Job")
    status, data = api("POST", "/api/jobs", {
        "title": "Senior Python Developer",
        "description": "We need a senior Python developer with FastAPI and SQLAlchemy experience. Must have 5+ years of experience.",
        "requirements_raw": {
            "skills": ["Python", "FastAPI", "SQLAlchemy", "PostgreSQL", "Docker"],
            "experience_years": 5,
            "education": "BS in Computer Science"
        }
    }, token=token)
    print(f"  Status: {status}")
    print(f"  Response: {json.dumps(data, indent=2)[:300]}")
    job_id = data.get("id", "")
    results.append(("Create Job", status, status == 201))
    
    # 5. List Jobs
    print("\n" + "=" * 60)
    print("STEP 5: List Jobs")
    status, data = api("GET", "/api/jobs", token=token)
    print(f"  Status: {status}")
    print(f"  Jobs count: {len(data) if isinstance(data, list) else 'N/A'}")
    results.append(("List Jobs", status, status == 200))
    
    # 6. Get Single Job
    print("\n" + "=" * 60)
    print(f"STEP 6: Get Job {job_id[:8]}...")
    status, data = api("GET", f"/api/jobs/{job_id}", token=token)
    print(f"  Status: {status}")
    print(f"  Title: {data.get('title', 'N/A')}")
    results.append(("Get Job", status, status == 200))
    
    # 7. Upload Resume (text-based PDF simulation)
    print("\n" + "=" * 60)
    print("STEP 7: Upload Resume")
    # Create a minimal PDF-like content  
    pdf_content = b"%PDF-1.4 fake resume content - John Doe, Python Developer with 7 years experience"
    status, data = upload_file(
        f"/api/resumes/upload?job_id={job_id}",
        {"file": ("john_doe_resume.pdf", pdf_content, "application/pdf")},
        token
    )
    print(f"  Status: {status}")
    print(f"  Response: {json.dumps(data, indent=2)[:300]}")
    resume_id = data.get("id", "")
    results.append(("Upload Resume", status, status in [200, 201]))
    
    # 8. List Candidates for Job
    print("\n" + "=" * 60)
    print("STEP 8: List Candidates")
    status, data = api("GET", f"/api/jobs/{job_id}/candidates", token=token)
    print(f"  Status: {status}")
    print(f"  Candidates: {len(data) if isinstance(data, list) else data}")
    results.append(("List Candidates", status, status == 200))
    
    # 9. Get Analysis (may not exist yet without pipeline)
    print("\n" + "=" * 60)
    print("STEP 9: Get Analyses for Job")
    status, data = api("GET", f"/api/jobs/{job_id}/analyses", token=token)
    print(f"  Status: {status}")
    print(f"  Response: {json.dumps(data, indent=2)[:200]}")
    results.append(("List Analyses", status, status in [200, 404]))
    
    # 10. Generate Feedback (may fail without analysis)
    print("\n" + "=" * 60)
    print("STEP 10: List Feedback")
    status, data = api("GET", "/api/feedback", token=token)
    print(f"  Status: {status}")
    print(f"  Response: {json.dumps(data, indent=2)[:200]}")
    results.append(("List Feedback", status, status in [200, 404]))
    
    # 11. Health check
    print("\n" + "=" * 60)
    print("STEP 11: Health Check")
    status, data = api("GET", "/health")
    print(f"  Status: {status}")
    results.append(("Health", status, status == 200))
    
    # Summary
    print("\n" + "=" * 60)
    print("NAVIGATION TEST SUMMARY")
    print("=" * 60)
    passed = 0
    for name, status, ok in results:
        icon = "PASS" if ok else "FAIL"
        print(f"  [{icon}] {name}: HTTP {status}")
        if ok:
            passed += 1
    print(f"\n  Result: {passed}/{len(results)} steps passed")

if __name__ == "__main__":
    main()
