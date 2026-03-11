import uuid
import os
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import traceback

from serve_pipeline import serve_pipeline as _run_serve_pipeline

app = FastAPI(title="AI Documentation Generator API")

# Serve the frontend UI from /ui path
_BACKEND_DIR = Path(__file__).resolve().parent
_FRONTEND_DIR = _BACKEND_DIR.parent / "frontend"
if _FRONTEND_DIR.exists():
    app.mount("/ui", StaticFiles(directory=str(_FRONTEND_DIR), html=True), name="frontend")

# Configure CORS so the frontend can easily communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In a production environment, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory dictionary to track background job status
# Format: { "project_id": {"status": "processing" | "completed" | "failed", "zip_path": "...", "error": "..."} }
job_status = {}

class DocsRequest(BaseModel):
    repo_url: str

def process_repository_task(repo_url: str, project_id: str):
    """
    Background task: runs the serve_pipeline (build only, no serve step)
    and stores the resulting site_dir and zip_path in job_status.
    """
    try:
        job_status[project_id] = {"status": "processing"}
        
        # Use serve_pipeline which generates all the rich content
        # It returns site_dir via the pipeline, we need to extract it
        site_dir, zip_path = _run_serve_pipeline(repo_url, build_only=True)
        
        job_status[project_id] = {
            "status": "completed",
            "zip_path": str(zip_path) if zip_path else None,
            "site_dir": str(site_dir) if site_dir else None
        }
    except Exception as e:
        error_msg = str(e)
        print(f"Background task failed for {project_id}: {error_msg}")
        traceback.print_exc()
        job_status[project_id] = {
            "status": "failed",
            "error": error_msg
        }

@app.post("/api/generate-docs")
async def generate_docs(request: DocsRequest, background_tasks: BackgroundTasks):
    """
    Accepts a GitHub repository URL, assigns a project_id, and triggers 
    the documentation generation pipeline safely in the background.
    """
    if not request.repo_url:
        raise HTTPException(status_code=400, detail="repo_url is required")
        
    project_id = f"project_{uuid.uuid4().hex[:8]}"
    
    # Fire off the background task
    background_tasks.add_task(process_repository_task, request.repo_url, project_id)
    
    return {
        "message": "Documentation generation started in the background",
        "project_id": project_id
    }

@app.get("/api/status/{project_id}")
async def get_status(project_id: str):
    """
    Checks the status of the pipeline using the project_id.
    """
    if project_id not in job_status:
        raise HTTPException(status_code=404, detail="Project ID not found")
        
    return job_status[project_id]

@app.get("/api/download/{project_id}")
async def download_docs(project_id: str):
    """
    Serves the generated docs.zip file if the pipeline completed successfully.
    """
    if project_id not in job_status:
        raise HTTPException(status_code=404, detail="Project ID not found")
        
    status_info = job_status[project_id]
    
    if status_info["status"] == "processing":
        raise HTTPException(status_code=400, detail="Documentation is still generating")
    elif status_info["status"] == "failed":
        raise HTTPException(status_code=400, detail=f"Documentation generation failed: {status_info.get('error')}")
        
    zip_path = status_info.get("zip_path")
    
    if not zip_path or not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="Zip file not found on server")
        
    return FileResponse(
        zip_path, 
        media_type="application/zip", 
        filename=f"{project_id}_docs.zip"
    )

@app.get("/api/preview/{project_id}")
async def preview_docs(project_id: str):
    """
    Mounts the static HTML site directory on the fly and redirects the user to it.
    """
    if project_id not in job_status:
        raise HTTPException(status_code=404, detail="Project ID not found")
        
    status_info = job_status[project_id]
    
    if status_info["status"] != "completed":
        raise HTTPException(status_code=400, detail="Documentation is not ready for preview")
        
    # The zip_path is something like e:\gen_ai_pro\ai_doc_generator\temp\docs.zip
    # The static files are located at e:\gen_ai_pro\ai_doc_generator\temp\site
    # We strip down to the base temp dir using the zip_path context
    zip_path = status_info.get("zip_path")
    site_dir = status_info.get("site_dir")
    
    # Fallback: compute site_dir from zip_path if not stored
    if not site_dir and zip_path:
        site_dir = os.path.join(os.path.dirname(str(zip_path)), "site")
    
    if not site_dir:
        raise HTTPException(status_code=404, detail="Preview files not found on server")
        
    if not os.path.exists(site_dir):
        raise HTTPException(status_code=404, detail=f"Generated HTML site not found at: {site_dir}")
    
    # Dynamically mount this specific project's site directory so it can serve assets (CSS, JS) safely
    mount_path = f"/preview/{project_id}"
    
    # Clean up old mounts if they exist to prevent crashing
    for route in app.routes:
        if hasattr(route, "path") and route.path == mount_path:
            break
    else:
        # If the route does not exist yet restrictively mount it mapping directly to the specific project's 'site' folder
        app.mount(mount_path, StaticFiles(directory=site_dir, html=True), name=f"preview_{project_id}")
    
    # Redirect the user's browser to the newly mounted path
    return RedirectResponse(url=mount_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
