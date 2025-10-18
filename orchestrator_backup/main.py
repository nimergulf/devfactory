import os, tempfile, shutil
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import secretmanager
from github import Github, InputGitTreeElement
from orchestrator.generator import synthesize, materialize_repo_root

PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION", "me-central1")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")
TEMPLATE_DIR = os.path.join(os.getcwd(), "template")

app = FastAPI(title="DevFactory Orchestrator")

class GenRequest(BaseModel):
    service_name: str
    requirement: str

def _get_github_pat():
    # Prefer env var (if Cloud Run mounted the secret as env)
    env_pat = os.getenv("GITHUB_PAT")
    if env_pat:
        return env_pat.strip()
    # Otherwise, read from Secret Manager secret named 'GITHUB_PAT'
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/GITHUB_PAT/versions/latest"
    resp = client.access_secret_version(name=name)
    return resp.payload.data.decode("utf-8").strip()

def _walk_and_stage(path: str):
    items = []
    for root, _, files in os.walk(path):
        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, path)
            with open(full, "rb") as fp:
                items.append((rel, fp.read()))
    return items

@app.post("/generate")
def generate(req: GenRequest):
    try:
        print(f"🎯 Starting generation for: {req.service_name}")
        
        # 1) Generate ADR, OpenAPI, and code via Vertex AI (inside synthesize)
        print("📝 Generating content...")
        synthesized = synthesize(req.service_name, REGION, req.requirement)
        print(f"✅ Content generated: {list(synthesized.keys())}")

        # 2) Write into a temp dir (repo root layout)
        tmp = tempfile.mkdtemp(prefix="dfgen_")
        print(f"📂 Using temp dir: {tmp}")
        
        try:
            print("📄 Materializing repository...")
            materialize_repo_root(tmp, synthesized, TEMPLATE_DIR)
            print("✅ Repository materialized")

            # 3) Commit to GitHub root (overwrite existing files)
            print("🔑 Getting GitHub PAT...")
            pat = _get_github_pat()
            gh = Github(pat)
            repo = gh.get_repo(f"{GITHUB_OWNER}/{GITHUB_REPO}")
            print("✅ GitHub connection established")

            # Build a new tree with all files from tmp (upsert)
            print("🌳 Building Git tree...")
            base_ref = repo.get_git_ref(f"heads/{GITHUB_BRANCH}")
            base_commit = repo.get_git_commit(base_ref.object.sha)

            tree_elements = []
            for rel, content in _walk_and_stage(tmp):
                print(f"📁 Adding file: {rel}")
                try:
                    decoded_content = content.decode("utf-8", errors="replace")
                    tree_elements.append(
                        InputGitTreeElement(
                            path=rel, mode="100644", type="blob",
                            content=decoded_content
                        )
                    )
                except Exception as decode_error:
                    print(f"❌ Failed to decode {rel}: {decode_error}")
                    raise decode_error

            print("🌳 Creating Git tree...")
            new_tree = repo.create_git_tree(tree_elements, base_commit.tree)
            
            print("💾 Creating commit...")
commit_msg = f"[DevFactory] Generate service: {req.service_name}"
            new_commit = repo.create_git_commit(commit_msg, new_tree, [base_commit])
            base_ref.edit(new_commit.sha)
            print("✅ Commit pushed to GitHub")

        finally:
            shutil.rmtree(tmp, ignore_errors=True)
            print("🧹 Cleaned up temp directory")

        return {"ok": True, "message": "Artifacts generated and committed. Cloud Build will deploy."}
        
    except Exception as e:
        print(f"❌ Generation error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
